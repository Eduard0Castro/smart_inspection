from gpiozero import LED

from time import sleep


class BasicActuators():

    def __init__(self)-> None:

        self.leds = list()

        self.red_led = None
        self.yellow_led = None
        self.green_led = None

        self.configured = False 


    def initial_config(self, 
                       pin_red_led:    int = 13,
                       pin_yellow_led: int = 19,
                       pin_green_led:  int = 26) -> None:

        """
        
        Function to setup all the LEDs in the smart inspection project.

        Parameters
        ----------
        pin_leds : int
            GPIO pin numbers for each LED to set.
        
        """

        if not self.configured:
            self.red_led    = LED(pin_red_led)
            self.yellow_led = LED(pin_yellow_led)
            self.green_led  = LED(pin_green_led) 
            self.configured = True

        else: print("Initial config already defined")

    def led_status(self):

        self.red_led_sts = self.red_led.is_lit
        self.yellow_led_sts = self.yellow_led.is_lit
        self.green_led_sts = self.green_led.is_lit 
        return self.red_led_sts, self.yellow_led_sts, self.green_led_sts


    def control_leds(self, 
                     red: bool = False, 
                     green: bool = False, 
                     yellow: bool = False):

        """
        
        Function to control the the leds.

        Parameters
        ----------
        red, yellow, green : bool
            True to turn on, False to turn off
        
        """

        self.red_led.on() if red else self.red_led.off()
        self.yellow_led .on() if yellow else self.yellow_led .off()
        self.green_led.on() if green else self.green_led.off()


if __name__ == "__main__":

    basic = BasicActuators()
    basic.initial_config()

    basic.control_leds(True, True, True)
    print(basic.led_status())
    sleep(5)

    basic.control_leds(False, False, False)



