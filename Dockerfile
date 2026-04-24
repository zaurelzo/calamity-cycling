FROM python:3.10-slim

WORKDIR /home/app

RUN apt-get update && apt-get install -y bash

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["bash", "launch.sh"]