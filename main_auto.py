"""Pipeline automatizado para criação de roteiro via OpenAI, geração de narração TTS e edição do vídeo."""

import os
from typing import List, Optional
import openai
from unidecode import unidecode
from pydub import AudioSegment
from gtts import gTTS

import legenda as legenda_module
import roteiro as roteiro_module
from video_generator import create_video_from_text


def get_idea(nome_arquivo: str) -> Optional[List]:
    """Lê a primeira ideia do arquivo de ideias, extrai metadados e remove a linha processada.

    Formato esperado da linha:
        Tema ou Prompt.opção_prompt*id_thumb-numero

    Args:
        nome_arquivo (str): Caminho para o arquivo contendo a fila de ideias.

    Returns:
        Optional[List]: [string_tema, indice_opcao, numero_asterisco, numero_hifen] ou None se vazio.
    """
    if not os.path.exists(nome_arquivo):
        return None

    with open(nome_arquivo, 'r+', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines()
        numero_asterisco = 0
        numero_ponto = 0
        numero_hifen = 0

        if not linhas:
            return None

        primeira_linha = linhas[0].strip()
        string_retornada = primeira_linha.split('.', 1)[0]

        # Extrai número após '.' (índice da opção do prompt)
        ponto_index = primeira_linha.find('.')
        if ponto_index != -1:
            numero_str = primeira_linha[ponto_index + 1:].strip()
            # Pega apenas os dígitos iniciais
            digitos = ''
            for c in numero_str:
                if c.isdigit():
                    digitos += c
                else:
                    break
            if digitos:
                numero_ponto = int(digitos)

        # Extrai número após '*'
        asterisco_index = primeira_linha.find('*')
        if asterisco_index != -1 and asterisco_index + 1 < len(primeira_linha):
            prox_char = primeira_linha[asterisco_index + 1]
            if prox_char.isdigit():
                numero_asterisco = int(prox_char)

        # Extrai número após '-'
        hifen_index = primeira_linha.find('-')
        if hifen_index != -1 and hifen_index + 1 < len(primeira_linha):
            prox_char = primeira_linha[hifen_index + 1]
            if prox_char.isdigit():
                numero_hifen = int(prox_char)

        # Atualiza o arquivo sem a linha atual
        restante_linhas = linhas[1:]
        arquivo.seek(0)
        arquivo.truncate()
        for linha in restante_linhas:
            arquivo.write(linha)

        return [string_retornada, numero_ponto, numero_asterisco, numero_hifen]


def clean_prompt(string: str) -> str:
    """Higieniza caracteres para gerar nomes de arquivos válidos no sistema operacional.

    Args:
        string (str): Texto original.

    Returns:
        str: Texto truncado antes do primeiro caractere inválido.
    """
    caracteres_invalidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '!']
    for i, char in enumerate(string):
        if char in caracteres_invalidos:
            return string[:i]
    return string


def main():
    # 0. Garante que os diretórios necessários existem
    os.makedirs("roteiros", exist_ok=True)
    os.makedirs("audios", exist_ok=True)
    os.makedirs("videos", exist_ok=True)
    os.makedirs("thumbVideos", exist_ok=True)
    os.makedirs("videosBase", exist_ok=True)

    # Configuração de credenciais da OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente OPENAI_API_KEY não foi configurada. Defina-a antes de rodar.")
    openai.api_key = api_key

    # PARTE 1 - GERAR ROTEIRO COM IA
    caminho_ideias = "Ideias.txt" if os.path.exists("Ideias.txt") else "roteiros/Ideias.txt"
    ideas_prompt = get_idea(caminho_ideias)
    if ideas_prompt is None:
        print(f"Nenhuma ideia encontrada em '{caminho_ideias}'. Adicione ideias para gerar vídeos.")
        return

    options = [
        " answer it charismatically as a video that has 1 minute duration or less, make it relaxed (return only raw text, no specifications)",
        " in 1 minute video or less, tell like it was a self story, with some big plot at final"
    ]

    opcao_idx = ideas_prompt[1] if ideas_prompt[1] < len(options) else 0
    prompt_texto = ideas_prompt[0] + options[opcao_idx]
    variable_tokens = max(150, 4000 - len(prompt_texto))

    print(f"Vídeo a fazer: {ideas_prompt[0]}")
    print(f"Opção de estilo: {options[opcao_idx]}")

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt_texto,
        max_tokens=variable_tokens,
        n=1,
        stop=None,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    last_response = response.choices[0].text.strip()

    option_suffix = f"_{ideas_prompt[2]}" if ideas_prompt[2] > 1 else ""
    pasta_nome_base = unidecode(f"{clean_prompt(ideas_prompt[0]).lower()}{option_suffix}").strip().replace(' ', '_')

    caminho_roteiro = f"roteiros/{pasta_nome_base}.txt"
    with open(caminho_roteiro, 'w', encoding='utf-8') as arquivo:
        arquivo.write(unidecode(last_response))

    print(f"Roteiro gravado em: {caminho_roteiro}")

    # PARTE 2 - TRANSFORMAR ROTEIRO EM ÁUDIO
    roteiro, _ = roteiro_module.fix_roteiro(caminho_roteiro)
    parte_text = f" part {ideas_prompt[2]}!" if ideas_prompt[2] > 1 else ""
    texto = f"{ideas_prompt[0]}{parte_text} " + roteiro_module.roteiro_as_string(roteiro) + " Subscribe to our channel for more!"

    tts = gTTS(text=texto, lang='en-us')
    arquivo_mp3 = f"audios/{pasta_nome_base}.mp3"
    tts.save(arquivo_mp3)

    audio = AudioSegment.from_file(arquivo_mp3, format="mp3")
    speed_aud = 1.2 if len(audio) > 70 * 1000 else 1.1

    audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * speed_aud)
    })
    audio.export(arquivo_mp3, format="mp3")

    arquivo_mp3_clean = f"audios/Base_{pasta_nome_base}.mp3"
    audio.export(arquivo_mp3_clean, format="mp3")

    # PARTE 3 - RENDERIZAR O VÍDEO
    arquivo_saida = f"videos/{pasta_nome_base}.mp4"
    arquivo_finale = f"videos/{pasta_nome_base}_finale.mp4"

    create_video_from_text(arquivo_saida, arquivo_mp3, thumb_id=ideas_prompt[3])

    # PARTE 4 - APLICAR LEGENDAS
    legendas = legenda_module.sincronizar_legendas([texto], arquivo_mp3_clean)
    legenda_module.adicionar_legendas(arquivo_saida, legendas, arquivo_finale)

    if os.path.exists(arquivo_saida):
        os.remove(arquivo_saida)
    if os.path.exists(arquivo_mp3_clean):
        os.remove(arquivo_mp3_clean)
    if os.path.exists(arquivo_finale):
        os.rename(arquivo_finale, arquivo_saida)

    print(f"Vídeo com legenda finalizado em: {arquivo_saida}")


if __name__ == "__main__":
    main()
