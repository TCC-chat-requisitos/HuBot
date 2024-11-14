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
                melhorias.append(f'{len(melhorias)+1}. (Critério de aceiração Nº {linha[0]}): {linha[3:]}')

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

        tipo_usuario_anterior = tracker.get_slot("tipo_usuario_anterior")
        objetivo_usuario_anterior = tracker.get_slot("objetivo_usuario_anterior")
        motivo_usuario_anterior = tracker.get_slot("motivo_usuario_anterior")
        criterios_aceitacao_anterior = tracker.get_slot("criterios_aceitacao_anterior")

        if not tipo_usuario or not objetivo_usuario or not motivo_usuario:
            if (
                not tipo_usuario_anterior or 
                not objetivo_usuario_anterior or 
                not motivo_usuario_anterior
            ):
                dispatcher.utter_message(text="Ops! Para avaliar uma História de Usuário, você precisa cria-la primeiro.")
                dispatcher.utter_button_message(
                    text="Deseja criar uma história de usuário?",
                    buttons=[
                        {"title": "Sim", "payload": "/criar_hu"},
                        {"title": "Não", "payload": "/nao_criar_hu"},
                    ]
                )
                return []
            else:
                tipo_usuario = tipo_usuario_anterior
                objetivo_usuario = objetivo_usuario_anterior
                motivo_usuario = motivo_usuario_anterior
                criterios_aceitacao = criterios_aceitacao_anterior

        if not tipo_usuario or not objetivo_usuario or not motivo_usuario:
            dispatcher.utter_message(text="Ops! Para avaliar uma História de Usuário, você precisa cria-la primeiro.")
            dispatcher.utter_button_message(
                text="Deseja criar uma história de usuário?",
                buttons=[
                    {"title": "Sim", "payload": "/criar_hu"},
                    {"title": "Não", "payload": "/nao_criar_hu"},
                ]
            )
            return []

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
                "tipo_usuario_anterior", hu_melhorada.split(",")[0].split(" ")[1]
            ),
            SlotSet(
                "objetivo_usuario_anterior", 
                hu_melhorada.split(", quero ")[1].split(", para")[0]
            ),
            SlotSet(
                "motivo_usuario_anterior", 
                hu_melhorada.split(", para ")[1].split(".")[0]
            ),
            SlotSet(
                "criterios_aceitacao_anterior", 
                ";".join(criterios_aceitacao_melhorados)
            ),
            SlotSet("tipo_usuario", None), 
            SlotSet("objetivo_usuario", None), 
            SlotSet("motivo_usuario", None), 
            SlotSet("criterios_aceitacao", None)
        ]


class ActionNaoAderirSugestoes(Action):
    def name(self):
        return "action_nao_aderir_sugestoes"

    def run(self, dispatcher, tracker, domain):
        tipo_usuario = tracker.get_slot("tipo_usuario")
        objetivo_usuario = tracker.get_slot("objetivo_usuario")
        motivo_usuario = tracker.get_slot("motivo_usuario")
        criterios_aceitacao = tracker.get_slot("criterios_aceitacao")

        dispatcher.utter_message(
            text="Sem problemas! As sugestões não foram aderidas. Se precisar de ajuda, estou por aqui! 😉"
        )

        return [
            SlotSet("tipo_usuario_anterior", tipo_usuario), 
            SlotSet("objetivo_usuario_anterior", objetivo_usuario), 
            SlotSet("motivo_usuario_anterior", motivo_usuario), 
            SlotSet("criterios_aceitacao_anterior", criterios_aceitacao),
            SlotSet("tipo_usuario", None), 
            SlotSet("objetivo_usuario", None), 
            SlotSet("motivo_usuario", None), 
            SlotSet("criterios_aceitacao", None)
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

        dispatcher.utter_message(text="Melhorias possíveis:")
        dispatcher.utter_message(text="\n".join(melhorias))

        return []


class ActionSugestoesAderidas(Action):
    def name(self):
        return "action_sugestoes_aderidas"
    
    def run(self, dispatcher, tracker, domain):
        lista_slots_set = []
        criterios_aceitacao = tracker.get_slot("criterios_aceitacao")

        if criterios_aceitacao:
            lista_criterios = criterios_aceitacao.split(";")
        else:
            lista_criterios = []

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
                "tipo_usuario_anterior", hu_melhorada.split(",")[0].split(" ")[1]
                ))
                lista_slots_set.append(SlotSet(
                    "objetivo_usuario_anterior", 
                    hu_melhorada.split(", quero ")[1].split(", para")[0]
                ))
                lista_slots_set.append(SlotSet(
                    "motivo_usuario_anterior", 
                    hu_melhorada.split(", para ")[1].split(".")[0]
                ))
            else:
                num_criterio = int(melhorias[sugestao-1].split("Nº ")[1][0])
                lista_criterios[num_criterio-1] = melhorias[sugestao-1].split(": ")[1].split(" [")[0]

            dispatcher.utter_message(text=f"Sugestão '{sugestao}' aderida com sucesso! 🎉")
            dispatcher.utter_message(text=melhorias[sugestao-1])
        
        lista_slots_set.append(SlotSet(
            "criterios_aceitacao_anterior", 
            ";".join(lista_criterios)
        ))
        lista_slots_set = lista_slots_set + [
            SlotSet("tipo_usuario", None), 
            SlotSet("objetivo_usuario", None), 
            SlotSet("motivo_usuario", None), 
            SlotSet("criterios_aceitacao", None)
        ]

        return lista_slots_set


class ActionApresentaHU(Action):
    def name(self):
        return "action_apresenta_hu"

    def run(self, dispatcher, tracker, domain):
        tipo_usuario = tracker.get_slot("tipo_usuario_anterior")
        objetivo_usuario = tracker.get_slot("objetivo_usuario_anterior")
        motivo_usuario = tracker.get_slot("motivo_usuario_anterior")
        criterios_aceitacao = tracker.get_slot("criterios_aceitacao_anterior")

        lista_criterios = criterios_aceitacao.split(";") if criterios_aceitacao else None

        if not lista_criterios:
            criterios_formatados = "Não foram levantados critérios de aceitação."
        else:
            criterios_formatados = "\n".join([f"{i+1}. {criterio.strip().capitalize()}" for i, criterio in enumerate(lista_criterios)])

        dispatcher.utter_message(
            text=(
                f"# Historia de Usuário\n"
                f"## Título\n"
                f"Como {tipo_usuario}, quero {objetivo_usuario}, para {motivo_usuario}\n"
                f"## Critério(s) de Aceitação\n{criterios_formatados}"
            ),
            parse_mode="MarkdownV2"
        )
        
        return []
