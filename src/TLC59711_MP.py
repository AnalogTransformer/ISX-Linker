import struct
from machine import Pin, SPI
import time

# Constants
_CHIP_BUFFER_BYTE_COUNT = 28
COLORS_PER_PIXEL = 3
LEDS_PER_CHIP = 4
CHANNEL_PER_CHIP = COLORS_PER_PIXEL * LEDS_PER_CHIP
_BUFFER_BYTES_PER_COLOR = 2

_BC_CHIP_BUFFER_BIT_OFFSET = 0
_BC_BIT_COUNT = 3 * 7
_BC_FIELDS = {
    "BCR": {"offset": 0, "length": 7, "mask": 0b01111111},
    "BCG": {"offset": 7, "length": 7, "mask": 0b01111111},
    "BCB": {"offset": 14, "length": 7, "mask": 0b01111111},
}

_FC_CHIP_BUFFER_BIT_OFFSET = _BC_BIT_COUNT
_FC_BIT_COUNT = 5
_FC_FIELDS = {
    "BLANK": {"offset": 0, "length": 1, "mask": 0b1},
    "DSPRPT": {"offset": 1, "length": 1, "mask": 0b1},
    "TMGRST": {"offset": 2, "length": 1, "mask": 0b1},
    "EXTGCK": {"offset": 3, "length": 1, "mask": 0b1},
    "OUTTMG": {"offset": 4, "length": 1, "mask": 0b1},
}

_WC_CHIP_BUFFER_BIT_OFFSET = _BC_BIT_COUNT + _FC_BIT_COUNT
_WC_BIT_COUNT = 6
_WC_FIELDS = {
    "WRITE_COMMAND": {"offset": 0, "length": 6, "mask": 0b111111},
}
WRITE_COMMAND = 0b100101

_CHIP_BUFFER_HEADER_BIT_COUNT = _WC_BIT_COUNT + _FC_BIT_COUNT + _BC_BIT_COUNT
_CHIP_BUFFER_HEADER_BYTE_COUNT = _CHIP_BUFFER_HEADER_BIT_COUNT // 8


