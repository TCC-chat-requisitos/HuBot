cd hubot/

# Iniciar o servidor de ações do RASA em segundo plano
rasa run actions --actions actions &

# Iniciar o servidor principal do RASA
rasa run --model models --enable-api --cors "*"