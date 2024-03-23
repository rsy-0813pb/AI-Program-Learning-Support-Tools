import time
import google.generativeai as genai
from google.api_core import exceptions

api_key = ""

def set_api_key(key):
    global api_key
    api_key = key
    genai.configure(api_key=api_key)

def check_solution(problem_statement, code, output):
    if not api_key:
        return "Please enter a valid Google Gemini API key."

    try:
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.0-pro-001",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[])

        convo.send_message(f"Problem Statement:\n{problem_statement}\n\nCode:\n{code}\n\nOutput:\n{output}\n\nPlease check if the provided code correctly solves the problem statement. If there are any syntax errors or the output does not match the expected output based on the problem statement, the solution is incorrect. Provide a clear explanation of what needs to be fixed if the solution is incorrect.")
        time.sleep(1)
        response = convo.last.text

        if "incorrect" in response.lower() or "error" in response.lower():
            return f"Incorrect solution. Hint: {response}"
        else:
            return "Correct solution!"

    except exceptions.InvalidArgument as e:
        return f"Invalid API key. Please enter a valid Google Gemini API key. Error: {str(e)}"