class TLC59711:
    """TLC5971 & TLC59711 16-bit 12 channel LED PWM driver."""

    def __init__(self, pixel_count=4, spi_id=0, sck_pin=2, mosi_pin=3):
        """Initialize the TLC59711 driver.
        
        Args:
            pixel_count: Number of pixels (default 32)
            spi_id: SPI bus ID (0 or 1 for RP2040)
            sck_pin: SCK pin number
            mosi_pin: MOSI pin number
        """
        # Initialize SPI - TLC59711 only needs SCK and MOSI
        self._spi = SPI(spi_id, 
                       baudrate=1000000,
                       polarity=0,
                       phase=0,
                       sck=Pin(sck_pin),
                       mosi=Pin(mosi_pin))
        
        self.pixel_count = pixel_count
        self.channel_count = self.pixel_count * COLORS_PER_PIXEL
        self.chip_count = self.pixel_count // LEDS_PER_CHIP
        self._buffer = bytearray(_CHIP_BUFFER_BYTE_COUNT * self.chip_count)

        self.bcr = 127
        self.bcg = 127
        self.bcb = 127

        self.outtmg = True
        self.extgck = False
        self.tmgrst = True
        self.dsprpt = True
        self.blank = False

        self._init_buffer()
        self._buffer_LED_index_lookuptable = []
        self._init_LED_lookuptable()

    def _init_buffer(self):
        for chip_index in range(self.chip_count):
            self.chip_set_BCData(chip_index, bcr=self.bcr, bcg=self.bcg, bcb=self.bcb)
            self._chip_set_FunctionControl(chip_index)
            self._chip_set_WriteCommand(chip_index)

    def set_chipheader_bits_in_buffer(self, chip_index=0, part_bit_offset=0, 
                                     field=None, value=0):
        """Set chip header bits in buffer."""
        if field is None:
            field = {"mask": 0, "length": 0, "offset": 0}
        offset = part_bit_offset + field["offset"]
        value &= field["mask"]
        value <<= offset
        header_start = chip_index * _CHIP_BUFFER_BYTE_COUNT
        header = struct.unpack_from(">I", self._buffer, header_start)[0]
        mask = field["mask"] << offset
        header &= ~mask
        header |= value
        struct.pack_into(">I", self._buffer, header_start, header)

    def chip_set_BCData(self, chip_index, bcr=127, bcg=127, bcb=127):
        """Set BC-Data."""
        self.set_chipheader_bits_in_buffer(
            chip_index=chip_index,
            part_bit_offset=_BC_CHIP_BUFFER_BIT_OFFSET,
            field=_BC_FIELDS["BCR"],
            value=bcr,
        )
        self.set_chipheader_bits_in_buffer(
            chip_index=chip_index,
            part_bit_offset=_BC_CHIP_BUFFER_BIT_OFFSET,
            field=_BC_FIELDS["BCG"],
            value=bcg,
        )
        self.set_chipheader_bits_in_buffer(
            chip_index=chip_index,
            part_bit_offset=_BC_CHIP_BUFFER_BIT_OFFSET,
            field=_BC_FIELDS["BCB"],
            value=bcb,
        )

    def update_BCData(self):
        """Update BC-Data for all Chips in Buffer."""
        for chip_index in range(self.chip_count):
            self.chip_set_BCData(chip_index, bcr=self.bcr, bcg=self.bcg, bcb=self.bcb)

    def set_brightness(self, bcr, bcg, bcb):
        """Set global brightness control for red, green, and blue."""
        self.bcr = bcr & _BC_FIELDS["BCR"]["mask"]
        self.bcg = bcg & _BC_FIELDS["BCG"]["mask"]
        self.bcb = bcb & _BC_FIELDS["BCB"]["mask"]
        self.update_BCData()
        self.show()

    def _chip_set_FunctionControl(self, chip_index):
        """Set Function Control Bits in Buffer."""
        self.set_chipheader_bits_in_buffer(
            chip_index=chip_index,
            part_bit_offset=_FC_CHIP_BUFFER_BIT_OFFSET,
            field=_FC_FIELDS["OUTTMG"],
            value=1 if self.outtmg else 0,
        )
        self.set_chipheader_bits_in_buffer(
            chip_index=chip_index,
            part_bit_offset=_FC_CHIP_BUFFER_BIT_OFFSET,
            field=_FC_FIELDS["EXTGCK"],
            value=1 if self.extgck else 0,
        )
        self.set_chipheader_bits_in_buffer(
            chip_index=chip_index,
            part_bit_offset=_FC_CHIP_BUFFER_BIT_OFFSET,
            field=_FC_FIELDS["TMGRST"],
            value=1 if self.tmgrst else 0,
        )
        self.set_chipheader_bits_in_buffer(
            chip_index=chip_index,
            part_bit_offset=_FC_CHIP_BUFFER_BIT_OFFSET,
            field=_FC_FIELDS["DSPRPT"],
            value=1 if self.dsprpt else 0,
        )
        self.set_chipheader_bits_in_buffer(
            chip_index=chip_index,
            part_bit_offset=_FC_CHIP_BUFFER_BIT_OFFSET,
            field=_FC_FIELDS["BLANK"],
            value=1 if self.blank else 0,
        )

    def update_fc(self):
        """Update Function Control Bits for all Chips in Buffer."""
        for chip_index in range(self.chip_count):
            self._chip_set_FunctionControl(chip_index)

    def _chip_set_WriteCommand(self, chip_index):
        """Set WRITE_COMMAND."""
        self.set_chipheader_bits_in_buffer(
            chip_index=chip_index,
            part_bit_offset=_WC_CHIP_BUFFER_BIT_OFFSET,
            field=_WC_FIELDS["WRITE_COMMAND"],
            value=WRITE_COMMAND,
        )

    def _init_LED_lookuptable(self):
        for channel_index in range(self.channel_count):
            buffer_index = (_CHIP_BUFFER_BYTE_COUNT // _BUFFER_BYTES_PER_COLOR) * (
                channel_index // CHANNEL_PER_CHIP
            ) + channel_index % CHANNEL_PER_CHIP
            buffer_index *= _BUFFER_BYTES_PER_COLOR
            buffer_index += _CHIP_BUFFER_HEADER_BYTE_COUNT
            self._buffer_LED_index_lookuptable.append(buffer_index)

    def _write(self):
        self._spi.write(self._buffer)

    def show(self):
        """Write out the current LED PWM state to the chip."""
        self._write()

    def set_all(self, brightness):
        """Set the normalized R, G, B values for all pixels."""
        for i in range(self.channel_count):
            self.set_channel(i, brightness)

    def set_all_black(self):
        """Turn off all pixels."""
        for i in range(self.channel_count):
            self.set_channel(i, 0)

    def set_channel(self, channel_index, value):
        """Set a single channel's value (0-100%)."""
        value = int(value * 655.35)
        if not (0 <= channel_index < self.channel_count):
            raise IndexError(f"channel_index {channel_index} out of range (0..{self.channel_count})")
        if not 0 <= value <= 65535:
            raise ValueError(f"value {value} not in range: 0..65535")
        struct.pack_into(">H", self._buffer, 
                        self._buffer_LED_index_lookuptable[(self.channel_count-1)-channel_index], 
                        value)

    def __setitem__(self, channel_index, value):
        self.set_channel(channel_index, value)

    def __getitem__(self, channel_index):
        """Get the current PWM value of a specific channel."""
        if not (0 <= channel_index < self.channel_count):
            raise IndexError(f"channel_index {channel_index} out of range (0..{self.channel_count-1})")

        buffer_index = self._buffer_LED_index_lookuptable[(self.channel_count - 1) - channel_index]
        value = struct.unpack_from(">H", self._buffer, buffer_index)[0]
        
        # Return as a normalized percentage (0-100%)
        return round(value / 655.35)

    def deinit(self):
        """Clean up SPI resources."""
        self._spi.deinit()


