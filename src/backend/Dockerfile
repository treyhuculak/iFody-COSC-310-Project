FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt from project root into container
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory into the container
COPY src ./src

# Set PYTHONPATH so 'src' is discoverable
ENV PYTHONPATH="/app"

EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
