from actuators import CrazyflieActuator
from sensors import MultirangerSensor

from pathlib import Path
import threading

import csv

from time import sleep


class CreateDataset():


    """
    
    Class to create a intern distance range dataset with a Multiranger Deck and a 
    Crazyflie drone. 

    The objective is to perform a predefined drone operation, obtaining the distance 
    captured by a Multiranger Deck, which is a deck with five lidars.

    
    """

    CSV_PATH = Path(__file__).parent/"dataset"
    HEADER = ["Front", "Back", "Right", "Left", "Up", "Status"]


    def __init__(self) -> None:

        """
        
        Create dataset constructor:

        Init crazyflie actuator, threading and sincronization parameters.
        
        """

        self.crazyflie = CrazyflieActuator()
        self.crazyflie.initial_config()


        self.thread_get_data = threading.Thread(target = self.get_data)
        self.lock = threading.Lock()
        self.data = list()
        self.finish = False
        self.cleaned = False


    def initial_config(self) -> None:

        """
        
        Connects crazyradio with the drone and prepares Multiranger Deck sensor
        for operation.
        
        """

        print("Connecting with drone")
        self.crazyflie.connect()

        self.multiranger = MultirangerSensor(sync_crazyflie = self.crazyflie.sync_crazyflie)
        self.multiranger.initial_config()


    def move_crazyflie(self)-> None:

        """
        
        Execute Crazyflie movement to monitor the entire room.
        
        """
        
        self.mc = self.crazyflie.motion_commander

        self.mc.take_off()        
        print("Take off")
        sleep(1.0)
        self.thread_get_data.start()

        print("Starting capture data from multiranger deck")
        print("Rotating 360° counterclockwise!")
        self.mc.turn_left(360)
        sleep(1.0)

        print("Rotating 360° clockwise!")
        self.mc.turn_right(360)
        with self.lock: self.finish = True
        sleep(1.0)


    def get_data(self) -> None:

        """
        
        Gets data from each of five lidars from Multiranger Deck and store it in a 
        list.
        
        """


        while not self.finish:
            front, back, right, left, up = self.multiranger.get_data()
            sample = [front, back, right, left, up]

            if not any(value is None for value in sample):
                status = "Nothing detected" if not any(distance <= 0.3 for distance in sample) else "Anomaly Detected"
                sample.append(status)
                self.data.append(sample)

                print(f"Front: {front} \nBack: {back} \nRight: {right} \nLeft: {left} \nUp: {up}")
            sleep(0.3)
        print("Finish get data")

    
    def create(self) -> None:

        """
        
        Call move_crazyflie function to initialize the data capture and then
        terminate the application.
        
        """

        try: self.move_crazyflie()
        except KeyboardInterrupt:...
        except Exception as ex: print(ex)
        finally: self.cleanup()


    def write_csv_file(self) -> None:

        if len(self.data) > 5:

            print("Writing data in csv file")
            with open(f"{CreateDataset.CSV_PATH}/multiranger_data.csv", "a") as file:
                writer = csv.writer(file)
                for i in self.data:
                    writer.writerow(i)


    def cleanup(self) -> None:

        """
        
        Cleanup the application
        
        """

        if not self.cleaned:
            self.mc.land()
            self.crazyflie.disconnect()
            self.multiranger.close()
            self.write_csv_file()
            self.cleaned = True

        else: print("Already cleaned")


if __name__ == "__main__":
        
    dataset = CreateDataset()
    dataset.initial_config()
    dataset.create()



