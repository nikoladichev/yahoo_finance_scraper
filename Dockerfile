# Use the official Selenium standalone Chrome image
FROM selenium/standalone-chrome:latest

# Set the working directory inside the container
WORKDIR /

# Copy the current directory contents into the container at /app
COPY . /

# Install Python and pip
USER root
RUN apt-get update && apt-get install -y python3 python3-pip

# Install any additional dependencies your project may need
RUN pip3 install --no-cache-dir -r requirements.txt

#Expose server port
EXPOSE 9090

# Run your Python script
CMD ["python3", "server.py"]