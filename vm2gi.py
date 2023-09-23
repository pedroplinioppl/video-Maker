from moviepy.editor import ImageSequenceClip, AudioFileClip
from google_images_search import GoogleImagesSearch
from moviepy.video.compositing.concatenate import concatenate_videoclips
import os
import random
from mutagen.mp3 import MP3
from diretoriofunc import *
import subprocess
from concatenateaudio import juntar_audios

def download_images(query, num_images):
    gis = GoogleImagesSearch('AIzaSyAxHN_qPzlAlEne62d4MYXHkvBl9h8EA_4', 'd7ce9af48fd6f47a8')

    _search_params = {
        'q': query,
        'num': 10,
        'fileType': 'jpg|png',
        'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
        'safe': 'off', ##
        'imgType': 'photo', ##
        'imgSize': 'large', ##
    }

    gis.search(search_params=_search_params)

    paths = []
    for i, image in enumerate(gis.results()):
        if i >= num_images:
            break

        image.download('Imagens/')
        image.resize(500, 500)
        paths.append(f'{image.path}')
    if len(paths) == 0:
        print("Não foi encontrado imagens para a pesquisa: " + query)
    else:
        print(f"Imagem {len(paths)} baixada")
    return paths

from moviepy.editor import *

def create_video_from_text(output_file, audio_file, monotheme=False, id=0):
    background_audio_file = "backgroundmusic.mp3"

    # Juntar áudios
    juntar_audios(audio_file, background_audio_file, audio_file, 10)

    # Se monotheme == False:
    #     context, len_context = contar_paragrafos(roteiro)
    # else:
    #     context, len_context = contar_paragrafos(f"roteiros/{roteiro}.txt")

    videos_folder = "videosBase/"
    video_files = os.listdir(videos_folder)
    random.shuffle(video_files)  # Embaralhar a ordem dos vídeos

    # Selecionar o primeiro clipe de vídeo aleatório
    first_video_file = random.choice(os.listdir("thumbVideos/"))
    if id != 0:
        first_video_clip = os.listdir("thumbVideos/")[id]
        
    first_video_path = os.path.join("thumbVideos/", first_video_file)
    
    video_clips = []
    total_duration = 0

    # Carregar o primeiro clipe de vídeo
    first_video_clip = VideoFileClip(first_video_path)

    # Definir a duração do primeiro clipe de vídeo entre 4 e 7 segundos
    first_video_duration = random.uniform(3, 5)
    if first_video_clip.duration > first_video_duration:
        first_video_clip = first_video_clip.subclip(0, first_video_duration)
    else:
        first_video_clip = first_video_clip.fx(vfx.speedx, first_video_duration / first_video_clip.duration)

    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration

        # Redimensionar o clipe de vídeo para as dimensões desejadas
    first_video_clip = first_video_clip.resize((1080, 1920))

    # Adicionar o primeiro clipe de vídeo à lista de clipes
    video_clips.append(first_video_clip)
    total_duration += first_video_clip.duration

    while total_duration < audio_duration:
        # Selecionar um vídeo aleatório
        video_file = random.choice(video_files)
        video_path = os.path.join(videos_folder, video_file)

        # Carregar o vídeo
        video_clip = VideoFileClip(video_path)

        # Redimensionar o clipe de vídeo para as dimensões desejadas
        video_clip = video_clip.resize((1080 , 1920))

        # Verificar se a duração do vídeo excede a duração restante do áudio
        remaining_duration = audio_duration - total_duration
        if video_clip.duration > remaining_duration:
            video_clip = video_clip.subclip(0, remaining_duration)

        # Adicionar o vídeo à lista de clipes
        video_clips.append(video_clip)
        total_duration += video_clip.duration

    # Concatenar os clipes de vídeo
    final_video = concatenate_videoclips(video_clips)

    # Configurar áudio no vídeo
    final_video = final_video.set_audio(audio)

    # Definir codec e gravar vídeo com áudio
    final_video.write_videofile(output_file, codec="libx264", fps=24, audio_codec="aac")

    print(f"Vídeo criado: {output_file}")