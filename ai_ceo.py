import logging
import speech_recognition as sr
from duckduckgo_search import DDGS
from sympy import sympify
import cohere
from langchain_community.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_experimental.tools import PythonREPLTool
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import PyPDF2  # For reading PDF files
import tkinter as tk
from tkinter import filedialog

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Initialize Cohere API
COHERE_API_KEY = 'uZnDNG0nkoKv8lPqjrQlSklJsPZU5LQNXh1m5x4q'  # Replace with your actual API key
cohere_client = cohere.Client(COHERE_API_KEY)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Initialize LangChain agent for coding
llm = OpenAI(openai_api_key="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")  # Replace with your OpenAI API key if needed
agent = initialize_agent(
    tools=[PythonREPLTool()],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Function to send an email
def send_email(to_email, subject, body):
    sender_email = "your_email@gmail.com"  # Replace with your Gmail address
    sender_password = "your_password"      # Replace with your Gmail app password

    # Create the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

# Function to read a PDF file
def read_pdf(file_path):
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
            return text
    except FileNotFoundError:
        return "File not found. Please provide a valid PDF file path."
    except Exception as e:
        return f"Error reading PDF: {e}"

# Function to open a file dialog and select a PDF file
def browse_for_pdf():
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window
        file_path = filedialog.askopenfilename(
            title="Select a PDF file",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if not file_path:
            logging.warning("User canceled file selection.")
        return file_path
    except Exception as e:
        logging.error(f"Error opening file dialog: {e}")
        return ""

# Process voice command
def process_command(command):
    command = command.lower()
    
    if "calculate" in command:
        try:
            expression = command.replace("calculate", "").strip()
            result = sympify(expression)
            return f"The result is {result}."
        except Exception as e:
            return f"Error calculating: {e}"
    
    elif "search" in command:
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
    
    elif "read pdf" in command.lower() or "open pdf" in command.lower():
        try:
            # Open file dialog to browse for PDF
            print("Opening file dialog to select a PDF...")
            file_path = browse_for_pdf()
            
            if not file_path:
                return "No file selected. Operation canceled."
            
            # Read the PDF file
            text = read_pdf(file_path)
            return f"PDF Content:\n\n{text}"
        except Exception as e:
            return f"Error reading PDF: {e}"
    
    elif "write" in command or "create" in command:
        prompt = command.replace("write", "").replace("create", "").strip()
        return f"Here's what I wrote: {generate_response(prompt)}"
    
    elif "code" in command:
        try:
            code_prompt = command.replace("code", "").strip()
            generated_code = agent.run(f"Generate Python code for: {code_prompt}")
            return f"Generated Python code:\n\n{generated_code}"
        except Exception as e:
            return f"Error generating code: {e}"
        
    elif "send an email" in command:
        try:
            # Extract recipient, subject, and body from the command
            parts = command.split(" to ")
            if len(parts) > 1:
                to_email = parts[1].strip()
            else:
                to_email = "xyz@gmail.com"  # Default recipient
            
            subject = "Automated Email"
            body = "This is an automated email sent by AI CEO."
            
            result = send_email(to_email, subject, body)
            return result
        except Exception as e:
            return f"Error sending email: {e}"
    
    else:
        return "Command not recognized. Please try again."

# Listen for commands
def listen_for_command():
    print("Listening for your command...")
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio)
        logging.info(f"Recognized command: {command}")
        print(f"DEBUG: Recognized command: {command}")  # Add this line for debugging
        return command
    except sr.UnknownValueError:
        logging.error("Speech recognition could not understand audio.")
        return "Sorry, I couldn't understand the command."
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service: {e}")
        return f"Error with speech recognition: {e}"

# Voice authentication
def authenticate_voice():
    print("Please say your authentication phrase.")
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio)
        logging.info(f"Recognized command: {command}")
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

# Main execution
def main():
    print("Welcome to AI CEO!")
    logging.info("AI CEO Activated.")

    authenticated = authenticate_voice()
    if not authenticated:
        print("Authentication failed. Exiting...")
        return
    
    print("Authentication successful. Listening for commands...")
    
    try:
        while True:
            command = listen_for_command()
            
            # Check for exit phrases
            if "exit" in command.lower() or "that's enough for now" in command.lower():
                print("Exiting AI CEO. Goodbye!")
                break
            
            if command:
                result = process_command(command)
                print(f"AI CEO: {result}")
    except KeyboardInterrupt:
        print("\nExiting AI CEO. Goodbye!")

if __name__ == "__main__":
    main()