def cycle_through_leds(tlc, brightness, cycle_time):
    """Cycle through all LEDs with a given brightness and cycle time."""
    try:
        while True:
            # Cycle through all LEDs
            for led in range(tlc.channel_count):
                # Turn off all LEDs
                tlc.set_all_black()
                # Turn on current LED
                tlc[led] = brightness
                # Update the LED controller
                tlc.show()
                print(f"LED {led} set to brightness {brightness}")
                time.sleep(cycle_time)
    except KeyboardInterrupt:
        # Gracefully exit the loop on user interrupt
        # Turn off all LEDs
        tlc.set_all_black()
        tlc.show()
        tlc.deinit()
        print("LED cycling stopped.")


def flash_all(tlc, brightness, cycle_time):
    """Flash all LEDs on and off."""
    try:
        while True:
            # Turn on all LEDs
            tlc.set_all(brightness)
            tlc.show()
            time.sleep(cycle_time)
            # Turn off all LEDs
            tlc.set_all_black()
            tlc.show()
            time.sleep(cycle_time)
    
    except KeyboardInterrupt:
        # Gracefully exit the loop on user interrupt
        # Turn off all LEDs
        tlc.set_all_black()
        tlc.show()
        tlc.deinit()
        print("Flash All stopped.")




if __name__ == "__main__":
    
    brightness = 100
    flash_time = 1
    cycle_time = 1
    
    # Initialize TLC59711 with default SPI pins
    # For RP2040: SPI0 uses GP18(SCK), GP19(MOSI)
    # You can change these pins as needed
    tlc = TLC59711(pixel_count=4, spi_id=0, sck_pin=2, mosi_pin=3)
    print("Initialization complete. Sending test data...")
    
    # Uncomment one of these to test:
    # flash_all(tlc, brightness, flash_time)
    cycle_through_leds(tlc, brightness, cycle_time)
    
    print("Switch Off FET")
