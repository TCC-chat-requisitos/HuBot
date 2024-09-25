from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionObterTipoUsuario(Action):

    def name(self) -> Text:
        return "action_cria_hu"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        tipo_usuario = tracker.get_slot('tipo_usuario').upper()
        # objetivo_usuario = tracker.get_slot('objetivo_usuario').upper()
        # motivo_usuario = tracker.get_slot('motivo_usuario').upper()

        dispatcher.utter_message(text=f"Tem certeza que deseja criar um HU para um(a) {tipo_usuario}?")

        

        return []
