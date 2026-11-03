# Gerador Automatizado de Vídeos Curtos (Shorts / Reels / TikTok)

Este projeto automatiza a criação de vídeos curtos em formato vertical (9:16) a partir de ideias em texto ou roteiros pré-definidos.

O pipeline realiza:
1. **Geração do Roteiro**: Criação do texto e da história utilizando a API da OpenAI.
2. **Narração (TTS)**: Conversão do roteiro em fala com Google Text-to-Speech (`gTTS`) e aceleração sutil da cadência.
3. **Mixagem de Áudio**: Combinação da voz com música de fundo (`backgroundmusic.mp3`) atenuada.
4. **Montagem de Vídeo**: Combinação de vídeos de introdução (`thumbVideos/`) e clipes de fundo satisfatórios (`videosBase/`) dimensionados para resolução vertical (1080x1920).
5. **Sincronização de Legendas**: Detecção de picos de voz e pausas para inserção de legendas dinâmicas e centralizadas.

---

## 📁 Estrutura de Diretórios

```text
├── .env.example            # Exemplo de configuração de variáveis de ambiente
├── .gitignore              # Arquivos e pastas ignorados no versionamento
├── requirements.txt        # Dependências Python do projeto
├── Ideias.txt              # Fila de prompts e temas para gerar vídeos
├── backgroundmusic.mp3     # Música instrumental de fundo
├── main_auto.py            # Pipeline completo automático (da ideia ao vídeo final)
├── bin_manual.py           # Pipeline manual (processa roteiros já existentes em roteiros/)
├── video_generator.py      # Montagem de vídeos e busca de imagens
├── legenda.py              # Sincronização e renderização das legendas no vídeo
├── sincronize_audio.py     # Análise de dBFS e detecção de silêncios/fala
├── concatenate_audio.py    # Mixagem e ajuste de volume de trilha de áudio
├── roteiro.py              # Limpeza, pontuação e pausas do texto
├── diretorio_func.py       # Funções utilitárias auxiliares de texto e busca semântica
├── audios/                 # Diretório temporário dos áudios gerados
├── roteiros/               # Diretório temporário dos roteiros gerados
├── videos/                 # Diretório onde os vídeos finais renderizados são salvos
├── videosBase/             # Vídeos satisfatórios/gameplay para compor o fundo
├── thumbVideos/            # Vídeos curtos usados no início (hook / thumbnail)
└── Imagens/                # Diretório para download de imagens (quando aplicável)
```

---

## ⚙️ Pré-requisitos

1. **Python**: Versão 3.8 ou superior.
2. **FFmpeg**: Necessário para processamento de áudio e vídeo com `moviepy` e `pydub`.
   - **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install ffmpeg`
   - **MacOS**: `brew install ffmpeg`
   - **Windows**: Instalar via Chocolatey (`choco install ffmpeg`) ou baixar no site oficial e adicionar ao `PATH`.
3. **ImageMagick** (opcional/recomendado para certas funcionalidades de texto do MoviePy):
   - Deve estar instalado caso use `TextClip` do MoviePy.

---

## 🚀 Instalação

1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DO_REPOSITORIO>
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   Copie `.env.example` para `.env` ou configure no seu sistema:
   ```bash
   cp .env.example .env
   ```
   Defina sua chave da OpenAI e chaves do Google (caso use busca de imagens):
   ```bash
   export OPENAI_API_KEY="sua_chave_openai"
   # Opcional se for utilizar download_images:
   export GOOGLE_API_KEY="sua_chave_google"
   export GOOGLE_CX="seu_cx_google"
   ```

---

## 🎬 Como Usar

### 1. Preparar os arquivos de mídia
- Coloque vídeos de fundo na pasta `videosBase/` (vídeos curtos, gameplays ou satisfatórios em alta qualidade).
- Coloque clipes curtos de introdução na pasta `thumbVideos/`.
- Adicione sua música instrumental preferida como `backgroundmusic.mp3` na raiz.

### 2. Modo Automático (`main_auto.py`)
Adicione as ideias no arquivo `Ideias.txt`, no formato:
```text
Tema da ideia.opção_estilo*número_parte-id_thumb
```
Exemplo:
```text
Why do cats purr?.0*1-0
The mystery of the Bermuda Triangle.1*0-0
```

Execute o script:
```bash
python main_auto.py
```
O script consumirá a primeira ideia, gerará o roteiro com IA, criará a narração, montará o vídeo com a trilha sonora, adicionará as legendas e salvará o resultado em `videos/`.

### 3. Modo Manual (`bin_manual.py`)
Se você já escreveu ou possui arquivos `.txt` de roteiro prontos, coloque-os dentro da pasta `roteiros/` e execute:
```bash
python bin_manual.py
```

---

## 🛡️ Segurança e Boas Práticas

- Nenhuma chave de API ou credencial está exposta no código-fonte.
- Todas as chaves devem ser configuradas via variáveis de ambiente.
- Arquivos temporários e vídeos renderizados são ignorados pelo `.gitignore`.

---

## 📄 Licença

Este projeto é disponibilizado sob a licença MIT. Sinta-se livre para utilizar, modificar e aprimorar!
