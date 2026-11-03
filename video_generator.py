"""Módulo responsável por gerar o vídeo compilando clipes de fundo e áudio sincronizado."""

import os
import random
from typing import List, Optional
from google_images_search import GoogleImagesSearch
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx
from concatenate_audio import juntar_audios


def download_images(query: str, num_images: int = 5, output_dir: str = "Imagens/") -> List[str]:
    """Busca e baixa imagens utilizando a Google Custom Search API.

    Args:
        query (str): Termo de busca no Google Imagens.
        num_images (int, optional): Número máximo de imagens a baixar. Padrão: 5.
        output_dir (str, optional): Diretório onde as imagens serão salvas. Padrão: 'Imagens/'.

    Returns:
        List[str]: Caminhos dos arquivos de imagem baixados.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CX")
    if not api_key or not cx:
        raise ValueError(
            "Variáveis GOOGLE_API_KEY e GOOGLE_CX devem ser definidas no ambiente para busca de imagens."
        )

    os.makedirs(output_dir, exist_ok=True)
    gis = GoogleImagesSearch(api_key, cx)

    search_params = {
        'q': query,
        'num': max(1, min(num_images, 10)),
        'fileType': 'jpg|png',
        'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
        'safe': 'off',
        'imgType': 'photo',
        'imgSize': 'large',
    }

    gis.search(search_params=search_params)

    paths: List[str] = []
    for i, image in enumerate(gis.results()):
        if i >= num_images:
            break
        image.download(output_dir)
        image.resize(500, 500)
        paths.append(str(image.path))

    if not paths:
        print(f"Nenhuma imagem encontrada para a pesquisa: {query}")
    else:
        print(f"{len(paths)} imagem(ns) baixada(s).")
    return paths


def create_video_from_text(
    output_file: str,
    audio_file: str,
    monotheme: bool = False,
    thumb_id: int = 0,
    background_audio_file: str = "backgroundmusic.mp3",
    videos_folder: str = "videosBase/",
    thumb_folder: str = "thumbVideos/"
) -> None:
    """Monta o vídeo vertical (1080x1920) combinando clipes de fundo com o áudio narrado.

    Args:
        output_file (str): Caminho para salvar o vídeo renderizado (.mp4).
        audio_file (str): Caminho para o arquivo de áudio narrado.
        monotheme (bool, optional): Flag para modo monotemático. Padrão: False.
        thumb_id (int, optional): Índice específico do clipe inicial em thumbVideos. Padrão: 0.
        background_audio_file (str, optional): Caminho para o áudio de fundo instrumental. Padrão: 'backgroundmusic.mp3'.
        videos_folder (str, optional): Pasta contendo os vídeos de fundo. Padrão: 'videosBase/'.
        thumb_folder (str, optional): Pasta contendo vídeos curtos para thumbnail/introdução. Padrão: 'thumbVideos/'.
    """
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Caso exista música de fundo, mixa com o áudio da narração
    if os.path.exists(background_audio_file):
        juntar_audios(audio_file, background_audio_file, audio_file, volume_reduction=10.0)

    if not os.path.exists(videos_folder):
        raise FileNotFoundError(f"Pasta de vídeos base não encontrada: {videos_folder}")
    if not os.path.exists(thumb_folder):
        raise FileNotFoundError(f"Pasta de vídeos de introdução/thumb não encontrada: {thumb_folder}")

    video_files = [f for f in os.listdir(videos_folder) if f.lower().endswith(('.mp4', '.mov', '.mkv', '.avi'))]
    thumb_files = [f for f in os.listdir(thumb_folder) if f.lower().endswith(('.mp4', '.mov', '.mkv', '.avi'))]

    if not video_files:
        raise ValueError(f"Nenhum arquivo de vídeo encontrado em {videos_folder}")
    if not thumb_files:
        raise ValueError(f"Nenhum arquivo de vídeo encontrado em {thumb_folder}")

    random.shuffle(video_files)

    # Selecionar o vídeo inicial da introdução
    if 0 <= thumb_id < len(thumb_files):
        first_video_file = thumb_files[thumb_id]
    else:
        first_video_file = random.choice(thumb_files)

    first_video_path = os.path.join(thumb_folder, first_video_file)

    video_clips = []
    total_duration = 0.0

    # Carregar o primeiro clipe de vídeo (intro/hook)
    first_video_clip = VideoFileClip(first_video_path)
    first_video_duration = random.uniform(3.0, 5.0)

    if first_video_clip.duration > first_video_duration:
        first_video_clip = first_video_clip.subclip(0, first_video_duration)
    elif first_video_clip.duration > 0:
        first_video_clip = first_video_clip.fx(vfx.speedx, first_video_duration / first_video_clip.duration)

    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration

    # Redimensionar para o formato vertical (9:16 - Reels / Shorts / TikTok)
    first_video_clip = first_video_clip.resize((1080, 1920))
    video_clips.append(first_video_clip)
    total_duration += first_video_clip.duration

    # Preencher a duração do áudio com vídeos aleatórios da pasta de conteúdo
    while total_duration < audio_duration:
        video_file = random.choice(video_files)
        video_path = os.path.join(videos_folder, video_file)

        video_clip = VideoFileClip(video_path).resize((1080, 1920))
        remaining_duration = audio_duration - total_duration

        if video_clip.duration > remaining_duration:
            video_clip = video_clip.subclip(0, remaining_duration)

        video_clips.append(video_clip)
        total_duration += video_clip.duration

    # Concatenar todos os clipes de vídeo
    final_video = concatenate_videoclips(video_clips)
    final_video = final_video.set_audio(audio)

    # Renderizar vídeo final com áudio
    final_video.write_videofile(output_file, codec="libx264", fps=24, audio_codec="aac")

    # Liberar recursos
    audio.close()
    for clip in video_clips:
        clip.close()
    final_video.close()

    print(f"Vídeo criado com sucesso em: {output_file}")
