# Use an arm64v8 Ubuntu 22.04 base image (optimized for Raspberry Pi 4)

# FROM ubuntu:22.04

# Raspberry distribution
FROM arm64v8/ubuntu:22.04 

# Environment variable to suppress interactive prompts during package installation
# ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3, pip, and system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev build-essential && \
    apt-get clean && apt-get install -y cron

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency file
COPY . .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Enable permissions to the script
RUN chmod +x ./start.sh

# Create log files
RUN touch /var/log/cron.log

# Command to run the main script
CMD ["/app/start.sh"]


