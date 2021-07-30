FROM python:3.10.0b4-alpine
LABEL maintainer=Asgoret

ARG user=bot
ARG group=botGroup

ENV botToken=mock
ENV envFile=mock

RUN addgroup -S ${group} && adduser -S ${user} -G ${group}; \
    apk add --no-cache gcc g++ musl-dev python3-dev libffi-dev openssl-dev cargo                  

USER ${user}

WORKDIR /home/${user}
COPY requirements.txt ./
RUN mkdir ./bot; \
    pip install --upgrade pip; \
    pip install setuptools --upgrade; \
    pip install --no-cache-dir -r requirements.txt
    
COPY ./bot /bot
WORKDIR /bot

CMD python devopshelberbot.py -b=$botToken -e=$envFile
