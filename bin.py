import openai
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pydub import AudioSegment
import time
from gtts import gTTS
import os

from vm2gi import create_video_from_text
import legendaput as legendaB
import roteirobetter as rB

###         ###    
### PARTE 1 ### CRIAR UM ROTEIRO COM BASE NO TEMA
###         ###

def get_Idea(nome_arquivo):
    with open(nome_arquivo, 'r+') as arquivo:
        linhas = arquivo.readlines()  # Lê todas as linhas do arquivo
        numero_asterisco = 0
        numero_ponto = 0
        numero_hifen = 0

        if linhas:
            primeira_linha = linhas[0].strip()  # Pega a primeira linha e remove espaços em branco
            string_retornada = primeira_linha.split('.', 1)[0]
            
            # Obtém o número após o caractere '.' na primeira linha, se existir
            ponto_index = primeira_linha.find('.')
            if ponto_index != -1:
                numero_str = primeira_linha[ponto_index + 1:].strip()
                if numero_str.isdigit():
                    numero_ponto = int(numero_str)
            
            asterisco_index = primeira_linha.find('*')
            if asterisco_index != -1 and asterisco_index + 1 < len(primeira_linha):
                proximo_caractere = primeira_linha[asterisco_index + 1]
                if proximo_caractere.isdigit():
                    numero_asterisco = int(proximo_caractere)
            
            hifen_index = primeira_linha.find('-')
            if hifen_index != -1 and hifen_index + 1 < len(primeira_linha):
                proximo_caractere = primeira_linha[hifen_index + 1]
                if proximo_caractere.isdigit():
                    numero_hifen = int(proximo_caractere)

            restante_linhas = linhas[1:]  # Pega as linhas restantes do arquivo

            arquivo.seek(0)  # Volta para o início do arquivo
            arquivo.truncate()  # Limpa o conteúdo do arquivo

            # Escreve as linhas restantes no arquivo atualizado
            for linha in restante_linhas:
                arquivo.write(linha)

            # Retorna a primeira linha como uma string, o número após o ponto,
            # o número após o asterisco e o número após o hífen
            return [string_retornada, numero_ponto, numero_asterisco, numero_hifen]
        else:
            return None  # Retorna None se o arquivo estiver vazio

def clean_prompt(string): #Limpa os caracteres inválidos para futuramente salvar o promp como nome de  arquivo
    caracteres_invalidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '!']

    for i, char in enumerate(string):
        if char in caracteres_invalidos:
            return string[:i]

    return string


# Defina a chave de API da OpenAI
openai.api_key = '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'

# Parâmetros de entrada para a chamada da API
ideasPrompt = get_Idea("roteiros/Ideias.txt")

if ideasPrompt is None:
    quit()


options = [
    " answer it charismactly as a video that have 1 minute duration or less, make it relaxed (return only raw text, no specifications)",
    " in 1 minute video or less, tell like it was a self story, with some big plot at final"
]

variable_tokens = 4000-len(options[ideasPrompt[1]]) - len(ideasPrompt[0])

print(f"Vídeo a fazer: {ideasPrompt[0]}")
print(f"Opção escolhida: {options[ideasPrompt[1]]}")

# Faz a chamada para gerar uma resposta
response = openai.Completion.create(
    engine='text-davinci-003',
    prompt=ideasPrompt[0] + options[ideasPrompt[1]],
    max_tokens=variable_tokens,
    n=1,
    stop=None,
    temperature=0.7,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)


# Obtém a última resposta gerada
last_response = response.choices[0].text.strip()
clean_answer = last_response.split()

option = ""
if ideasPrompt[2] > 1:
    option = f' {ideasPrompt[2]}'
pasta_nome_base = unidecode(f'{clean_prompt(ideasPrompt[0]).lower()}{option}').replace(' ', '_') #Futuramente caso usasse a biblioteca os, o espaço daria problema

# Escreve a última resposta em um arquivo de texto 
with open(f'roteiros/{pasta_nome_base}.txt', 'w') as arquivo:
    arquivo.write(unidecode(last_response))

print(f"\nÚltima resposta gravada no arquivo 'roteiros/{pasta_nome_base}.txt'.")

###         ###    
### PARTE 2 ### - TRANSFORMAR O ROTEIRO EM ÁUDIO MP3
###         ###

# Exemplo de uso

roteiro = rB.fix_roteiro(f"roteiros/{pasta_nome_base}.txt")

parte_text = ""
if ideasPrompt[2] > 1:
    parte_text = f" part {ideasPrompt[2]}!"

texto = f"{ideasPrompt[0]} {parte_text} "+ rB.roteiro_as_string(roteiro) + " Subscribe into our channel for more!"

tts = gTTS(text=texto, lang='en-us')  # 'pt-br' para voz em português brasileiro

arquivo_mp3 = f"audios/{pasta_nome_base}.mp3"
tts.save(arquivo_mp3)

audio = AudioSegment.from_file(arquivo_mp3, format="mp3")
speed_aud = 1.1

if audio.__len__ > 70 * 1000:
    speed_aud = 1.2

audio = audio._spawn(audio.raw_data, overrides={
    "frame_rate": int(audio.frame_rate * speed_aud) # Agiliza o áudio
})

audio.export(arquivo_mp3, format="mp3")

arquivo_mp3_clean = f"audios/Base_{pasta_nome_base}.mp3"
audio.export(arquivo_mp3_clean, format="mp3")

###         ###    
### PARTE 3 ### TRANSFORMAR O ÁUDIO EM VÍDEO
###         ###

arquivo_saida = f"videos/{pasta_nome_base}.mp4"
arquivo_finale = f"videos/{pasta_nome_base}_finale.mp4"

create_video_from_text(arquivo_saida, arquivo_mp3, id=ideasPrompt[3])

###         ###    
### PARTE 4 ### BOTAR LEGENDA NO VÍDEO
###         ###

roteiro = [
    texto,
]

legendas = legendaB.sincronizar_legendas(roteiro, arquivo_mp3_clean)
legendaB.adicionar_legendas(arquivo_saida, legendas, arquivo_finale)
os.remove(arquivo_saida)
os.remove(arquivo_mp3_clean)
os.rename(arquivo_finale, arquivo_saida)


###         ###    
### PARTE 5 ### 
###         ###