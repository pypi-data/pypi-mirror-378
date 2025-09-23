# various_api_tools

A lightweight utility package for common API-related tasks in Python, including JSON and Pydantic error translators that provide user-friendly Russian messages.

---

## 📦 Features

- ✅ **JSON Error Translator** – Translates `JSONDecodeError` into clear Russian messages.
- ✅ **Pydantic Validation Error Translator** – Converts Pydantic validation errors into human-readable Russian strings.
- ✅ **Easy to integrate** – Designed for use in web APIs and data validation pipelines.

---

## 🐍 Installation

Install using pip from source or a private repository:

```bash
pip install various_api_tools
```

## 🧪 Basic Usage

### Translate JSON Decode Errors

```python
import json
from various_api_tools.translators.json import DecodeErrorTranslator

try:
    json.loads('{"name": "Alice",}')
except json.JSONDecodeError as e:
    print(DecodeErrorTranslator.translate(e))

# Output:
# Ошибка конвертации в формате JSON.
# Позиция: 16.
# Описание: не правильно используются двойные кавычки.
```

---

### Translate Pydantic Validation Errors

```python
from pydantic import BaseModel, ValidationError
from various_api_tools.translators.pydantic import ValidationErrorTranslator

class User(BaseModel):
    email: str

try:
    User(email=123)
except ValidationError as e:
    print(ValidationErrorTranslator.translate(e.errors()))

# Output:
# Поле: "email". Ошибка: "Невалидное строковое значение(str)";
```

---

## 📄 License

MIT License — feel free to use it in any project! 🎉

---

## 🧑‍💻 Made with ❤️ by [@dkurchigin](https://gitverse.ru/dkurchigin)

Have questions? Open an issue or contribute to the repo!


## 🐙 GITVERSE


🔗 [https://gitverse.ru/dkurchigin/various-api-tools](https://gitverse.ru/dkurchigin/various-api-tools)
