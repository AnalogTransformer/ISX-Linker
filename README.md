# ISX-Linker

MicroPython I2C controller for interactive LED lighting with physical button and slider inputs.

## Hardware Requirements

- Raspberry Pi Pico or RP2040-based board
- SparkFun Qwiic Button (I2C address: 0x6F)
- NeoSlider with NeoPixels (I2C address: 0x30)
- TLC59711 LED Driver
- I2C pull-up resistors (if not included on modules)

## Installation

**Critical:** Upload ALL files directly to the root directory of your Pico. The `main.py` must be at root level to auto-execute on boot.

```bash
# Copy all Python files to Pico root (not in a subfolder)
cp src/*.py /Volumes/CIRCUITPY/
```

## Hardware Enclosure

3D printable case components:

- [Base](CAD/3D_Models/Base.stl)
- [Mini Light Case](CAD/3D_Models/Mini_Light_Case.stl)

## Usage

The system auto-starts on power-up. Button cycles through 4 lighting states. Slider controls brightness/color gradient.

## License

MIT