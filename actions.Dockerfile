FROM rasa/rasa-sdk:3.6.2

USER root

ADD ./hubot/actions /app/actions

CMD [ "start", "--actions", "actions" ]