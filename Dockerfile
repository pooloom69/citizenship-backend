FROM python:3.11-slim

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /app/.venv

# Ensure venv pip is upgraded
RUN /app/.venv/bin/pip install --upgrade pip

# Copy requirements
COPY requirements.txt .

RUN /app/.venv/bin/pip uninstall -y httpx || true


# Install dependencies INSIDE venv
RUN /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Force reinstall OpenAI 최신 버전
RUN /app/.venv/bin/pip install --upgrade --force-reinstall openai==1.47.0

# Copy project
COPY . .

# ⛔ Proxy auto detect 문제 방지 (매우 중요)
ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""
ENV http_proxy=""
ENV https_proxy=""

# Uvicorn uses python from venv
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
