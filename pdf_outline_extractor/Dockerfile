FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all source files into container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run all steps
CMD ["python", "main.py"]
