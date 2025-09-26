# Use an official Python runtime as a parent image
# Using a specific version ensures build consistency. 'slim' is a smaller image size.
FROM python:3.9-slim

# Set the working directory in the container to keep things organized
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching.
# This layer only rebuilds if requirements.txt changes.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces the image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Make port 5001 available to the world outside this container
EXPOSE 5001

# The command to run the application when the container starts.
# For production, it's recommended to use a proper WSGI server like Gunicorn.
# Example for production: CMD ["gunicorn", "--bind", "0.0.0.0:5001", "cpanel_mcp_server:app"]
CMD ["python", "cpanel_mcp_server.py"]
