[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

# Fastapi-Testrunner

`fastapi_testrunner` is an automated testing utility for **FastAPI applications**.  
It extracts the `openapi.json` schema from your running FastAPI app, automatically generates request data, and tests routes without requiring Postman or manual setup.

All test results are displayed in the terminal and stored in a `DeB_FastAPI_Test_Logs` folder with date & time logs — making it easy for developers to validate endpoints quickly.

---

## ✨ Features
- 🔗 Fetches `openapi.json` from your FastAPI `base_url`.
- ⚡ Automatically generates request payloads for testing.
- 🧩 Supports:
  - Custom input for specific routes
  - Adding headers
  - Including or excluding routes
- 📝 Saves test results to logs (`DeB_FastAPI_Test_Logs`).
- 🚀 No need for Postman or curl — just run and test all routes in one go.

---

## 🔢 Supported Data Types
- str
- int
- float
- bool
- dict
- list
- enum
- TypedDict
- date
- email
- list[...] → Lists of any of the above types
- 👉 This means your routes with parameters like List[int], List[str], or List[dict] are also supported.

---

## 📦 Installation

```bash
pip install fastapi_testrunner

```

---

## 🧑‍💻Examples

### ✅ Test All Routes Automatically
```python
from fastapi_testrunner import TestFastAPIRoutes

tester = TestFastAPIRoutes()
tester.start_test()

```

## On Class TestFastAPIRoutes
```python
TestFastAPIRoutes(
    custom_inputs: CustomInputFormat = {},
    base_url: str = 'http://127.0.0.1:8000/',
    headers: dict = None,
    routes_tocheck: list = [],
    routes_touncheck: list = []
)
```

## On Class CustomInputsFormat
```python
CustomInputFormat(TypedDict):
    method:str
    path:str
    isfor_params:bool
    isfor_json:bool
    data:dict
    headers:dict
```

## Example with Custom Input
```python
from fastapi_testrunner import TestFastAPIRoutes, CustomInputFormat

custom_input = CustomInputFormat(
        method="POST",
        path="/items",
        isfor_params=False,
        isfor_json=True,
        data={"name": "Laptop", "price": 999},
        headers={"Authorization": "Bearer TOKEN123"}
    )


tester = TestFastAPIRoutes(
    base_url="http://127.0.0.1:8000/",
    custom_input=custom_input,
    routes_touncheck=["/auth/login","/auth/otp"]
)

tester.start_test()
```