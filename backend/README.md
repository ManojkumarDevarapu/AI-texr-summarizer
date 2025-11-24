# AI Text Summarizer Backend

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create .env file:
```bash
cp .env.example .env
```

4. Run the application:
```bash
python app.py
```

The server will start on http://localhost:5000

## API Endpoints

### POST /api/summarize
Summarize text using BART model

**Request Body:**
```json
{
  "text": "Your long text here...",
  "min_length": 25,
  "max_length": 100
}
```

**Response:**
```json
{
  "success": true,
  "summary": "Summarized text...",
  "original_length": 150,
  "summary_length": 45,
  "parameters": {
    "min_length": 25,
    "max_length": 100
  }
}
```

### GET /health
Check API health status

## Production Deployment

Use gunicorn for production:
```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --timeout 120
```