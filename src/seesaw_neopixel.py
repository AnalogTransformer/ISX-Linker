# SPDX-FileCopyrightText: 2017 Dean Miller for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# pylint: disable=missing-docstring,invalid-name,too-many-public-methods

"""
`adafruit_seesaw.neopixel`
====================================================
"""
import struct

try:
    from micropython import const
except ImportError:

    def const(x):
        return x

_NEOPIXEL_BASE = const(0x0E)

_NEOPIXEL_STATUS = const(0x00)
_NEOPIXEL_PIN = const(0x01)
_NEOPIXEL_SPEED = const(0x02)
_NEOPIXEL_BUF_LENGTH = const(0x03)
_NEOPIXEL_BUF = const(0x04)
_NEOPIXEL_SHOW = const(0x05)

# Pixel color order constants
RGB = (0, 1, 2)
"""Red Green Blue"""
GRB = (1, 0, 2)
"""Green Red Blue"""
RGBW = (0, 1, 2, 3)
"""Red Green Blue White"""
GRBW = (1, 0, 2, 3)
"""Green Red Blue White"""


class SeeSaw_NeoPixel:
    """Control NeoPixels connected to a seesaw

    :param ~adafruit_seesaw.seesaw.Seesaw seesaw: The device
    :param int pin: The pin number on the device
    :param int n: The number of pixels
    :param int bpp: The number of bytes per pixel
    :param float brightness: The brightness, from 0.0 to 1.0
    :param bool auto_write: Automatically update the pixels when changed
    :param tuple pixel_order: The layout of the pixels.
        Use one of the order constants such as RGBW."""

    def __init__(
        self,
        seesaw,
        pin,
        n,
        *,
        bpp=3,
        brightness=1.0,
        auto_write=True,
        pixel_order=None
    ):
        # TODO: brightness not yet implemented.
        self._seesaw = seesaw
        self._pin = pin
        self._bpp = bpp
        self.auto_write = auto_write
        self._n = n
        self._brightness = min(max(brightness, 0.0), 1.0)
        self._pixel_order = GRBW if pixel_order is None else pixel_order

        cmd = bytearray([pin])
        self._seesaw.write(_NEOPIXEL_BASE, _NEOPIXEL_PIN, cmd)
        cmd = struct.pack(">H", n * self._bpp)
        self._seesaw.write(_NEOPIXEL_BASE, _NEOPIXEL_BUF_LENGTH, cmd)
        self._pre_brightness_color = [None] * n

    @property
    def brightness(self):
        """Overall brightness of the pixel"""
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        # pylint: disable=attribute-defined-outside-init
        self._brightness = min(max(brightness, 0.0), 1.0)

        # Suppress auto_write while updating brightness.
        current_auto_write = self.auto_write
        self.auto_write = False
        for i in range(self._n):
            if self._pre_brightness_color[i] is not None:
                self[i] = self._pre_brightness_color[i]
        if current_auto_write:
            self.show()
        self.auto_write = current_auto_write

    def deinit(self):
        pass

    def __len__(self):
        return self._n

    def __setitem__(self, key, color):
        """Set one pixel to a new value"""
        cmd = bytearray(2 + self._bpp)
        struct.pack_into(">H", cmd, 0, key * self._bpp)
        
        # Handle both integer color values and tuple/list color values
        if isinstance(color, int):
            # Integer color value (24-bit RGB or 32-bit RGBW)
            w = (color >> 24) & 0xFF
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
        elif hasattr(color, '__len__') and hasattr(color, '__getitem__'):
            # Tuple, list, or other sequence
            if self._bpp == 3:
                if len(color) >= 3:
                    r, g, b = color[0], color[1], color[2]
                    w = 0
                else:
                    raise ValueError("Color sequence must have at least 3 values for RGB")
            else:
                if len(color) >= 4:
                    r, g, b, w = color[0], color[1], color[2], color[3]
                elif len(color) >= 3:
                    r, g, b = color[0], color[1], color[2]
                    w = 0
                else:
                    raise ValueError("Color sequence must have at least 3 values")
        else:
            # Try to treat as integer if it's a numeric type
            try:
                color_int = int(color)
                w = (color_int >> 24) & 0xFF
                r = (color_int >> 16) & 0xFF
                g = (color_int >> 8) & 0xFF
                b = color_int & 0xFF
            except (ValueError, TypeError):
                raise ValueError("Color must be an integer or sequence of RGB(W) values")

        self._pre_brightness_color[key] = color

        # If all components are the same and we have a white pixel then use it
        # instead of the individual components.
        if self._bpp == 4 and r == g == b and w == 0:
            w = r
            r = 0
            g = 0
            b = 0

        if self.brightness < 0.99:
            r = int(r * self.brightness)
            g = int(g * self.brightness)
            b = int(b * self.brightness)
            if self._bpp == 4:
                w = int(w * self.brightness)

        # Store colors in correct slots
        r = int(r)
        g = int(g)
        b = int(b)
        cmd[2 + self._pixel_order[0]] = r
        cmd[2 + self._pixel_order[1]] = g
        cmd[2 + self._pixel_order[2]] = b
        if self._bpp == 4:
            cmd[2 + self._pixel_order[3]] = w

        self._seesaw.write(_NEOPIXEL_BASE, _NEOPIXEL_BUF, cmd)
        if self.auto_write:
            self.show()

    def __getitem__(self, key):
        pass

    def fill(self, color):
        """Set all pixels to the same value"""
        # Suppress auto_write while filling.
        current_auto_write = self.auto_write
        self.auto_write = False
        for i in range(self._n):
            self[i] = color
        if current_auto_write:
            self.show()
        self.auto_write = current_auto_write

    def show(self):
        """Update the pixels even if auto_write is False"""
        self._seesaw.write(_NEOPIXEL_BASE, _NEOPIXEL_SHOW)