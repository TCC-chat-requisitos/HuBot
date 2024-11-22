from actions.avalia_hu_action import ActionAvaliarHU, ActionAderirTodasSugestoes, ActionAderirAlgumasSugestoes

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

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


class ActionFormadaHU(Action):

    def name(self) -> Text:
        return "action_formada_hu"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        campos_formados = []

        tipo_usuario = tracker.get_slot("tipo_usuario")
        objetivo_usuario = tracker.get_slot("objetivo_usuario")
        motivo_usuario = tracker.get_slot("motivo_usuario")
        criterios_aceitacao = tracker.get_slot("criterios_aceitacao")

        if criterios_aceitacao:
            if criterios_aceitacao[-1] == ";":
                criterios_aceitacao = criterios_aceitacao[:-1]
            
            lista_criterios_aceitacao = criterios_aceitacao.split(";")
            lista_criterios_aceitacao = [criterio.capitalize() for criterio in lista_criterios_aceitacao]
            criterios_aceitacao = ";".join(lista_criterios_aceitacao)

            campos_formados.append(SlotSet("criterios_aceitacao", criterios_aceitacao))
        
        if tipo_usuario:
            campos_formados.append(
                SlotSet("tipo_usuario", tipo_usuario.lower())
            )
        else:
            campos_formados.append(
                SlotSet("tipo_usuario", "usuário")
            )
        
        if objetivo_usuario:
            campos_formados.append(
                SlotSet("objetivo_usuario", objetivo_usuario.lower())
            )
        else:
            campos_formados.append(
                SlotSet(
                    "objetivo_usuario", "'objetivo do usuário não informado'"
                )
            )
        
        if motivo_usuario:
            campos_formados.append(
                SlotSet("motivo_usuario", motivo_usuario.lower())
            )
        else:
            campos_formados.append(
                SlotSet(
                    "motivo_usuario", "'motivo do usuário não informado'"
                )
            )

        return campos_formados
