# Dockerfile
FROM python:3.6
ADD . /code
WORKDIR /code
ADD ./requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "-u", "/src/main.py"]