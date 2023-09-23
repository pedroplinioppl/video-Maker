import pydub
from pydub import AudioSegment
from time import sleep

def calculate_decibel_level(audio_file):
    sound = AudioSegment.from_mp3(audio_file)

    # Aumentar o volume do áudio em 20 decibéis
    sound += 20

    # Definir o intervalo de tempo para cálculo em milissegundos
    interval = 100

    # Definir a quantidade de milissegundos para cada cálculo
    step = 100

    # Calcular o nível de decibéis em cada intervalo de tempo
    decibel_levels = []
    for i in range(0, len(sound), step):
        segment = sound[i:i+interval]
        decibel = segment.dBFS
        decibel_levels.append(decibel)

    return decibel_levels

def find_drop_points(decibel_levels):
    drop_points = []
    start_point = None

    for i, level in enumerate(decibel_levels):
        if level > -50:
            if start_point is None:
                start_point = i * 100  # Tempo em milissegundos

        elif start_point is not None:
            end_point = i * 100  # Tempo em milissegundos

            drop_points.append((start_point, end_point))
            start_point = None


    return drop_points