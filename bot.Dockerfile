FROM python:3.8

USER root

ADD ./hubot /app
ADD ./requirements.txt /app

RUN pip install --upgrade pip && \ 
    pip install --progress-bar off -r /app/requirements.txt

RUN python -m spacy download pt_core_news_sm

WORKDIR /app

ENTRYPOINT [ "rasa" ]

CMD [ "run", "--enable-api" ]