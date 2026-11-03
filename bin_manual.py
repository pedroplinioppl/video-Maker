"""Fluxo de execução para processar roteiros já existentes e produzir o vídeo final."""

import os
from typing import Optional, Tuple
from unidecode import unidecode
from pydub import AudioSegment
from gtts import gTTS

import legenda as legenda_module
import roteiro as roteiro_module
from video_generator import create_video_from_text


def return_roteiro(diretorio: str = "roteiros/") -> Tuple[Optional[str], Optional[str]]:
    """Obtém o primeiro arquivo de texto disponível no diretório informado.

    Args:
        diretorio (str, optional): Diretório com os roteiros. Padrão: 'roteiros/'.

    Returns:
        Tuple[Optional[str], Optional[str]]: Conteúdo do arquivo e nome do arquivo.
    """
    if not os.path.exists(diretorio):
        return None, None

    arquivos = [f for f in os.listdir(diretorio) if f.endswith(".txt")]
    if not arquivos:
        return None, None

    primeiro_arquivo = arquivos[0]
    caminho_arquivo = os.path.join(diretorio, primeiro_arquivo)

    with open(caminho_arquivo, "r", encoding="utf-8", errors="ignore") as arquivo:
        conteudo = arquivo.read()

    return conteudo, primeiro_arquivo


def clean_prompt(string: str) -> str:
    """Higieniza caracteres impróprios para criação de nomes de arquivos no sistema operacional.

    Args:
        string (str): Texto a ser limpo.

    Returns:
        str: Texto seguro para nome de arquivo.
    """
    caracteres_invalidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '!']
    for i, char in enumerate(string):
        if char in caracteres_invalidos:
            return string[:i]
    return string


def main():
    os.makedirs("roteiros", exist_ok=True)
    os.makedirs("audios", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

    # 1. Obter roteiro
    last_response, nome_arquivo = return_roteiro("roteiros/")
    if not nome_arquivo:
        print("Nenhum roteiro encontrado na pasta 'roteiros/'. Adicione um arquivo .txt e tente novamente.")
        return

    print(f"Vídeo a produzir a partir do roteiro: {nome_arquivo}")

    pasta_nome_base = os.path.splitext(nome_arquivo)[0]
    caminho_roteiro = os.path.join("roteiros", nome_arquivo)

    # 2. Corrigir e estruturar texto para áudio
    roteiro, tipo_video = roteiro_module.fix_roteiro(caminho_roteiro)
    texto = f"{pasta_nome_base}! " + roteiro_module.roteiro_as_string(roteiro) + " Subscribe to our channel for more!"

    # 3. Gerar narração TTS
    tts = gTTS(text=texto, lang='en-us')
    arquivo_mp3 = f"audios/{pasta_nome_base}.mp3"
    tts.save(arquivo_mp3)

    # 4. Ajustar velocidade do áudio
    audio = AudioSegment.from_file(arquivo_mp3, format="mp3")
    audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * 1.1)
    })
    audio.export(arquivo_mp3, format="mp3")

    arquivo_mp3_clean = f"audios/Base_{pasta_nome_base}.mp3"
    audio.export(arquivo_mp3_clean, format="mp3")

    # 5. Criar vídeo base
    arquivo_saida = f"videos/{pasta_nome_base}.mp4"
    arquivo_finale = f"videos/{pasta_nome_base}_finale.mp4"

    create_video_from_text(arquivo_saida, arquivo_mp3, thumb_id=tipo_video)

    # 6. Sincronizar e aplicar legendas
    legendas = legenda_module.sincronizar_legendas([texto], arquivo_mp3_clean)
    legenda_module.adicionar_legendas(arquivo_saida, legendas, arquivo_finale)

    # 7. Limpeza dos arquivos intermediários
    if os.path.exists(arquivo_saida):
        os.remove(arquivo_saida)
    if os.path.exists(arquivo_mp3_clean):
        os.remove(arquivo_mp3_clean)
    if os.path.exists(arquivo_finale):
        os.rename(arquivo_finale, arquivo_saida)
    if os.path.exists(caminho_roteiro):
        os.remove(caminho_roteiro)

    print(f"Processo concluído! Vídeo final salvo em {arquivo_saida}")


if __name__ == "__main__":
    main()
