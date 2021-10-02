# syntax=docker/dockerfile:1

FROM mongo:5.0.3
LABEL maintainer=zaurelzo

RUN apt-get update && apt-get install -y python3.8  python3-pip  python3.8-venv
WORKDIR /home
COPY . .
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
CMD ["bash", "-x" ,"launch.sh"]
