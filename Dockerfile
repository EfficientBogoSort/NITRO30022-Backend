FROM python:3.9.1
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt