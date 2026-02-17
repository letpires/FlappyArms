# Gym Flappy Bird

Jogo estilo Flappy Bird controlado pelos braços: use a webcam e levante os braços para fazer o passarinho voar. Ideal para se movimentar enquanto joga.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-orange)

## Como funciona

- **Câmera**: o jogo usa a webcam para detectar sua pose em tempo real.
- **Controle**: levante um ou os dois braços (pulsos acima dos ombros) para o passarinho dar um “flap” e subir.
- **Calibração**: antes de jogar, é necessário calibrar (tecla **C**) para o jogo reconhecer sua posição inicial.

## Requisitos

- **Python 3.9**
- **Webcam** funcionando
- Boa iluminação para a detecção de pose

## Instalação

1. Clone o repositório (ou baixe os arquivos):

```bash
git clone <url-do-repositorio>
cd flappy-arms
```

2. Crie e ative um ambiente virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# ou: .venv\Scripts\activate   # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Coloque na pasta do projeto (opcional): `logo_image.png` (logo do menu) e `bird_image.png` (passarinho no jogo). Sem elas, o menu e o pássaro usam o desenho padrão.

## Como jogar

1. Execute o jogo:

```bash
python flappy_arms.py
```

2. No menu:
   - Pressione **C** para **calibrar** (fique em pé, braços relaxados).
   - Quando aparecer "CALIBRADO!", pressione **ESPAÇO** para iniciar.

3. Durante o jogo:
   - **Levante os braços** para o passarinho subir e desviar dos canos.
   - **ESC** volta ao menu.

4. No game over:
   - **ESPAÇO** — jogar de novo  
   - **ESC** — voltar ao menu

## Controles (teclado)

| Tecla   | Ação                    |
|---------|-------------------------|
| **C**   | Calibrar (no menu)      |
| **ESPAÇO** | Iniciar / Jogar de novo |
| **ESC** | Sair do jogo / Voltar ao menu |

## Estrutura do projeto

```
flappy-arms/
├── flappy_arms.py    # Código principal do jogo
├── requirements.txt  # Dependências Python
├── logo_image.png   # Logo no menu (opcional)
├── bird_image.png   # Imagem do passarinho no jogo (opcional)
└── README.md
```

## Dependências

- **pygame** — gráficos e loop do jogo  
- **opencv-python** — captura da webcam  
- **mediapipe** — detecção de pose (ombros e pulsos)

## Dicas

- Use um fundo relativamente limpo e boa luz para a câmera.
- Mantenha o corpo (pelo menos ombros e braços) enquadrado na câmera.
- O “flap” é detectado na **subida** dos braços; não precisa ficar com eles levantados o tempo todo.

## Licença

Projeto de uso livre para estudo e diversão.
