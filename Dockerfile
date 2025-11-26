FROM python:3.11-slim

WORKDIR /app

# Install pip + OS dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Remove all default python packages
RUN pip list --format=freeze | cut -d '=' -f1 | xargs -r pip uninstall -y

# Copy requirements
COPY requirements.txt .

# Clean install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Force reinstall OpenAI 최신 버전
RUN pip install --upgrade --force-reinstall openai==1.40.1

# Copy project files
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
