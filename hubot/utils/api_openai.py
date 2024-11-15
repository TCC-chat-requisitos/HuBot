from openai import OpenAI
from dotenv import load_dotenv

import os


class APIOpenAI:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )

    def obter_analise_hu(self, historia_usuario: str):
        """
        Função que recebe uma string com a história do usuário e retorna a análise da história de usuário.
        """
        prompt = self._prompt_analise_hu(historia_usuario)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def _prompt_analise_hu(self, historia_usuario: str):
        """
        Função que recebe uma string com a história do usuário e retorna um prompt.
        """
        prompt = f'''
# Análise de História de Usuário

Análise a história de usuário a seguir, lembrando que ela deve estar no seguinte padrão:
Como <persona>, quero <objetivo desejado>, para que <valor a ser alcançado>.

O padrão deve ser seguido para que a análise seja feita corretamente, não altere a estrutura do padrão, não retire vírgulas ou pontos finais impostos no padrão, apenas faça correções gramaticais e de concordância.

Verifique se a gramática está correta e se há possíveis incongruências nos locais de preenchimento da história de usuário. Caso encontre correções ou incongruências, recomende melhorias ou correções. Analise cada critério de aceitação e verifique se há possibilidade de melhoria ou correção. Se houver, sugira as correções necessárias, mencionando claramente o número do critério.

Exemplo de historia a ser analisada:

## Historia de usuário

Como client de um banco on-line, quero acessar meu extrato bancario de forma rápida e segura pelo aplicativo movel, para poder ver minhas transações financeiras a qualquer momento. 

Critério(s) de Aceitação

1. O usuário deve ser capaz de fazer login com autenticação de dois fatores.
2. O extrato bancário deve ser atualizado de 10 em 10 minutos.


Exemplo de resposta esperada, ou seja, retorna o titulo e os criterios de aceitação no mesmo formato, porém, com suas devidas melhorias e correções, além de mostrar mostrar entre colchetes se a alteração foi uma: melhoria, correção ou ambos. Tenho melhoria ou correção também é listado o motivo dessas correções e melhorias.

Resposta esperada:

## História de Usuário (analisada e corrigida)

Como cliente de um banco online, quero acessar meu extrato bancário de forma rápida e segura pelo aplicativo móvel, para poder monitorar minhas transações financeiras a qualquer momento. [MELHORIA/CORREÇÃO]
- client -> cliente.
- on-line -> online.
- bancario -> bancário.
- movel -> móvel.
- para poder ver minhas transações -> para poder monitorar minhas transações.

Critério(s) de Aceitação

1. O usuário deve ser capaz de fazer login com autenticação de dois fatores.
2. O extrato bancário deve ser atualizado em tempo real. [MELHORIA]
	- atualizado de 10 em 10 minutos -> atualizado em tempo real.

Visão geral: A análise mostra que a história de usuário e os critérios de aceitação estão bem formulados com pequenos ajustes gramaticais e de clareza necessários. Após a correção, a história de usuário cumpre o padrão desejado e os critérios de aceitação são claros e concisos.


Analise essa historia de usuário e responda na mesma estrutura do exemplo de resposta espera:

## Historia de usuário a ser analisada
 
{historia_usuario}
'''
        return prompt

