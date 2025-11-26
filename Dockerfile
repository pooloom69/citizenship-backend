FROM python:3.11-slim

WORKDIR /app

# Clean pip cache and uninstall everything
RUN pip install --upgrade pip
RUN pip list | awk 'NR>2 {print $1}' | xargs pip uninstall -y || true

COPY requirements.txt .

# Install only what we want
RUN pip install --no-cache-dir -r requirements.txt

# Force reinstall OpenAI
RUN pip install --upgrade --force-reinstall openai==1.40.1

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
