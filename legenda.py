"""Módulo para sincronização de legendas com o áudio e inserção de textos no vídeo."""

import os
from random import randint
from typing import Dict, List, Union
import moviepy.editor as mp
import sincronize_audio as sA


def sincronizar_legendas(roteiro: List[str], audio_file: str) -> List[Dict[str, Union[str, float]]]:
    """Segmenta o roteiro em trechos curtos e sincroniza os tempos com as pausas do áudio.

    Args:
        roteiro (List[str]): Lista com o texto do roteiro.
        audio_file (str): Caminho para o arquivo de áudio para medir tempos e silêncios.

    Returns:
        List[Dict[str, Union[str, float]]]: Lista de dicionários contendo {'text', 'start', 'end'}.
    """
    legendas: List[Dict[str, Union[str, float]]] = []

    decibel_levels = sA.calculate_decibel_level(audio_file)
    drop_points = sA.find_drop_points(decibel_levels)
    drop_index = 0

    for linha in roteiro:
        analyzing = 13
        frases = []
        frase_atual = ""
        aspas_counter = 0

        for i, caractere in enumerate(linha):
            if caractere in [",", ":", ";", ".", "?", "!", "\"", "(", ")"]:
                if frase_atual:
                    frase_atual += caractere
                    if caractere in [',', '.']:
                        if i + 1 < len(linha):
                            if linha[i + 1] == ' ' or not linha[i + 1].isdigit():
                                frases.append(frase_atual.strip())
                                frase_atual = ""
                                analyzing = 0
                        else:
                            frases.append(frase_atual.strip())
                            frase_atual = ""
                            analyzing = 0
                    elif caractere == "(":
                        frases.append(frase_atual[:-1].strip())
                        frase_atual = "("
                        analyzing = 0
                    elif caractere == ")":
                        frases.append(frase_atual.strip())
                        frase_atual = ""
                        analyzing = 0
                    elif caractere == "\"":
                        aspas_counter += 1
                        if aspas_counter % 2 != 0:
                            frases.append(frase_atual.strip())
                            frase_atual = ""
                    else:
                        frases.append(frase_atual.strip())
                        frase_atual = ""
                        analyzing = 0
            else:
                if len(frase_atual) >= analyzing and caractere == " ":
                    caractere = '\n'
                    analyzing += 13
                frase_atual += caractere

        if frase_atual:
            frases.append(frase_atual.strip())

        for frase in frases:
            if not frase:
                continue

            drop_start = 0.0
            drop_end = 2.0
            if drop_index < len(drop_points):
                p_start, p_end = drop_points[drop_index]
                drop_start = max(0.0, (p_start + randint(1, 100)) / 1000.0)
                drop_end = max(drop_start + 0.5, (p_end + randint(1, 100)) / 1000.0)
                drop_index += 1

            legenda = {"text": frase, "start": drop_start, "end": drop_end}
            legendas.append(legenda)

    return legendas


def adicionar_legendas(video_path: str, legendas: List[Dict[str, Union[str, float]]], output_file: str) -> None:
    """Insere as legendas centralizadas estilizadas em cima do arquivo de vídeo.

    Args:
        video_path (str): Caminho do vídeo original.
        legendas (List[Dict[str, Union[str, float]]]): Lista de dicionários com 'text', 'start' e 'end'.
        output_file (str): Caminho onde o vídeo legendado será salvo.
    """
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    video = mp.VideoFileClip(video_path)

    legendas_clips = [
        mp.TextClip(
            str(l['text']),
            fontsize=randint(100, 115),
            color='white',
            font="Calibri",
            stroke_color="black",
            stroke_width=1.0
        )
        .set_duration(float(l['end']) - float(l['start']))
        .set_start(float(l['start']))
        .set_position('center')
        for l in legendas
        if float(l['end']) > float(l['start'])
    ]

    video_final = mp.CompositeVideoClip([video] + legendas_clips)
    video_final.write_videofile(output_file, codec="libx264", audio_codec="aac")
    video.close()
    video_final.close()
