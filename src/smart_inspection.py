from actuators import BasicActuators, CrazyflieActuator
from sensors import PIRMotionDetector, MultirangerSensor
from slm import SLMConfig, InteractivityHandler

from typing import Tuple
from time import sleep
from pathlib import Path

import logging

import threading

import csv


class SmartInspection():

    """
    
    Class to present a smart application for monitoring and inspection.
    
    """

    def __init__(self) -> None:

        """
        
        Smart Inspection constructor

        It initiates sensors and actuators
        
        """

        self.basic_actuators = BasicActuators()
        self.motion_detector = PIRMotionDetector()
        self.crazyflie       = CrazyflieActuator()
        

    def initial_config(self, model: str) -> None:

        """
        Function to initialize motion detector, actuators and slm


        :param model(str): name of the model to load with ollama library

        """

        self.basic_actuators.initial_config()
        self.motion_detector.initial_config()
        self.crazyflie.initial_config()
        self.slm = SLMConfig(model = model)
        self.model = model

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)

        self.multiranger = None
        self.locker = threading.Lock()
        self.stop_mult_thread = False
        self.mult_rng_data = list()
        self.final_inpection_result = False

        self.messages = [
                {
                    "role": "system",
                    "content": InteractivityHandler.SYSTEM_MESSAGE
                }
            ]


    def __get_all_data(self) -> Tuple[bool, Tuple[bool, bool, bool]]:

        """
        
        Function to get data from motion sensor and led status

        Returns:
            Tuple[bool, Tuple[bool, bool, bool]]
        
        """


        return self.motion_detector.get_data(), self.basic_actuators.led_status()


    def get_user_message(self, user_input: str) -> str:

        """
        
        Returns movement sensor data and red, yellow, green leds status.
        
        """


        try:
            movement, leds_status = self.__get_all_data()
            led_red_sts, led_ylw_sts, led_grn_sts = leds_status

        except Exception as ex: 
            self.logger.exception(f"Assistant error: unable to get fisic infos. \
                                   Please, try again. \n{ex}")
            
            return user_input

        else: 
            user_msg = InteractivityHandler.smart_inspection_prompt(movement,
                                                                    led_red_sts,
                                                                    led_ylw_sts,
                                                                    led_grn_sts,
                                                                    user_input)
        return user_msg


    def interactive_mode(self)-> None:

        """
        
        Initialize interactive mode with SLM.

        """
        
        InteractivityHandler.instructions_for_user(self.model)
        self.slm.preload_model()

        while True:

            user_input = input("You: ").strip()
            
            if not user_input:
                continue
                
            msg = user_input.lower()
            if msg in ['exit', 'quit', 'q']:
                print("\nExiting interactive mode. Goodbye!")
                break

            elif msg == 'status': 
                motion, leds_status = self.__get_all_data()
                InteractivityHandler.display_status(motion, leds_status)
                continue
            
            if any(word in msg for word in ['crazyflie', 'drone', 'fly']):
                self.slm.tools.append(InteractivityHandler.CRAZYFLIE_INSPECTION_TOOL)
            else: self.slm.tools = list()
            
            user_msg = self.get_user_message(user_input)
            
            self.messages.append({
                "role": "user",
                "content": user_msg
            })
            
            # Get SLM response using chat API
            print("Assistant: [Thinking...]")
            response = self.slm.inference(self.messages)

            if response.message.tool_calls:

                tool = response.message.tool_calls[0].function.name

                if tool == "__crazyflie_inspection":
                    print("Assistant: Initiating drone inspection...")
                    try: self.__crazyflie_inspection()
                    except Exception as ex:
                        self.logger.error(f"Drone inspection error: {ex}")
                    finally: 
                        self.crazyflie.disconnect()
                        continue
                    
            # Parse response
            assistant_content = response['message']['content']
            message, (red, yellow, green, motion) = InteractivityHandler.\
                                                    interactive_response(assistant_content)
            
            # Add assistant's response to conversation history
            self.messages.append({
                "role": "assistant",
                "content": assistant_content
            })
            
            # Display assistant's message
            print(f"Assistant: {message}")
            
            # Control LEDs based on response
            self.basic_actuators.control_leds(red = red, yellow = yellow, green = green)
            if motion: 
                drone_inspection = input("Motion detected: Start drone inspection?(Y/N): ").\
                strip()
                if drone_inspection.upper() == 'Y': 
                    
                    try: self.__crazyflie_inspection()
                    except Exception as ex: 
                       self.logger.error(f"Drone inspection gets an error: {ex}")
                    finally: self.crazyflie.disconnect()

            
            # Keep only system message + recent conversation (8 user/assistant messages)
            if len(self.messages) > 9:
                self.messages = [self.messages[0]] + self.messages[-8:]


    def __crazyflie_inspection(self) -> None:


        self.mult_rng_thread = threading.Thread(target = self.__multiranger_get_data)

        self.logger.info("Connecting with drone")
        self.crazyflie.connect()
        
        #Fazer tratamento de exceção para esse tipo de coisa
        self.multiranger = MultirangerSensor(sync_crazyflie = self.crazyflie.sync_crazyflie)
        self.multiranger.initial_config()

        mc = self.crazyflie.motion_commander

        mc.take_off()
        self.logger.info("Take off")
        sleep(1.0)

        self.mult_rng_thread.start()

        self.logger.info("Starting capture data from multiranger deck")
        self.logger.info("Rotating 360° counterclockwise!")
        mc.turn_left(360)

        sleep(1.0)

        self.logger.info("Rotating 360° clockwise!")
        mc.turn_right(360)

        with self.locker: self.stop_mult_thread = True
        self.multiranger.close()
        self.mult_rng_thread.join()

        sleep(1.0)

        self.logger.info("Landing the drone")
        mc.land()

        self.crazyflie.disconnect()
        self.write_csv_file()


    def __multiranger_get_data(self) -> None:
        

        while not self.stop_mult_thread:
            front, back, right, left, up = self.multiranger.get_data()
            ranges = (front, back, right, left, up)

            if not any(value is None for value in ranges):
                self.mult_rng_data.append(ranges)

            sleep(0.3)
        
        self.logger.info("Finish get data")
        with self.locker: self.stop_mult_thread = False


    def write_csv_file(self) -> None:

        path = Path(__file__).parent/"inspection_data.csv"
        header = ["Front", "Back", "Right", "Left", "Up"]

        if len(self.mult_rng_data) > 5:

            self.logger.info("Writing data in csv file")
            with open(str(path), "w") as file:
                writer = csv.writer(file)
                writer.writerow(header)
                for i in self.mult_rng_data:
                    writer.writerow(i)
                    



def main() -> None:


    smart_inspection = SmartInspection()
    smart_inspection.initial_config(model = "llama3.2:3b")
    try: smart_inspection.interactive_mode()
    except KeyboardInterrupt:...
    except Exception as ex: print(f"Interactive mode gets an error: {ex}")


if __name__ == "__main__":
    main()