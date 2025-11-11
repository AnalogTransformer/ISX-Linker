# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
NeoSlider NeoPixel Rainbow Demo - Class Implementation
"""
from mp_i2c import qwiic_i2c
from rainbowio import custom_colorwheel, two_color_gradient
from seesaw import Seesaw
from analoginput import AnalogInput
import seesaw_neopixel
import time


class NeoSliderController:
    """
    A class to control NeoSlider potentiometer and NeoPixel colors.
    """
    
    def __init__(self, addr=0x30, potentiometer_pin=18, neopixel_pin=14, num_pixels=4, color1=(0, 0, 185), color2=(255, 255, 255)):
        """
        Initialize the NeoSlider controller.
        
        Args:
            addr: I2C address of the NeoSlider (default: 0x30)
            potentiometer_pin: Pin number for potentiometer (default: 18)
            neopixel_pin: Pin number for NeoPixels (default: 14)
            num_pixels: Number of NeoPixels (default: 4)
        """
        # NeoSlider Setup
        self.neoslider = Seesaw(addr=addr)
        self.potentiometer = AnalogInput(self.neoslider, potentiometer_pin)
        self.pixels = seesaw_neopixel.SeeSaw_NeoPixel(
            self.neoslider, neopixel_pin, num_pixels, 
            pixel_order=seesaw_neopixel.GRB
        )
        
        # Default colors - Green to White gradient
        self.color1 = color1
        self.color2 = color2
        self.color3 = None  # Optional third color for three-color gradients
        self.gradient_type = "two_color"
    
    def potentiometer_to_color(self, value):
        """Scale the potentiometer values (0-1023) to the colorwheel values (0-255)."""
        return value / 1023 * 255
    
    def set_colors(self, color1, color2=None, color3=None, gradient_type="two_color"):
        """
        Set the colors for the gradient.
        
        Args:
            color1: First color (RGB tuple or predefined color)
            color2: Second color (RGB tuple or predefined color)
            color3: Third color (RGB tuple or predefined color, optional)
            gradient_type: "two_color" or "three_color"
        """
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3
        self.gradient_type = gradient_type
    
    def get_potentiometer_value(self):
        """Get the raw potentiometer value (0-1023)."""
        return self.potentiometer.value
    
    def get_value(self):
        """
        Get the current potentiometer value.
        
        Returns:
            int: Raw potentiometer value (0-1023)
        """
        return self.potentiometer.value
    
    def get_color_output(self):
        """
        Get the current color output based on potentiometer position.
        
        Returns:
            tuple: (color_int, raw_potentiometer_value)
        """
        pot_value = self.potentiometer.value
        scaled_value = self.potentiometer_to_color(pot_value)
        
        if self.gradient_type == "three_color" and self.color3 is not None:
            color_output = custom_colorwheel(scaled_value, self.color1, self.color2, self.color3)
        else:
            color_output = two_color_gradient(scaled_value, self.color1, self.color2)
        
        color_int = color_output[0]  # Extract the integer color value
        return color_int, pot_value
    
    def set_pixel_color(self, pixel_index, color):
        """
        Set the color of a specific NeoPixel.
        
        Args:
            pixel_index: Index of the NeoPixel (0 to num_pixels-1)
            color: Color to set (RGB tuple)
        """
        if 0 <= pixel_index < len(self.pixels):
            self.pixels[pixel_index] = color
        else:
            raise IndexError("Pixel index out of range.")
    
    def update_pixels(self):
        """Update the NeoPixels with the current color based on potentiometer position."""
        color_int, _ = self.get_color_output()
        self.pixels.fill(color_int)

    
    def get_current_state(self):
        """
        Get the current state of the controller.
        
        Returns:
            dict: Contains potentiometer value, color output, and settings
        """
        color_int, pot_value = self.get_color_output()
        return {
            'potentiometer_value': pot_value,
            'color_int': color_int,
            'scaled_value': self.potentiometer_to_color(pot_value),
            'gradient_type': self.gradient_type,
            'colors': {
                'color1': self.color1,
                'color2': self.color2,
                'color3': self.color3
            }
        }


if __name__ == "__main__":
    # Testing the class
    print("Testing NeoSlider Controller...")
    
    # Initialize the controller with default settings
    controller = NeoSliderController()
    
    while True:
        value = controller.get_value()
        print(f"Potentiometer value: {value}")
        controller.update_pixels()  # Colors are just a nice bonus
        time.sleep(0.1)  # Sleep for a second before the next read