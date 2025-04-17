# Stage 1: build stage
FROM python:3.13-slim
 
# Create the app directory
RUN mkdir /app
 
# Set the working directory inside the container
WORKDIR /app
 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
# Copy the Django project  and install dependencies
RUN pip install --upgrade pip
COPY requirements.txt  /app/
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the Django project to the container
COPY . /app/
 
# Expose the Django port
EXPOSE 8080

RUN chmod +x /app/entrypoint.prod.sh
 
# Run Django’s development server
CMD ["/app/entrypoint.prod.sh"]
