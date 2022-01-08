FROM python:3.10-slim
LABEL maintainer=Asgoret

ARG APP_USER=bot
ARG APP_GROUP=botgroup

ENV APP_USER=${APP_USER}
ENV APP_GROUP=${APP_GROUP}

ENV botToken=mock
ENV envFile=mock

RUN addgroup --system ${APP_GROUP} && adduser --system --ingroup ${APP_GROUP} ${APP_USER}

USER ${APP_USER}
WORKDIR /home/${APP_USER}
RUN mkdir ./bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./bot /bot
WORKDIR /bot

CMD ["python", "devopshelberbot.py", "-b=$botToken", "-e=$envFile"]
