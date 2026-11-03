"""Módulo auxiliar com funções de análise de texto e busca semântica."""

import os
import re
from typing import List, Tuple
import openai


def get_openai_client():
    """Configura e valida a chave de API da OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente OPENAI_API_KEY não foi configurada.")
    openai.api_key = api_key
    return openai


def key_word(prompt: str) -> str:
    """Gera uma busca recomendada para imagens com base em um prompt.

    Args:
        prompt (str): Texto para derivar as palavras-chave.

    Returns:
        str: Termo sugerido para pesquisa no Google Imagens.
    """
    client = get_openai_client()
    variable_tokens = max(100, 4000 - len(prompt))

    instruction = (
        "Return the output as if you were doing a search on google images, that is, "
        "prioritize a speech that, if I searched and looked at google images, I would know "
        "exactly what was happening, for example (Text: 'Pelé is better than ribamar', "
        f"return : 'Pelé vs ribamar photos'). With this in mind: {prompt}"
    )

    response = client.Completion.create(
        engine='text-davinci-003',
        prompt=instruction,
        max_tokens=variable_tokens,
        n=1,
        stop=None,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    retorno = response.choices[0].text.strip()
    return retorno.replace('.', '')


def key_theme(prompt: str) -> str:
    """Identifica se o texto trata de uma pessoa ou assunto genérico.

    Args:
        prompt (str): Trecho de texto a ser analisado.

    Returns:
        str: Identificação do sujeito ou assunto do texto.
    """
    client = get_openai_client()
    variable_tokens = max(100, 4000 - len(prompt))

    instruction = (
        f"{prompt} Does the text talk about a person or subject? If it's a subject, "
        "say the subject, if it's a person, say the person, don't justify yourself just say it."
    )

    response = client.Completion.create(
        engine='text-davinci-003',
        prompt=instruction,
        max_tokens=variable_tokens,
        n=1,
        stop=None,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    retorno = response.choices[0].text.strip()
    return retorno.replace('.', '')


def contar_paragrafos(arquivo: str) -> Tuple[List[str], int]:
    """Lê um arquivo de texto e o divide em parágrafos separados por pontos finais.

    Args:
        arquivo (str): Caminho do arquivo a ser lido.

    Returns:
        Tuple[List[str], int]: Lista de parágrafos/sentenças e a quantidade encontrada.
    """
    with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
        texto = f.read()

    paragrafos = [p.strip() for p in re.split(r'\.', texto) if p.strip()]
    return paragrafos, len(paragrafos)
