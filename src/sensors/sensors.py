from abc import ABC, abstractmethod
from typing import Tuple

import time

import board

import adafruit_bmp280
import adafruit_dht
from gpiozero import MotionSensor, Button

from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils.multiranger import Multiranger


class Sensor(ABC):

    """
    Abstract class to define the sensors behavior and methods
    """

    def __init__(self, name: str) -> None:

        """

        :param name(str): name of the sensor. Default is the class name.

        """

        self.configured = False
        self.name = name
        
    @abstractmethod
    def initial_config(self) -> None:
        
        """
        Setup specifics sensor settings. It calls protected function _setup
        that must be implemented in inherited classes.

        """
        if not self.configured: 
            try:
                self._setup()
            except Exception as ex: 
                print(f"Erro has occured while setting up sensor: {ex}")
                return
            else: self.configured = True

        else: print("Device already configured")

    @abstractmethod
    def _setup(self) -> None:
        raise NotImplementedError(f"Should be implemented setup method for class")
    
    @abstractmethod
    def get_data(self):

        if not self.configured: 
            raise BrokenPipeError(f"{self.name} sensor is not configured yet")
        


class BMP280(Sensor):
    

    def __init__(self, name = "BMP280") -> None:
        super().__init__(name)

    def initial_config(self) -> None:
        return super().initial_config()

    def _setup(self) -> None:

        i2c = board.I2C()
        self.bmp280_adafruit = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
        self.bmp280_adafruit.sea_level_pressure = 1013.25
        
    def get_data(self) -> Tuple[float, float, float]: 

        super().get_data()

        return self.bmp280_adafruit.temperature, \
               self.bmp280_adafruit.pressure,    \
               self.bmp280_adafruit.altitude
    

class PIRMotionDetector(Sensor):


    def __init__(self, 
                 name: str = "PIR HC-SR501", 
                 pin: int = 4, 
                 queue_len: int = 15) -> None:

        """
        Constructor for PIRMotionDetector class

        :param pin(int): GPIO pin number that motion sensor output is connected
        :param queue_len(int): The length of the queue used to store values read 
         from the sensor. This defaults to 1 which effectively disables the queue. 
         If your motion sensor is particularly “twitchy” you may wish to increase 
         this value. 

        Reference: 
        https://gpiozero.readthedocs.io/en/stable/api_input.html#gpiozero.InputDevice
        
        """

        super().__init__(name)

        self.queue_len = queue_len
        self.pin = pin

    def initial_config(self) -> None:
        return super().initial_config()

    def _setup(self) -> None:
        self.pir = MotionSensor(self.pin, queue_len = self.queue_len)

    def get_data(self, timeout: float = 5.0) -> bool:
        super().get_data()
        return self.pir.wait_for_motion(timeout = timeout)

        
class DHT22(Sensor):


    def __init__(self, name: str = "DHT22") -> None:

        super().__init__(name)

    def initial_config(self) -> None:
        return super().initial_config()
    
    def _setup(self):
        self.dht = adafruit_dht.DHT22(board.D16)

    def get_data(self) -> Tuple[float, float]:
        super().get_data()
        
        return self.dht.temperature, self.dht.humidity

class ButtonSensor(Sensor):


    def __init__(self, name: str = "Button", pin: int = 20) -> None:

        """
        Button sensor constructor

        :param pin(int): GPIO pin number that button is connected
        
        """
        super().__init__(name)

        self.pin = pin

    def initial_config(self) -> None:
        return super().initial_config()

    def _setup(self) -> None:

        self.__button = Button(self.pin)

    def get_data(self) -> bool:

        super().get_data()

        return self.__button.is_pressed


class MultirangerSensor(Sensor):

    def __init__(self, 
                 name: str = "Multiranger Deck", 
                 sync_crazyflie: SyncCrazyflie = None) -> None:

        super().__init__(name)

        self.__sync_crazyflie = sync_crazyflie

    def initial_config(self) -> None:

        return super().initial_config()

    def _setup(self) -> None:

        self.__multiranger_deck = Multiranger(self.__sync_crazyflie)
        self.__multiranger_deck.start()

    def get_data(self) -> None:

        super().get_data()

        return self.__multiranger_deck.front, self.__multiranger_deck.back,\
               self.__multiranger_deck.right, self.__multiranger_deck.left,\
               self.__multiranger_deck.up

    def close(self) -> None:

        self.__multiranger_deck.stop()


if __name__ == "__main__":
    bmp = BMP280() 
    bmp.initial_config()

    dht = DHT22()
    dht.initial_config()


    pir = PIRMotionDetector()
    pir.initial_config()

    button = ButtonSensor()
    button.initial_config()

    try:

        while True:

            print("Motion detected") if pir.get_data() else print("Any motion detected")
            print("Button pressed") if button.get_data() else print("Button is not pressed")
            temperature, pressure, altitude = bmp.get_data()

            print("\nTemperature: %0.3f C" % temperature)
            print("Pressure: %0.1f hPa" % pressure)
            print("Altitude = %0.2f meters" % altitude)
            time.sleep(1.0)

            temperature, humidity = dht.get_data()
            print(f"DHT temperature: {temperature}")
            print(f"DHT humidity: {humidity}")

    except KeyboardInterrupt:...
    except Exception as ex: print("Test sensors gets an error: {}" .format(ex))
