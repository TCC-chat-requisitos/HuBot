from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from utils.api_openai import APIOpenAI

class ActionAvaliarHU(Action):
    def name(self):
        return "action_avaliar_hu"
    
    def desmebrar_historia_usuario(self, historia_usuario: str):
        titulo_hu = historia_usuario.split(
            "## História de Usuário (analisada e corrigida)"
        )[1].split(".")[0].replace("\n", "")
        titulo_hu += "."

        criterios_aceitacao = []

        criterios = historia_usuario.split(
            "Critério(s) de Aceitação\n"
        )[1].split("Visão geral")[0].split("\n")

        for criterio in criterios:
            if criterio == "":
                continue

            if criterio[0].isnumeric():
                criterios_aceitacao.append(criterio.split(". ")[1])
            
            if criterios_aceitacao[-1][-1] != ".":
                criterios_aceitacao[-1] += "."
        
        return titulo_hu, criterios_aceitacao

    def run(self, dispatcher, tracker, domain):
        # Lógica para avaliar a história de usuário, exibir feedback, etc.

        api_openai = APIOpenAI()

        dispatcher.utter_message(text="Sua história de usuário foi avaliada com sucesso! 🚀")
        analise = api_openai.obter_analise_hu(
            f'Como {tracker.get_slot("tipo_usuario")}, quero {tracker.get_slot("objetivo_usuario")} para que {tracker.get_slot("motivo_usuario")}'
        )
        dispatcher.utter_message(text=analise)

        dispatcher.utter_button_message(
            text="Deseja aderir as sugestões?",
            buttons=[
                {"title": "Sim, todas", "payload": "/aderir_todas_sugestoes"},
                {"title": "Sim, algumas", "payload": "/aderir_algumas_sugestoes"},
                {"title": "Não", "payload": "/nao_aderir_sugestoes"},
            ]
        )

        return [] 
