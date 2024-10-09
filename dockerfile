# Use the official Python image from DockerHub
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app

# Expose port 5000 to the outside world
EXPOSE 5000

# Set Flask environment to production
ENV FLASK_ENV=production

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
