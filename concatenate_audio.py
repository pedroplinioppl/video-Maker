"""Módulo auxiliar para manipulação e concatenação/mixagem de faixas de áudio."""

import os
from pydub import AudioSegment


def juntar_audios(
    audio1_path: str,
    audio2_path: str,
    output_path: str,
    volume_reduction: float = 10.0
) -> None:
    """Mixa dois arquivos de áudio (por exemplo, voz e música de fundo).

    Args:
        audio1_path (str): Caminho para o áudio principal (voz/narração).
        audio2_path (str): Caminho para o áudio de fundo (trilha sonora).
        output_path (str): Caminho onde o arquivo resultante será exportado.
        volume_reduction (float, optional): Quantidade de decibéis (dB) a serem reduzidos da trilha de fundo. Padrão: 10.0.
    """
    if not os.path.exists(audio1_path):
        raise FileNotFoundError(f"Arquivo de áudio principal não encontrado: {audio1_path}")
    if not os.path.exists(audio2_path):
        raise FileNotFoundError(f"Arquivo de áudio de fundo não encontrado: {audio2_path}")

    # Garante que o diretório de destino existe
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Carrega os arquivos de áudio
    audio1 = AudioSegment.from_file(audio1_path)
    audio2 = AudioSegment.from_file(audio2_path)

    # Ajusta a taxa de amostragem caso divirjam
    if audio1.frame_rate != audio2.frame_rate:
        audio2 = audio2.set_frame_rate(audio1.frame_rate)

    # Ajusta os canais caso divirjam
    if audio1.channels != audio2.channels:
        audio2 = audio2.set_channels(audio1.channels)

    # Reduz o volume da música de fundo para dar destaque à narração
    audio2 = audio2 - volume_reduction

    # Faz o loop da música de fundo caso ela seja mais curta que a narração
    if len(audio2) < len(audio1):
        loop_count = (len(audio1) // len(audio2)) + 1
        audio2 = audio2 * loop_count

    # Corta a música de fundo para a duração da narração
    audio2 = audio2[:len(audio1)]

    # Realiza a sobreposição (mixagem)
    mixed_audio = audio1.overlay(audio2)

    # Exporta o resultado
    mixed_audio.export(output_path, format="mp3")
    print(f"Áudio final mixado com sucesso em: {output_path}")
