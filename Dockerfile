FROM python:3.7.2-alpine
LABEL maintainer=Asgoret

ENV b=token
COPY requirements.txt ./
RUN mkdir /bot; \
    pip install --upgrade pip; \
    pip install setuptools --upgrade; \
    apk add --no-cache gcc g++ python3-dev libffi-dev openssl-dev; \
    pip install --no-cache-dir -r requirements.txt
    
COPY ./bot /bot
WORKDIR /bot

CMD python telebot.py -b=$b
