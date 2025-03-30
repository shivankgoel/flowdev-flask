# Flask API

A basic Flask REST API with a clean directory structure.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On macOS/Linux:
```bash
source venv/bin/activate
```
- On Windows:
```bash
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. The API will be available at:
```
http://localhost:5000
```

## API Endpoints

- `GET /`: Welcome message
  ```json
  {
    "message": "Welcome to Flask API",
    "status": "success"
  }
  ```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   └── __init__.py
│   └── static/
├── app.py
├── requirements.txt
└── README.md
``` 