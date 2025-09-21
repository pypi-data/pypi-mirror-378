# Neirost4r

Минимальный Python-клиент для [fenst4r.life API](https://fenst4r.life/api/ai_v5).  
Позволяет отправлять запросы к API и получать ответы от нейросети, используя профили и флаги.

## Установка

```bash
pip install neirost4r
```

## Пример использования

```python
from neirost4r import Neirost4r

client = Neirost4r()

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
```

Подробнее про использование параметры API: https://fenst4r.life/ai/api/