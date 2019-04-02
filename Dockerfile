# Use an official Python runtime as a parent image
FROM python:3-slim

# Set up working directory and copy files into it
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY app/ /app/

# Run these commands during image creation
# RUN pip3 install --upgrade pandas
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "build-essential"]
RUN ["pip3", "install", "--upgrade", "Flask"]
RUN ["pip3", "install", "--upgrade", "pandas"]
RUN ["pip3", "install", "--upgrade", "matplotlib"]
RUN ["pip3", "install", "--upgrade", "seaborn"]
RUN ["pip3", "install", "--upgrade", "python-Levenshtein"]

# Make port 80 available to the outside world
EXPOSE 80

# The command to run every time a container based on this image is started
ENTRYPOINT ["python", "app.py"]

