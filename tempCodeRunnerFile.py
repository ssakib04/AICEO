import logging
import speech_recognition as sr
from duckduckgo_search import DDGS
from sympy import sympify
import cohere

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Initialize Cohere API
COHERE_API_KEY = 'uZnDNG0nkoKv8lPqjrQlSklJsPZU5LQNXh1m5x4q'  # Replace with your actual API key
cohere_client = cohere.Client(COHERE_API_KEY)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Voice authentication
def authenticate_voice():
    """
    Authenticate the user's voice by comparing it with a pre-recorded sample.
    """
    print("Please say your authentication phrase.")
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    
    try:
        # Convert audio to text
        command = recognizer.recognize_google(audio)
        logging.info(f"Recognized command: {command}")
        
        # Compare with stored authentication phrase
        if command.lower() == "start":
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error during voice authentication: {e}")
        return False

# Function to generate response using Cohere
def generate_response(prompt):
    try:
        # Use the chat API for the 'command-xlarge-nightly' model
        response = cohere_client.chat(
            model='command-xlarge-nightly',
            message=prompt,
            max_tokens=100,
            temperature=0.7
        )
        logging.info(f"Cohere API response: {response.text.strip()}")
        return response.text.strip()
    except cohere.errors.BadRequestError as e:
        logging.error(f"Bad request to Cohere API: {e}")
        return "Sorry, there was an issue generating a response. Please try again later."
    except Exception as e:
        logging.error(f"Unexpected error with Cohere API: {e}")
        return "An unexpected error occurred. Please try again later."

def process_command(command):
    """
    Process the voice command and execute the corresponding task.
    """
    command = command.lower()  # Convert command to lowercase for consistency
    
    if "calculate" in command:
        # Secure math evaluation
        try:
            expression = command.replace("calculate", "").strip()
            result = sympify(expression)
            return f"The result is {result}."
        except Exception as e:
            return f"Error calculating: {e}"
    
    elif "search" in command:
        # Real-time search using DuckDuckGo
        query = command.replace("search", "").strip()
        try:
            search_results = DDGS().text(query, max_results=3)
            if search_results:
                return "\n".join([f"{result['title']} - {result['href']}" for result in search_results])
            else:
                return "Sorry, no results found."
        except Exception as e:
            logging.error(f"Error with DuckDuckGo search: {e}")
            return "Sorry, I couldn't fetch search results."
    
    elif "write" in command or "create" in command:
        # AI-generated text
        prompt = command.replace("write", "").replace("create", "").strip()
        return f"Here's what I wrote: {generate_response(prompt)}"
    
    else:
        # General AI response
        return generate_response(command)

def listen_for_command():
    """
    Capture voice input and convert it to text.
    """
    print("Listening for your command...")
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio)
        logging.info(f"Recognized command: {command}")
        
        # Check if the user wants to exit
        if "that's enough for now" in command.lower():
            print("Exiting AI CEO. Goodbye!")
            exit(0)  # Terminate the program
        
        return command
    except sr.UnknownValueError:
        logging.error("Speech recognition could not understand audio.")
        return "Sorry, I couldn't understand the command."
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service: {e}")
        return f"Error with speech recognition: {e}"

def main():
    print("Welcome to AI CEO!")
    logging.info("AI CEO Activated.")

    # Step 1: Voice Authentication
    authenticated = authenticate_voice()
    if not authenticated:
        print("Authentication failed. Exiting...")
        return
    
    print("Authentication successful. Listening for commands...")
    
    # Step 2: Listen for Commands
    try:
        while True:
            command = listen_for_command()
            if "exit" in command.lower():
                print("Exiting AI CEO. Goodbye!")
                break
            
            if command:
                result = process_command(command)
                print(f"AI CEO: {result}")
    except KeyboardInterrupt:
        print("\nExiting AI CEO. Goodbye!")

if __name__ == "__main__":
    main()