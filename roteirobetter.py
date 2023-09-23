import os
import random

def fix_roteiro(arquivo):
    lista_resultado = []
    primeira_linha = 0  # Alteração aqui

    with open(arquivo, 'r') as entrada:
        for i, linha in enumerate(entrada):  # Alteração aqui
            if i == 0:  # Alteração aqui
                primeira_linha = int(linha.strip())  # Alteração aqui
                continue

            palavras = linha.strip().split()
            nova_linha = ''
            contador_palavras = 0
            for i, palavra in enumerate(palavras):
                palavra = palavra.replace('"', "")

                # Verificar se a palavra contém um hífen
                if '-' in palavra:
                    if len(palavra) == 1:
                        # Substituir o hífen por uma vírgula uma posição antes
                        palavra = palavra.replace('-', ', ')
                        contador_palavras = 0

                if ',' in palavra or '.' in palavra:
                    if ',' in palavra:
                        if palavra.find(',') == len(palavra) - 1:
                            contador_palavras = 0

                    if '.' in palavra:
                        if i + 1 < len(palavras):
                            if palavra.find('.') == len(palavra) - 1:
                                palavra = palavra.replace('.', '. \n')
                                contador_palavras = 0
                else:
                    contador_palavras += 1
                    if i == len(palavras) - 1:
                        palavra += '.'

                if contador_palavras >= random.randint(11, 13):
                    nova_linha += palavra + ', '
                    contador_palavras = 0
                    continue
                nova_linha += palavra + ' '

            lista_resultado.append(nova_linha.rstrip())

    return lista_resultado, primeira_linha



def roteiro_as_string(roteiro):
    return '\n'.join(roteiro)