from pydub import AudioSegment

# Carregando os arquivos de áudio
audio1 = "audios\coca_cola_does_bad.mp3"
audio2 = "backgroundmusic.mp3"

def juntar_audios(audio1_path, audio2_path, output_path, volume_reduction):
    # Carregando os arquivos de áudio
    audio1 = AudioSegment.from_mp3(audio1_path)
    audio2 = AudioSegment.from_mp3(audio2_path)

    # Verificando se os dois arquivos têm a mesma taxa de amostragem
    if audio1.frame_rate != audio2.frame_rate:
        audio2 = audio2.set_frame_rate(audio1.frame_rate)

    # Verificando se os dois arquivos têm o mesmo número de canais
    if audio1.channels != audio2.channels:
        audio2 = audio2.set_channels(audio1.channels)

    # Redução do volume do segundo áudio
    audio2 = audio2 - volume_reduction

    # Mixagem dos áudios
    mixed_audio = audio1.overlay(audio2)

    # Salvando o áudio mixado em um novo arquivo
    mixed_audio.export(output_path, format="mp3")
    print("Aúdio feito e salvado em: " + output_path)
