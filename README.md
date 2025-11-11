# ISX-Linker

MicroPython-based hardware controller for interactive LED lighting systems. Interfaces with I2C devices (buttons, sliders) and controls LED strips through the TLC59711 driver, creating a responsive lighting control system with physical inputs.

## Hardware Requirements

- **Microcontroller**: Raspberry Pi Pico or RP2040-based board running MicroPython
- **Input Devices**:
  - SparkFun Qwiic Button (I2C address: 0x6F)
  - NeoSlider with integrated NeoPixels (I2C address: 0x30)
- **LED Driver**: TLC59711 12-channel 16-bit PWM LED driver
- **Support Components**: I2C pull-up resistors (4.7kΩ typical, if not included on modules)

## Pin Connections

### I2C Bus (Qwiic/STEMMA QT Compatible)
- **SDA**: GPIO 4 (Pin 6) - Default I2C0 on Pico
- **SCL**: GPIO 5 (Pin 7) - Default I2C0 on Pico
- **3.3V**: Pin 36 (3V3 OUT)
- **GND**: Pin 38 or any GND pin

### SPI for TLC59711 LED Driver
- **SCK (Clock)**: GPIO 2 (Pin 4)
- **MOSI (Data)**: GPIO 3 (Pin 5)
- **3.3V**: Pin 36
- **GND**: Pin 38

### LED Output from TLC59711
- Channels R0-R3, G0-G3, B0-B3 support up to 12 LED channels
- Each channel provides 16-bit PWM control (65,536 brightness levels)
- Connect LED strips with appropriate current limiting resistors

## Installation

**Critical:** Upload ALL files directly to the root directory of your MicroPython device. The `main.py` must be at root level to auto-execute on boot.

```bash
# Copy all Python files to Pico root (not in a subfolder)
cp src/*.py /Volumes/RPI-RP2/

# Or use Thonny IDE: Open each file and Save As to the Pico
```

## Hardware Enclosure

3D printable case components:

- [Base](CAD/3D_Models/Base.stl)
- [Mini Light Case](CAD/3D_Models/Mini_Light_Case.stl)

## System Architecture

The project uses a layered architecture:
- **Hardware Abstraction**: `i2c_driver.py` → `mp_i2c.py` (MicroPython-specific implementation)
- **Device Drivers**: Individual drivers for each I2C device (button, slider, LED controllers)
- **Main Control Loop**: `main.py` orchestrates inputs and outputs

Key components:
- **Qwiic Button**: Debounced input with integrated LED feedback
- **NeoSlider**: Combines analog potentiometer (0-1023) with 4 addressable NeoPixels
- **TLC59711**: Drives external LED strips with 12 channels of 16-bit PWM
- **Seesaw**: I2C multiplexer for extended GPIO and ADC functionality

## Usage

The system auto-starts on power-up with `main.py` executing automatically.

**Button Operation**:
- Implements a 4-state toggle cycle (0→1→2→3→0)
- States 1-2: LED ON with different behaviors
- State 3-0: LED OFF (standby brightness)
- Configurable debounce time (default: 5ms)

**Slider Control**:
- Potentiometer reads 0-1023, scaled to 0-255 for LED brightness
- Controls both NeoPixel colors on the slider itself
- Adjusts brightness of external LEDs via TLC59711
- Supports color gradients and rainbow effects

**LED Control Modes**:
- Direct brightness control through slider position
- Color gradient transitions (two-color or three-color)
- Rainbow wheel effects via `rainbowio.py` utilities

## Testing & Debugging

Connect via serial terminal or Thonny to test components:

```python
# Scan for I2C devices
from mp_i2c import qwiic_i2c
i2c = qwiic_i2c()
print(i2c.scan())  # Should show [0x6F, 0x30] or similar

# Test button
from qwiic_button import QwiicButton
button = QwiicButton(0x6F)
print(button.is_connected())  # Should return True

# Test slider
from neoslider import NeoSliderController
slider = NeoSliderController()
print(slider.read())  # Returns 0-1023 based on position
```

## License

MIT