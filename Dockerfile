# Use the official Python image as the base image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY app/requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the entire app directory into the container
COPY app/ .

# Expose the port on which your Flask app will run
EXPOSE 8080

# Set environment variables
ENV GOOGLE_CLIENT_ID=your_google_client_id
ENV SESSION_SECRET_KEY=your_session_secret_key

# Run your Flask app
CMD ["python", "your_flask_app.py"]
