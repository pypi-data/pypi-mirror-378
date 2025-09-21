"""
Reading data from particulate matter sensors with a serial interface.
"""

import time
import logging
import asyncio
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
import serial_asyncio_fast

from .const import (
    ID_REPLY, ID_WAIT_HISTORY, CONTINUE_REQUEST, START_REQUEST,
    PACKET_ID_HISTORY, PACKET_ID_HISTORY_DATA, PACKET_ID_REALTIME,
    RECORD_LENGTH, CURRENT, BAUD_RATE, BYTE_ORDER, LSB, MSB,
    MULTIPLIER, TIMEOUT
)


# Owl CM160 settings
OWL_CM160 = {
    RECORD_LENGTH: 11,
    CURRENT: 8,
    BAUD_RATE: 250000,
    BYTE_ORDER: LSB,
    MULTIPLIER: 0.07,
    TIMEOUT: 30
}

SUPPORTED_SENSORS = {
    "CM160": OWL_CM160
}

DEVICE_STATES = {
    "Unknown": 0,
    "IdentifierReceived": 1,
    "TransmittingHistory": 2,
    "TransmittingRealtime": 3
}

CMVALS=[CURRENT]

LOGGER = logging.getLogger(__name__)


class CMDataCollector():
    """Controls the serial interface and reads data from the sensor."""

