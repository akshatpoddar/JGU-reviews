# Use the official Python runtime image
FROM python:3.13  
 
# Create the app directory
RUN mkdir /app
 
# Set the working directory inside the container
WORKDIR /app
 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
# Copy the Django project  and install dependencies
COPY requirements.txt  /app/
 
RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the Django project to the container
COPY . /app/
 
# Expose the Django port
EXPOSE 8080
 
# Run Django’s development server
# CMD ["gunicorn", "jgu_course_reviewier.wsgi:app", "--host", "0.0.0.0", "--port", "8080"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
