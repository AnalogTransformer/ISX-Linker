# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`rainbowio` - Provides the `colorwheel()` function
===========================================================
See `CircuitPython:rainbowio` in CircuitPython for more details.
Not supported by all boards.

* Author(s): Kattni Rembor, Carter Nelson
"""


def colorwheel(color_value):
    """
    A colorwheel with improved color spread. ``0`` is deep blue, ``127`` is green, 
    and ``255`` is red, providing clear visual distinction between min and max values.

    :param int color_value: 0-255 of color value to return
    :return: tuple of RGB values
    """
    color_value = int(color_value)
    if color_value < 0 or color_value > 255:
        r = 0
        g = 0
        b = 0
    elif color_value < 64:
        # Deep blue to cyan (0-63)
        r = 0
        g = int(color_value * 4)  # 0 to 252
        b = 255
    elif color_value < 128:
        # Cyan to green (64-127)
        color_value -= 64
        r = 0
        g = 255
        b = int(255 - color_value * 4)  # 255 to 3
    elif color_value < 192:
        # Green to yellow (128-191)
        color_value -= 128
        r = int(color_value * 4)  # 0 to 252
        g = 255
        b = 0
    else:
        # Yellow to red (192-255)
        color_value -= 192
        r = 255
        g = int(255 - color_value * 4)  # 255 to 3
        b = 0
    
    return r << 16 | g << 8 | b, [r << 16, g << 8, b]


def colorwheel_simple(color_value):
    """
    A simplified colorwheel that goes from blue (0) to red (255).
    Perfect for sliders where you want clear min/max distinction.

    :param int color_value: 0-255 of color value to return
    :return: tuple of RGB values
    """
    color_value = int(color_value)
    if color_value < 0:
        color_value = 0
    elif color_value > 255:
        color_value = 255
    
    if color_value < 128:
        # Blue to green (0-127)
        r = 0
        g = int(color_value * 2)
        b = int(255 - color_value * 2)
    else:
        # Green to red (128-255)
        color_value -= 128
        r = int(color_value * 2)
        g = int(255 - color_value * 2)
        b = 0
    
    return r << 16 | g << 8 | b, [r << 16, g << 8, b]


def custom_colorwheel(color_value, start_color, middle_color, end_color):
    """
    A customizable colorwheel that transitions through three colors.
    
    :param int color_value: 0-255 of color value to return
    :param tuple start_color: RGB tuple for value 0 (e.g., (255, 0, 0) for red)
    :param tuple middle_color: RGB tuple for value 127 (e.g., (0, 255, 0) for green)
    :param tuple end_color: RGB tuple for value 255 (e.g., (0, 0, 255) for blue)
    :return: tuple of RGB values
    """
    color_value = int(color_value)
    if color_value < 0:
        color_value = 0
    elif color_value > 255:
        color_value = 255
    
    # Extract RGB components from input colors
    start_r, start_g, start_b = start_color
    middle_r, middle_g, middle_b = middle_color
    end_r, end_g, end_b = end_color
    
    if color_value <= 127:
        # Interpolate from start to middle (0-127)
        ratio = color_value / 127.0
        r = int(start_r + (middle_r - start_r) * ratio)
        g = int(start_g + (middle_g - start_g) * ratio)
        b = int(start_b + (middle_b - start_b) * ratio)
    else:
        # Interpolate from middle to end (128-255)
        ratio = (color_value - 127) / 128.0
        r = int(middle_r + (end_r - middle_r) * ratio)
        g = int(middle_g + (end_g - middle_g) * ratio)
        b = int(middle_b + (end_b - middle_b) * ratio)
    
    # Clamp values to 0-255 range
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    return r << 16 | g << 8 | b, [r << 16, g << 8, b]


def two_color_gradient(color_value, start_color, end_color):
    """
    A simple two-color gradient.
    
    :param int color_value: 0-255 of color value to return
    :param tuple start_color: RGB tuple for value 0 (e.g., (255, 0, 0) for red)
    :param tuple end_color: RGB tuple for value 255 (e.g., (0, 0, 255) for blue)
    :return: tuple of RGB values
    """
    color_value = int(color_value)
    if color_value < 0:
        color_value = 0
    elif color_value > 255:
        color_value = 255
    
    # Extract RGB components
    start_r, start_g, start_b = start_color
    end_r, end_g, end_b = end_color
    
    # Linear interpolation
    ratio = color_value / 255.0
    r = int(start_r + (end_r - start_r) * ratio)
    g = int(start_g + (end_g - start_g) * ratio)
    b = int(start_b + (end_b - start_b) * ratio)
    
    # Clamp values to 0-255 range
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    return r << 16 | g << 8 | b, [r << 16, g << 8, b]


# Predefined color constants for easy use
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)