import ollama


class SLMConfig():
    

    def __init__(self, model: str) -> None:

        """
        SLM Config constructor

        :param model(str): name of the model to load with ollama library

        """

        self.available_models = [model.model for model in ollama.list().models]
        self.model = model
        self.tools = list()


    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, value: str) -> None:
        if value in self.available_models:
            self._model = value
        else: raise ValueError(f"{value} model not available")

    def inference(self, messages: list):

        """
        
        Send chat request to Ollama using chat API.
        
        """

        response = ollama.chat(
            model=self.model,
            messages=messages,
            tools = self.tools
        )

        return response


    def preload_model(self):
        
        """
        
        Pre-load the model into memory to avoid loading delays.
        
        """

        print(f"Pre-loading model {self.model}...")
        try:
            ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": "hi"}]
            )
            print(f"Model {self.model} loaded successfully!\n")
        except Exception as e:
            print(f"Warning: Could not pre-load model: {e}")
            print("Model will load on first use.\n")


                
def main() -> None:

    slm = SLMConfig("llama3.2:3b")
    slm.preload_model()
    messages = list()
    try:
        while True:

            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'stop']: 
                print("\nExiting interactive mode. Goodbye!")
                break

            messages.append({
                "role": "user",
                "content": user_input
            })

            print("Assistant: [Thinking...]")
            response = slm.inference(messages)

            assistant_content = response['message']['content']
            print(assistant_content)
            messages.append({
                "role": "user",
                "content": assistant_content
            })

            if len(messages) > 9:  # system message + 8 user/assistant messages
                messages = [messages[0]] + messages[-8:]

    except KeyboardInterrupt:...
    except Exception as ex: print(f"SLM test gets an error: {ex}")


if __name__ == "__main__":
    main()




