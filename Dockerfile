FROM python:3.8.3-alpine

WORKDIR .

# Initialize environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Update and Install PostgreSQL dependency
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# Upgrade python pip
RUN pip install --upgrade pip

# Copy requirements.txt file and install required dependency for project
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy project directory
COPY . .
