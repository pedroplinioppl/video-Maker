import openai
import re
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from gtts import gTTS

openai.api_key = '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'

def key_word(prompt: str):
    variable_tokens = 4000-len(prompt)
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt="Return the output as if you were doing a search on google images, that is, prioritize a speech that, if I searched and looked at google images, I would know exactly what was happening, for example (Text: 'Pelé is better than ribamar', return : 'Pelé vs ribamar photos'). With this in mind: " + prompt,
        max_tokens=variable_tokens,
        n=1,
        stop=None,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    retorno = response.choices[0].text.strip()
    return retorno.replace('.', '')

def key_theme(prompt: str):
    variable_tokens = 4000-len(prompt)
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt + "Does the text talk about a person or subject? If it's a subject, say the subject, if it's a person, say the person, don't justify yourself just say it.",
        max_tokens=variable_tokens,
        n=1,
        stop=None,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    retorno = response.choices[0].text.strip()
    return retorno.replace('.', '')

def contar_paragrafos(arquivo):
    with open(arquivo, 'r') as f:
        texto = f.read()

    paragrafos = re.split('[.]', texto)
    numero_paragrafos = len(paragrafos)

    return paragrafos, numero_paragrafos #Retorna uma lista separada por '.' , e o número de parágrafos encontrados
