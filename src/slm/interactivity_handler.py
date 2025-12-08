import json

from typing import Tuple


class InteractivityHandler():

    SYSTEM_MESSAGE = """You are an IoT assistant controlling an environmental monitoring 
                        a room with a motion sensor.

                        Respond with JSON only:
                        {"message": "your helpful response", "leds": {"red_led": bool, 
                         "yellow_led": bool, "green_led": bool}, "motion_detected" : bool}

                        RULES:
                        - Information queries: keep current LED states unchanged
                        - LED commands: update LEDs as requested
                        - Only ONE LED should be on at a time UNLESS user explicitly says 
                          "all"
                        - Be concise and conversational
                        - Questions about motion sensor data, answer ONLY with: 
                          MOTION DETECTED or MOTION NOT DETECTED and set motion_detected
                          with True.
                        - If the user EXPLICITLY requests a CRAZYFLIE 
                          inspection (examples: "start drone inspection", "fly the drone", 
                          "run crazyflie inspection"), then you MUST call the function 
                          __crazyflie_inspection instead of replying JSON. Without explicity
                          user request, DO NOT call the function!!!

                        For leds and sensors operations ALWAYS RESPOND with 
                        valid JSON containing both "message" and "leds" fields.
                        """

    CRAZYFLIE_INSPECTION_TOOL = {
            "type": "function",
            "function": {
                "name": "__crazyflie_inspection",
                "description": "Initiates a crazyflie drone inspection if user ask",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }

    @staticmethod
    def complete_prompt(temp_dht    : float, 
                        hum         : float, 
                        temp_bmp    : float, 
                        press       : float, 
                        button_state:  bool, 
                        led_red_sts :  bool, 
                        led_ylw_sts :  bool, 
                        led_grn_sts :   str,
                        user_input  :   str) -> str:


        """
        
        Create a compact prompt based on the smart inspection project
        for interactive user commands and queries.

        :param temp_dht(float): temperature data from DHT22 sensor
        :param hum(float): humidity data from DHT22 sensor
        :param temp_bmp(float): temperature data from BMP280 sensor
        :param press(float): pressure from BMP280 sensor
        :param button_state(bool): Button state -> True for pressed, False for otherwise
        :param led_red_sts(bool): Red LED status
        :param led_ylw_sts(bool): Yellow LED status
        :param led_grn_sts(bool): Green LED status
        :param user_input(str): message input from user interactive
        
        """

        return f"""STATUS: 
                    DHT22={temp_dht:.1f}°C/{hum:.1f}% BMP280={temp_bmp:.1f}°C/{press:.2f}hPa 
                    Button={'PRESSED' if button_state else 'OFF'} 
                    LEDs:
                        R={'ON' if led_red_sts else 'OFF'}/
                        Y={'ON' if led_ylw_sts else 'OFF'}/
                        G={'ON' if led_grn_sts else 'OFF'}
                    USER: {user_input} """

    @staticmethod
    def smart_inspection_prompt(motion_data: bool,
                                led_red_sts: bool,
                                led_ylw_sts: bool,
                                led_grn_sts: bool,
                                user_input: str) -> str:

        return f"""STATUS: 
                    Motion={'DETECTED' if motion_data else 'NOT DETECTED'} 
                    LEDs:
                        R={'ON' if led_red_sts else 'OFF'}/
                        Y={'ON' if led_ylw_sts else 'OFF'}/
                        G={'ON' if led_grn_sts else 'OFF'}
                    USER: {user_input} """


    @staticmethod
    def instructions_for_user(model: str) -> None:

        print("\n" + "="*60)
        print("Smart Inspection System - Interactive Mode")
        print(f"Using Model: {model} (Optimized)")
        print("="*60)
        print("\nCommands you can try:")
        print("  - Turn on the yellow LED")
        print("  - Turn on all LEDs")
        print("  - Turn off all LEDs")        
        print("  - Type 'status' to see system status")
        print("  - For drone inspection without sensor check, type: 'Drone'/'Crazyflie/Fly'")
        print("  - Type 'exit' or 'quit' to stop")
        print("="*60 + "\n")

    @staticmethod
    def interactive_response(response_text: dict) -> Tuple[str, Tuple[bool, bool, bool]]:

        """
        
        Parse the interactive SLM JSON response.

        :param response_text(dict): JSON format dict from chat bot response
        
        """


        try:
            # Clean the response
            response_text = response_text.strip()
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Extract message
            message = data.get('message', 'No response provided.')
            
            # Extract LED states
            leds = data.get('leds', {})
            red_led = leds.get('red_led', False)
            yellow_led = leds.get('yellow_led', False)
            green_led = leds.get('green_led', False)

            motion = data.get('motion_detected', None)
            
            return message, (red_led, yellow_led, green_led, motion)
        
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response was: {response_text}")
            return "Error: Could not parse SLM response.", (False, False, False)


    @staticmethod
    def display_status(motion_data: bool, 
                       leds_status: Tuple[bool, bool, bool]) -> None:


        led_red_sts, led_ylw_sts, led_grn_sts = leds_status

        print("\n" + "="*60)
        print("SYSTEM STATUS")
        print("="*60)
        print(f"Motion:        {'DETECTED' if motion_data else 'NOT DETECTED'}")
        print(f"\nLED Status:")
        print(f"  Red LED:    {'●' if led_red_sts else '○'} {'ON' if led_red_sts else 'OFF'}")
        print(f"  Yellow LED: {'●' if led_ylw_sts else '○'} {'ON' if led_ylw_sts else 'OFF'}")
        print(f"  Green LED:  {'●' if led_grn_sts else '○'} {'ON' if led_grn_sts else 'OFF'}")
        print("="*60)
