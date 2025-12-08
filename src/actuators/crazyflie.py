import cflib.crtp as crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils.uri_helper import uri_from_env

from time import sleep

class CrazyflieActuator():


    def __init__(self) -> None:

        crtp.init_drivers()


    def initial_config(self, 
                       uri: str = "radio://0/80/2M/E7E7E7E7E7",
                       flying_height: float = 0.5) -> None:

        """
        
        Function to setup crazyflie tools

        :param uri(str): Crazyflie uri address to connect
        
        """

        self.uri = uri_from_env(default = uri)
        self.crazyflie = Crazyflie(rw_cache='.cache')
        self.sync_crazyflie = SyncCrazyflie(link_uri = self.uri, cf = self.crazyflie)
        self.motion_commander = MotionCommander(self.sync_crazyflie, 
                                                default_height = flying_height)
        self.connected = False

    def connect(self)-> None: 
        
        if not self.connected:
            self.sync_crazyflie.open_link()
            self.connected = True

    def disconnect(self)-> None:

        if self.connected:
            self.sync_crazyflie.close_link()
            self.connected = False

    
def main()-> None:
    
    crazyflie = CrazyflieActuator()
    crazyflie.initial_config()
    crazyflie.connect()

    mc = crazyflie.motion_commander
    mc.take_off()
    sleep(1.0)

    mc.turn_left(360)

    sleep(1.0)

    mc.land()

    crazyflie.disconnect()

if __name__ == "__main__":
    main()