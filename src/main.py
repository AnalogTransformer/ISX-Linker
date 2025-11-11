from qwiic_button import QwiicButton
from neoslider import NeoSliderController as NeoSlider
import time
import sys

from TLC59711_MP import TLC59711

GREEN_BUTTON = 0x6F
RED_BUTTON = 0x6F
NEO_SLIDER_ADDR = 0x30

brightness = 255
standby_brightness = 0
debounce_time = 5  # in milliseconds

button_state = False  # Initialize button state

button_green = QwiicButton(GREEN_BUTTON)

# button_red = QwiicButton(RED_BUTTON)

button_green.clear_event_bits()
# button_red.clear_event_bits()

button_green.set_debounce_time(debounce_time)
# button_red.set_debounce_time(debounce_time)

button_green.LED_on(standby_brightness)  # Set initial LED brightness
# button_red.LED_on(standby_brightness)  # Set initial LED brightness

# Initialize counters outside the main loop
green_count = 0
red_count = 0

slider = NeoSlider()

# Track previous states to detect changes
prev_state = False
prev_brightness = -1  # Initialize to -1 to ensure first update

def check_button_status(button):
    """
    Check the status of a button.
    
    :param button: QwiicButton instance
    :return: True if button is pressed, False otherwise
    """
    if button.available():
        # print(f"{button.address} Button Pressed")
        button.clear_event_bits()
        return True
    return False

def button_toggle(button, count, brightness, standby_brightness, state, edge="rise"):
    """
    Toggle button LED based on press count and edge type.
    
    :param button: QwiicButton instance
    :param count: Current press count
    :param edge: "rise" or "fall" - determines when LED turns on/off
    :return: Updated count value
    """
    if check_button_status(button):
        count += 1
        count = count % 4
        # print(f"Button {button.address} count: {count}, edge: {edge}")

    if edge == "rise":
        if count == 1:  # First press - turn on
            button.LED_on(brightness)
            state = True
        elif count == 2:  # Second press - turn off
            button.LED_on(brightness)
            state = True
        else:  # Third press - turn off
            button.LED_on(standby_brightness)
            state = False
    elif edge == "fall":
        if count == 2:  # Second press - turn on
            button.LED_on(brightness)
            state = True
        elif count == 0:  # Fourth press (wraps to 0) - turn off
            button.LED_on(standby_brightness)
            state = False
    
    return count, state

def convert_to_255(value):
    """
    convert slider 0- 1023 value to 0-255 for led brightness
    """
    return max(0,int(value / 1023 * 100))

def update_leds(tlc, brightness, state):
    """
    Update all LED channels with the given brightness.
    """
    if state:
        # Set all channels to the specified brightness
        tlc[0] = int(brightness)  # Set brightness for green button
        tlc[1] = int(brightness)  # Set brightness for green button
        tlc[2] = int(brightness)  # Set brightness for green button
        tlc[3] = int(brightness)  # Set brightness for red button
        tlc[4] = int(brightness)  # Set brightness for red button
        tlc[6] = int(brightness)  # Set brightness for slider
        tlc[7] = int(brightness)  # Set brightness for slider
        tlc[9] = int(brightness)  # Set brightness for slider
        tlc[10] = int(brightness) # Set brightness for slider
    else:
        # Turn off all channels
        tlc[0] = 0
        tlc[1] = 0
        tlc[2] = 0
        tlc[3] = 0
        tlc[4] = 0
        tlc[6] = 0
        tlc[7] = 0
        tlc[9] = 0
        tlc[10] = 0
    
    tlc.show()

if __name__ == '__main__':
    tlc = TLC59711(pixel_count=4, spi_id=0, sck_pin=2, mosi_pin=3)
    tlc.set_brightness(100, 100, 127)
    
    # Initialize LEDs to off state
    update_leds(tlc, 0, False)
    
    try:
        while True:
            slider.update_pixels()
            current_slider_value = slider.get_value()
            on_brightness = convert_to_255(current_slider_value)

            # print(f"Slider Value: {current_slider_value}, Brightness: {on_brightness}")

            green_count, state = button_toggle(button_green, green_count, on_brightness, standby_brightness, button_state)
            
            # Check if state changed or brightness changed (when state is on)
            state_changed = (state != prev_state)
            brightness_changed = (state and on_brightness != prev_brightness)
            
            if state_changed or brightness_changed:
                # Only update LEDs when there's a change
                update_leds(tlc, on_brightness, state)
                
                # Update previous values
                prev_state = state
                prev_brightness = on_brightness
                
                # Debug output
                # print(f"Update sent - State: {state}, Brightness: {on_brightness}")

            time.sleep(0.01)  # Polling interval
            
    except (KeyboardInterrupt, SystemExit) as exErr:
        tlc.set_all_black()
        tlc.show()
        tlc.deinit()
        print("\nProgram Ended")
        sys.exit(0)