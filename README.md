# Medical AI Agent

An intelligent medical analytics assistant that analyzes real-world patient and prescription data using natural language. Built with **LangGraph**, **FastAPI**, **DuckDB**, and **OpenRouter**.


## Setup

### 1. Get your OpenRouter API key
1. Go to [https://openrouter.ai](https://openrouter.ai)
2. Sign in or create an account
3. Navigate to **Settings → Keys** and click **"Create Key"**
4. Copy your key (starts with `sk-or-v1-...`)

### 2. Choose a model
Browse available models at [https://openrouter.ai/models](https://openrouter.ai/models).

### 3. Configure your environment
```bash
# Copy the example config
cp .env.example .env

# Edit .env and fill in your credentials
nano .env
```

Your `.env` should look like this:
```ini
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx
MODEL_NAME=qwen/qwen3-32b
MAX_STEPS=15
MAX_RETRIES=3
```

> **Important**: Never commit `.env` to version control!



## Run the application

### Start services
```bash
docker-compose up --build
```

This will:
- Build and start the **FastAPI backend** (port `8000`)
- Build and serve the **React frontend** (port `80`)

### Open the app
Visit in your browser:
    http://localhost:80

### Stop services
```bash
docker-compose down
```
