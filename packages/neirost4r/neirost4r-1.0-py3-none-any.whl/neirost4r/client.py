# fenst4r_client.py
import requests
from typing import Dict, Optional

class Neirost4r:
    """
    Минимальный Python-клиент для fenst4r.life/api/ai_v5.
    Просто отправляет POST-запрос с сообщением, профилем и флагами.
    """
    def __init__(self, api_url: str = "https://fenst4r.life/api/ai_v5"):
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

    def chat(
        self,
        message: str,
        profile: str = "friendly",
        flags: Optional[Dict] = None
    ) -> str:
        """
        Отправляет сообщение на API Fenst4r и возвращает текст ответа.
        """
        payload = {
            "message": message,
            "profile": profile,
            "flags": flags or {}
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.RequestException as e:
            raise RuntimeError(f"Ошибка при обращении к API: {e}")

# ===== Пример использования =====
if __name__ == "__main__":
    client = Neirost4r()  # исправлено название класса
    
    message = "Привет, расскажи что нового в технологиях"
    flags = {
        "provider": "mistral",
        "model": "mistral-medium",
        "formatting": True,
        "raw": False,
        "string": True,
        "clean": False,
        "uncensored": True,
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.9,
        "stop_sequences": "",
        "code_to_link": False
    }

    answer = client.chat(message=message, profile="friendly", flags=flags)
    print(answer)
