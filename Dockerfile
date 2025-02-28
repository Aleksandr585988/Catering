FROM python:3.11-slim

# ENV PYTHONUNBUFFERED=1

RUN apt-get update -y \
    # dependencies for building Python packages && cleaning apt apt packages
    && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools pipenv

WORKDIR /app/

# Install the application dependencies
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

# copy the project
COPY ./ ./

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]