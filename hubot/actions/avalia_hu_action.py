from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from utils.api_openai import APIOpenAI
from typing import Any, Text, Dict, List, Tuple, List


def desmebrar_historia_usuario(historia_usuario: str) -> Tuple[str, List[str]]:
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


def obter_melhorias(hu_analise: str) -> List[str]:
    melhorias = []

    linhas_hu_analise = hu_analise.split("\n")

    for linha in linhas_hu_analise:
        if 'CORREÇÃO' in linha or 'MELHORIA' in linha:
            if linha.split(" ")[0] == 'Como':
                melhorias.append(f'{len(melhorias)+1}. (Titulo): {linha}')
            else:
                melhorias.append(f'{len(melhorias)+1}. (Criterio de aceiração): {linha[3:]}')

    return melhorias


class ActionAvaliarHU(Action):
    def name(self):
        return "action_avaliar_hu"

    def run(self, dispatcher, tracker, domain):
        api_openai = APIOpenAI()
        tipo_usuario = tracker.get_slot("tipo_usuario")
        objetivo_usuario = tracker.get_slot("objetivo_usuario")
        motivo_usuario = tracker.get_slot("motivo_usuario")
        criterios_aceitacao = tracker.get_slot("criterios_aceitacao")

        if criterios_aceitacao:
            lista_criterios = criterios_aceitacao.split(";")
            criterios_aceitacao = "\n".join(
                [f"{i+1}. {criterio.strip()}" for i, criterio in enumerate(lista_criterios)]
            )
        else:
            criterios_aceitacao = "Não há critérios de aceitação definidos, por favor, me sugira alguns."

        dispatcher.utter_message(text="Sua história de usuário foi avaliada com sucesso! 🚀")
        analise = api_openai.obter_analise_hu(
            f'Como {tipo_usuario}, quero {objetivo_usuario}, para {motivo_usuario}\n\nCritério(s) de Aceitação\n {criterios_aceitacao}'   
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

        return [SlotSet("analise_hu", analise)] 
    

class ActionAderirTodasSugestoes(Action):
    def name(self):
        return "action_aderir_todas_sugestoes"
    
    def run(self, dispatcher, tracker, domain):

        hu_analise = tracker.get_slot("analise_hu")
        hu_melhorada, criterios_aceitacao_melhorados = desmebrar_historia_usuario(
            hu_analise  # type: ignore
        )

        dispatcher.utter_message(
            text="Todas as sugestões foram aderidas com sucesso! 🎉"
        )

        return [
            SlotSet(
                "tipo_usuario", hu_melhorada.split(",")[0].split(" ")[1]
            ),
            SlotSet(
                "objetivo_usuario", 
                hu_melhorada.split(", quero ")[1].split(", para")[0]
            ),
            SlotSet(
                "motivo_usuario", 
                hu_melhorada.split(", para ")[1].split(".")[0]
            ),
            SlotSet(
                "criterios_aceitacao", 
                ";".join(criterios_aceitacao_melhorados)
            )
        ]


class ActionAderirAlgumasSugestoes(Action):
    def name(self):
        return "action_aderir_algumas_sugestoes"

    def run(self, dispatcher, tracker, domain):
        melhorias = []

        dispatcher.utter_message(
            text="Perfeito! Agora, se desejar, você pode adicionar sugestões de melhorias para a História de Usuário. Digite as sugestões que deseja aderir separadas por vírgula. Exemplo: 1, 3, 5"
        )

        hu_analise: str = tracker.get_slot("analise_hu")  # type: ignore
        melhorias = obter_melhorias(hu_analise)

        dispatcher.utter_message(text="\n")
        dispatcher.utter_message(text="Melhorias possíveis:")
        dispatcher.utter_message(text="\n".join(melhorias))

        return []


class ActionSugestoesAderidas(Action):
    def name(self):
        return "action_sugestoes_aderidas"
    
    def run(self, dispatcher, tracker, domain):
        lista_slots_set = []
        criterios_aceitacao_aderidos = ""

        hu_analise: str = tracker.get_slot("analise_hu")  # type: ignore
        hu_melhorada, _ = desmebrar_historia_usuario(hu_analise)

        melhorias = obter_melhorias(hu_analise)
        sugestoes_aderidas = tracker.get_slot("items_melhoria")

        if not sugestoes_aderidas:
            dispatcher.utter_message(text="Nenhuma sugestão foi aderida.")
            return []

        if sugestoes_aderidas:
            sugestoes_aderidas = sugestoes_aderidas.replace(" ", "").split(",")
            sugestoes_aderidas = [int(sugestao) for sugestao in sugestoes_aderidas]
        
        for sugestao in sugestoes_aderidas:  # type: ignore
            if sugestao > len(melhorias):
                dispatcher.utter_message(text=f"Sugestão '{sugestao}' não existe.")
                continue

            if sugestao == 1 and "(Titulo)" in melhorias[0]:
                lista_slots_set.append(SlotSet(
                "tipo_usuario", hu_melhorada.split(",")[0].split(" ")[1]
                ))
                lista_slots_set.append(SlotSet(
                    "objetivo_usuario", 
                    hu_melhorada.split(", quero ")[1].split(", para")[0]
                ))
                lista_slots_set.append(SlotSet(
                    "motivo_usuario", 
                    hu_melhorada.split(", para ")[1].split(".")[0]
                ))
            else:
                criterios_aceitacao_aderidos += melhorias[sugestao-1].split(": ")[1].split(" [")[0] + ";"

            dispatcher.utter_message(text=f"Sugestão '{sugestao}' aderida com sucesso! 🎉")
            dispatcher.utter_message(text=melhorias[sugestao-1])
        
        lista_slots_set.append(SlotSet(
            "criterios_aceitacao", 
            criterios_aceitacao_aderidos
        ))

        return lista_slots_set


class ActionApresentaHU(Action):
    def name(self):
        return "action_apresenta_hu"

    def run(self, dispatcher, tracker, domain):
        tipo_usuario = tracker.get_slot("tipo_usuario")
        objetivo_usuario = tracker.get_slot("objetivo_usuario")
        motivo_usuario = tracker.get_slot("motivo_usuario")
        criterios_aceitacao = tracker.get_slot("criterios_aceitacao")

        lista_criterios = criterios_aceitacao.split(";") if criterios_aceitacao else None

        if not lista_criterios:
            criterios_formatados = "Não foram levantados critérios de aceitação."
        else:
            criterios_formatados = "\n".join([f"{i+1}. {criterio.strip().capitalize()}" for i, criterio in enumerate(lista_criterios)])

        dispatcher.utter_message(
            text=f"# Historia de Usuário\n\n## Título\nComo {tipo_usuario}, quero {objetivo_usuario}, para {motivo_usuario}\n\n## Critério(s) de Aceitação\n{criterios_formatados}"
        )

        return []
