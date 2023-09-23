import openai
from unidecode import unidecode
from pydub import AudioSegment
from gtts import gTTS
import os

from vm2gi import create_video_from_text
import legendaput as legendaB
import roteirobetter as rB

###         ###    
### PARTE 1 ### CRIAR UM ROTEIRO COM BASE NO TEMA
###         ###

def return_roteiro(diretorio):
    # Obtém a lista de arquivos no diretório
    arquivos = os.listdir(diretorio)
    
    # Filtra apenas os arquivos de texto
    arquivos_texto = [arquivo for arquivo in arquivos if arquivo.endswith(".txt")]
    
    if len(arquivos_texto) == 0:
        return None, None
    
    # Obtém o primeiro arquivo de texto
    primeiro_arquivo = arquivos_texto[0]
    
    # Obtém o caminho completo para o arquivo
    caminho_arquivo = os.path.join(diretorio, primeiro_arquivo)
    
    # Lê o conteúdo do arquivo como uma string
    with open(caminho_arquivo, "r") as arquivo:
        conteudo = arquivo.read()
    
    # Retorna o conteúdo do arquivo e o nome do arquivo
    return conteudo, primeiro_arquivo



def clean_prompt(string): #Limpa os caracteres inválidos para futuramente salvar o promp como nome de  arquivo
    caracteres_invalidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '!']

    for i, char in enumerate(string):
        if char in caracteres_invalidos:
            return string[:i]

    return string


# Obtém a última resposta gerada
last_response, nome_video = return_roteiro("roteiros/")

print(f"Vídeo a fazer: {nome_video}")

pasta_nome_base = nome_video
nome_video = nome_video[:len(nome_video)-4]
###         ###    
### PARTE 2 ### - TRANSFORMAR O ROTEIRO EM ÁUDIO MP3
###         ###

# Exemplo de uso

roteiro, tipo_video = rB.fix_roteiro(f"roteiros/{pasta_nome_base}")

texto = f"{nome_video}! " + rB.roteiro_as_string(roteiro) + " Subscribe into our channel for more!"

tts = gTTS(text=texto, lang='en-us')  # 'pt-br' para voz em português brasileiro

arquivo_mp3 = f"audios/{pasta_nome_base}.mp3"
tts.save(arquivo_mp3)

audio = AudioSegment.from_file(arquivo_mp3, format="mp3")

audio = audio._spawn(audio.raw_data, overrides={
    "frame_rate": int(audio.frame_rate * 1.1) # Agiliza o áudio
})

audio.export(arquivo_mp3, format="mp3")

arquivo_mp3_clean = f"audios/Base_{pasta_nome_base}.mp3"
audio.export(arquivo_mp3_clean, format="mp3")

###         ###    
### PARTE 3 ### TRANSFORMAR O ÁUDIO EM VÍDEO
###         ###

arquivo_saida = f"videos/{pasta_nome_base}.mp4"
arquivo_finale = f"videos/{pasta_nome_base}_finale.mp4"

create_video_from_text(arquivo_saida, arquivo_mp3, id=tipo_video)

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
os.remove(f"roteiros/{pasta_nome_base}")

###         ###    
### PARTE 5 ### 
###         ###