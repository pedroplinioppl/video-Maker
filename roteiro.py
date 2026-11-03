"""Módulo para formatação, pontuação e pré-processamento de roteiros de texto."""

import random
from typing import List, Tuple


def fix_roteiro(arquivo: str) -> Tuple[List[str], int]:
    """Lê um arquivo de roteiro, ajusta pausas/pontuações e retorna as linhas formatadas.

    O arquivo de roteiro pode opcionalmente conter um identificador numérico na primeira linha.

    Args:
        arquivo (str): Caminho para o arquivo de texto contendo o roteiro.

    Returns:
        Tuple[List[str], int]: Linhas formatadas do roteiro e identificador da primeira linha.
    """
    lista_resultado: List[str] = []
    primeira_linha = 0

    with open(arquivo, 'r', encoding='utf-8', errors='ignore') as entrada:
        linhas = entrada.readlines()

    if not linhas:
        return lista_resultado, primeira_linha

    inicio_idx = 0
    primeira_linha_candidata = linhas[0].strip()
    if primeira_linha_candidata.isdigit():
        primeira_linha = int(primeira_linha_candidata)
        inicio_idx = 1

    for linha in linhas[inicio_idx:]:
        palavras = linha.strip().split()
        if not palavras:
            continue

        nova_linha = ''
        contador_palavras = 0

        for i, palavra in enumerate(palavras):
            palavra = palavra.replace('"', "")

            # Tratar hífen isolado substituindo por vírgula para pausas naturais na voz
            if '-' in palavra and len(palavra) == 1:
                palavra = ', '
                contador_palavras = 0

            if ',' in palavra or '.' in palavra:
                if palavra.endswith(','):
                    contador_palavras = 0
                if palavra.endswith('.'):
                    if i + 1 < len(palavras):
                        palavra = palavra.replace('.', '. \n')
                    contador_palavras = 0
            else:
                contador_palavras += 1
                if i == len(palavras) - 1:
                    palavra += '.'

            # Insere pausas aleatórias a cada grupo de palavras para fluidez
            if contador_palavras >= random.randint(11, 13):
                nova_linha += palavra + ', '
                contador_palavras = 0
                continue

            nova_linha += palavra + ' '

        lista_resultado.append(nova_linha.rstrip())

    return lista_resultado, primeira_linha


def roteiro_as_string(roteiro: List[str]) -> str:
    """Converte a lista de linhas do roteiro em uma única string unificada.

    Args:
        roteiro (List[str]): Lista com as linhas do roteiro.

    Returns:
        str: Texto contínuo do roteiro.
    """
    return '\n'.join(roteiro)
