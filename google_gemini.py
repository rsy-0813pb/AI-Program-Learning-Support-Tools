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
        return "有効なGoogle Gemini APIキーを入力してください"

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

        convo.send_message(f"問題文:\n{problem_statement}\n\nコード:\n{code}\n\nターミナル出力:\n{output}\n\n提供されたコードが問題文を正しく解決しているかどうか確認してください。構文エラーがあったり、問題文から予想される出力と一致しない場合、<error>間違っています。</error>と答えてください。 解答が間違っていた場合、修正すべき点を明確に説明してください。また、日本語で答えてください。")
        time.sleep(1)
        response = convo.last.text

        if "<error>間違っています。</error>" in response.lower() or "error" in response.lower():
            return f"間違っています。 \nAI: \n{response}"
        else:
            return "正解です!"

    except exceptions.InvalidArgument as e:
        return f"APIキーが無効です。有効なGoogle Gemini APIキーを入力してください。エラー: {str(e)}"