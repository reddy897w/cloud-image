# Use an official Python runtime as a parent image
FROM python:3.11.4

# Set the working directory to /app
WORKDIR /app

# Copy the entire project directory into the container
COPY . /app

# Copy the service account key file into the container
COPY service-account-key.json /app/service-account-key.json

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 5000

# Define environment variable if needed
# ENV NAME World

# Run your app
CMD ["python", "app.py"]
