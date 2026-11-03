"""Módulo utilitário para análise de áudio e identificação de quedas de decibéis para sincronização."""

from typing import List, Tuple
from pydub import AudioSegment


def calculate_decibel_level(audio_file: str, step_ms: int = 100, interval_ms: int = 100) -> List[float]:
    """Calcula o nível de decibéis (dBFS) em intervalos de tempo ao longo do áudio.

    Args:
        audio_file (str): Caminho para o arquivo de áudio.
        step_ms (int, optional): Passo da janela em milissegundos. Padrão: 100.
        interval_ms (int, optional): Tamanho do segmento analisado em milissegundos. Padrão: 100.

    Returns:
        List[float]: Lista com os níveis de dBFS de cada segmento.
    """
    sound = AudioSegment.from_file(audio_file)

    # Aumentar o volume do áudio temporariamente para facilitar a detecção dos picos/pausas
    sound += 20

    decibel_levels: List[float] = []
    for i in range(0, len(sound), step_ms):
        segment = sound[i:i + interval_ms]
        decibel = segment.dBFS
        decibel_levels.append(decibel)

    return decibel_levels


def find_drop_points(decibel_levels: List[float], threshold_db: float = -50.0, step_ms: int = 100) -> List[Tuple[int, int]]:
    """Identifica os pontos de fala/silêncio com base no limiar de decibéis.

    Args:
        decibel_levels (List[float]): Lista de valores dBFS calculados.
        threshold_db (float, optional): Limiar em dB para considerar som audível. Padrão: -50.0.
        step_ms (int, optional): Passo em ms correspondente a cada índice da lista. Padrão: 100.

    Returns:
        List[Tuple[int, int]]: Lista de tuplas (início_ms, fim_ms) onde houve atividade sonora.
    """
    drop_points: List[Tuple[int, int]] = []
    start_point = None

    for i, level in enumerate(decibel_levels):
        if level > threshold_db:
            if start_point is None:
                start_point = i * step_ms
        elif start_point is not None:
            end_point = i * step_ms
            drop_points.append((start_point, end_point))
            start_point = None

    if start_point is not None:
        drop_points.append((start_point, len(decibel_levels) * step_ms))

    return drop_points
