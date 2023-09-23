import moviepy.editor as mp
import sincronizeAudio as sA
from random import randint
import roteirobetter as rB

# Função para sincronizar as legendas com base no roteiro e na taxa de palavras por minuto (wpm)
def sincronizar_legendas(roteiro, audio_file):
    legendas = []

    decibel_levels = sA.calculate_decibel_level(audio_file)
    drop_points = sA.find_drop_points(decibel_levels)
    drop_index = 0

    for linha in roteiro:
        anaylising = 13
        frases = []
        frase_atual = ""
        aspasCounter = 0

        for i, caractere in enumerate(linha):
            if caractere in [",", ":", ";", ".", "?", "!", "\"", "(", ")"]:
                if frase_atual:
                    frase_atual += caractere
                    if caractere == ',':
                        if i+1 < len(linha):
                            if linha[i+1] == ' ':
                                frases.append(frase_atual.strip())
                                frase_atual = "" 
                                anaylising = 0
                            else:
                                if linha[i+1].isdigit() is False:
                                    frases.append(frase_atual.strip())
                                    frase_atual = "" 
                                    anaylising = 0
                        else:
                            frases.append(frase_atual.strip())
                            frase_atual = "" 
                            anaylising = 0

                    elif caractere == '.':
                        if i+1 < len(linha):
                            if linha[i+1] == ' ':
                                frases.append(frase_atual.strip())
                                frase_atual = "" 
                                anaylising = 0
                            else:
                                if linha[i+1].isdigit() is False:
                                    frases.append(frase_atual.strip())
                                    frase_atual = "" 
                                    anaylising = 0
                        else:
                                frases.append(frase_atual.strip())
                                frase_atual = "" 
                                anaylising = 0
                    elif caractere == "(":
                        frases.append(frase_atual[:len(frase_atual)-2].strip())
                        frase_atual = "(" 
                        anaylising = 0

                    elif caractere == ")":
                        frases.append(frase_atual.strip())
                        frase_atual = "" 
                        anaylising = 0

                    elif caractere == "\"":
                        aspasCounter += 1
                        if aspasCounter % 2 != 0:
                            frases.append(frase_atual.strip())
                            frase_atual = "" 
                    else:
                        frases.append(frase_atual.strip())
                        frase_atual = ""    
                        anaylising = 0                  
            else:
                if len(frase_atual) >= anaylising and caractere == " ":
                    caractere = '\n'
                    anaylising += 13
                frase_atual += caractere
        if frase_atual:
            frases.append(frase_atual.strip())

        for frase in frases:
            # Substituir valores de início e fim pela queda repentina de decibéis, se houver
            if drop_index < len(drop_points):
                drop_start, drop_end = drop_points[drop_index]
                drop_start = (drop_start + randint(1, 100)) / 1000
                drop_end = (drop_end + randint(1,100)) / 1000
                drop_index += 1
    
            legenda = {"text": frase, "start": drop_start, "end": drop_end}
            legendas.append(legenda)

    return legendas

# Função para adicionar legendas personalizadas ao vídeo
def adicionar_legendas(video_path, legendas, outputfile):
    video = mp.VideoFileClip(video_path)

    # Adiciona as legendas
    legendas_clips = [
        mp.TextClip(l['text'], fontsize=randint(110, 125), color='white', font="Calibri", stroke_color = "black", stroke_width = 0.9)
        .set_duration(l['end'] - l['start'])
        .set_start(l['start'])
        .set_position('center')
        for l in legendas
    ]
    video = mp.CompositeVideoClip([video] + legendas_clips)

    # Salva o vídeo com as legendas
    video.write_videofile(outputfile, codec="libx264", audio_codec="aac")