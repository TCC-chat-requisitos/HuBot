from actions.avalia_hu_action import ActionAvaliarHU, ActionAderirTodasSugestoes, ActionAderirAlgumasSugestoes

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionMostraHU(Action):

    def name(self) -> Text:
        return "action_mostra_hu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Recupera os slots necessários
        tipo_usuario = tracker.get_slot("tipo_usuario")
        objetivo_usuario = tracker.get_slot("objetivo_usuario")
        motivo_usuario = tracker.get_slot("motivo_usuario")
        criterios_aceitacao = tracker.get_slot("criterios_aceitacao")

        # Divide os critérios de aceitação em uma lista
        lista_criterios = criterios_aceitacao.split(";") if criterios_aceitacao else []

        # Formata os critérios em uma string separada por novas linhas
        criterios_formatados = "\n".join([f"{i+1}. {criterio.strip()}" for i, criterio in enumerate(lista_criterios)])

        # Monta a mensagem final
        mensagem = (
            f"Ótimo! A História de Usuário foi criada com sucesso! 🎉\n\n"
            f"- Como {tipo_usuario}, quero {objetivo_usuario} para que {motivo_usuario}.\n\n"
            f"Critérios de aceitação:\n"
            f"{criterios_formatados}"
        )

        # Envia a mensagem para o usuário
        dispatcher.utter_message(text=mensagem, parse_mode="MarkdownV2")

        dispatcher.utter_button_message(
            text="Deseja avaliar a História de Usuário criada? 🤔",
            buttons=[
                {"title": "Sim", "payload": "/avaliar_hu"},
                {"title": "Não", "payload": "/nao_avaliar_hu"},
            ]
        )

        return []
