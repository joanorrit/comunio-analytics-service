## Dockerfile
#
## pull the official docker image
#FROM python:3.9.4-slim
#
## set work directory
#WORKDIR /app
#
## set env variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
## install dependencies
#COPY requirements.txt .
#RUN pip install -r requirements.txt
#
## copy project
#COPY . .

#
FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]