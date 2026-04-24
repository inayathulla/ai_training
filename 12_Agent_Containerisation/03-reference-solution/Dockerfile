# Use a slim Python base image — smaller image, faster pulls, smaller attack surface.
FROM python:3.11-slim

# The working directory inside the container.
WORKDIR /app

# Copy requirements first and install — this layer gets cached on rebuilds
# as long as requirements.txt doesn't change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application.
COPY . .

# Document the port the container listens on.
EXPOSE 5000

# Prevent Python from buffering stdout — we want logs to appear in real time.
ENV PYTHONUNBUFFERED=1

# Start the Flask app.
CMD ["python", "app.py"]