# pylint: disable=too-many-instance-attributes
    def __init__(self,
                 serialdevice,
                 configuration,
                 scan_interval=0):
        """Initialize the data collector based on the given parameters."""

        self.record_length = configuration[RECORD_LENGTH]
        self.byte_order = configuration[BYTE_ORDER]
        self.multiplier = configuration[MULTIPLIER]
        self.timeout = configuration[TIMEOUT]
        self.scan_interval = scan_interval
        self.listeners = []
        self.sensordata = {}
        self.config = configuration
        self._data = None
        self.last_poll = None
        self.device_state = DEVICE_STATES["Unknown"]
        self.device_found = False
        self.serialdevice = serialdevice
        self.reader = None
        self.writer = None
        self.baudrate = configuration[BAUD_RATE]
        self.connected = False
        self.update_task = None
        self._last_connect_attempt = 0
        self._connect_retry_interval = 5  # seconds

    async def disconnect(self):
        """Disconnect and cleanup resources."""
        if self.update_task is not None:
            try:
                self.update_task.cancel()
                await self.update_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                LOGGER.warning("Exception while cancelling update task: %s", e)
            finally:
                self.update_task = None

        if self.writer is not None:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                LOGGER.warning("Exception while closing writer: %s", e)
            finally:
                self.writer = None
                self.reader = None

        self.connected = False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self) -> bool:
        """Establish the serial connection asynchronously."""
        self.connected = False
        try:
            self.reader, self.writer = await serial_asyncio_fast.open_serial_connection(
                url=self.serialdevice,
                baudrate=self.baudrate,
                parity=PARITY_NONE,
                bytesize=EIGHTBITS,
                stopbits=STOPBITS_ONE,
                timeout=1,
                write_timeout=1,
                exclusive=False
            )
        except Exception as ex:
            LOGGER.warning("Failed to connect: %s", ex)
            self.connected = False
            return False
        
        self.connected = True
        
        # Stimulate the device
        await self.send_data(CONTINUE_REQUEST)

        if self.update_task is not None:
            try:
                self.update_task.cancel()
                self.update_task = None
            except Exception as e:
                LOGGER.warning("Exception while cancelling update Task: %s", e)

        if self.scan_interval > 0:
            self.update_task = asyncio.create_task(self.refresh())
        
        LOGGER.info("Connection to %s successful", self.serialdevice)
        return True

    async def refresh(self):
        """Asynchronous background refreshing task."""
        while True:
            try:
                await self.read_data()
                await asyncio.sleep(self.scan_interval)
            except asyncio.CancelledError:
                LOGGER.info("Refresh task cancelled")
                break
            except Exception as e:
                LOGGER.warning("Refresh loop exception: %s", e)
                self.connected = False
                await asyncio.sleep(self.scan_interval)

    async def send_data(self, data: bytes) -> None:
        LOGGER.debug("-> %s", ''.join(format(x, '02x') for x in data))
        try:
            self.writer.write(data)
            await self.writer.drain()
        except Exception as e:
            LOGGER.warning("Error while writing: %s", e)
            self.connected = False
    
    async def get_packet(self) -> bytearray:
        sbuf = bytearray()
        starttime = asyncio.get_event_loop().time()

        while len(sbuf) < self.record_length:
            elapsed = asyncio.get_event_loop().time() - starttime
            if elapsed > self.timeout:
                LOGGER.error("Timeout waiting for data")
                return bytearray()

            try:
                data_bytes = await self.reader.readexactly(1)
                if len(data_bytes) == 0:
                    LOGGER.warning("Timeout on data on serial")
                    return bytearray()
                sbuf += data_bytes
            except asyncio.IncompleteReadError:
                LOGGER.warning("Timeout on data on serial")
                return bytearray()

        return sbuf

    async def parse_packet(self, buffer: bytearray) -> dict | None:
        if len(buffer) != self.record_length:
            LOGGER.error("Wrong buffer length: %d", len(buffer))
            return

        LOGGER.debug("<- %s", ''.join(format(x, '02x') for x in buffer))
        try:
            str_buffer = buffer[1:10].decode("cp850", errors='replace')
        except (UnicodeDecodeError, IndexError) as e:
            LOGGER.error("Failed to decode buffer: %s", e)
            return None

        if ID_REPLY in str_buffer:
            LOGGER.info("Device found (%s)", str_buffer)
            self.device_found = True

        if self.device_found and ID_WAIT_HISTORY in str_buffer:
            await self.send_data(CONTINUE_REQUEST)

        if buffer[0] == PACKET_ID_HISTORY:
            if self.device_found:
                await self.send_data(START_REQUEST)
        elif buffer[0] == PACKET_ID_REALTIME:
            LOGGER.info("Realtime data received")
            self.device_state = DEVICE_STATES["TransmittingRealtime"]
            res = self.parse_buffer(buffer)
            return res
        elif buffer[0] == PACKET_ID_HISTORY_DATA:
            self.device_state = DEVICE_STATES["TransmittingHistory"]

        return None

    async def read_data(self) -> dict | None:
        """Read data from the serial interface asynchronously."""

        if not self.connected:
            current_time = time.time()
            if current_time - self._last_connect_attempt < self._connect_retry_interval:
                return None

            self._last_connect_attempt = current_time
            if not await self.connect():
                return None

        mytime = asyncio.get_event_loop().time()
        if (self.last_poll is not None) and \
           (mytime - self.last_poll) <= 15 and \
           self._data is not None:
            return self._data

        res = None
        finished = False

        while not finished:
            try:
                packet = await self.get_packet()
                if packet:
                    result = await self.parse_packet(packet)
                    if result is not None:
                        res = result
                        finished = True
            except Exception as ex:
                LOGGER.warning(ex)
                self.connected = False
                return None

        # consistency check
        if res[CURRENT] < 0.0 or res[CURRENT] > 100.0:
            LOGGER.warning("Inconsistent data: %s", res)
            return None
        
        self._data = res
        self.last_poll = asyncio.get_event_loop().time()
        return res

    def parse_buffer(self, sbuf) -> dict:
        """Parse the buffer and return the CM values."""
        res = {}
        for pmname in CMVALS:
            offset = self.config[pmname]
            if offset is not None:
                if self.byte_order == MSB:
                    res[pmname] = sbuf[offset] * \
                        256 + sbuf[offset + 1]
                else:
                    res[pmname] = sbuf[offset + 1] * \
                        256 + sbuf[offset]

                res[pmname] = round(res[pmname] * self.multiplier, 1)

        return res

    def supported_values(self) -> list:
        """Returns the list of supported values for the actual device"""
        res = []
        for pmname in CMVALS:
            offset = self.config[pmname]
            if offset is not None:
                res.append(pmname)
        return res
    
    def get_current(self) -> float | None:
        """ Returns latest realtime current transmitted by the device """
        
        if not self.connected:
            return None

        if self._data is None:
            return None
        
        if CURRENT in self._data:
            return self._data[CURRENT]
        
        return None
