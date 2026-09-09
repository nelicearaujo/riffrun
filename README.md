# Riff Run — Pygame

Protótipo inicial do jogo de plataforma 2D Riff Run.

## O que já existe

- Movimentação com A/D e setas
- Pulo com Espaço/W/seta para cima
- Gravidade e colisões
- Câmera lateral
- Plataformas e buracos
- Mini guitarras colecionáveis
- Sistema de pontuação
- Inimigos simples
- Ataque com clique esquerdo
- Sistema de 3 vidas
- Tela de Game Over
- Objetivo final da fase: recuperar o instrumento
- Tela de vitória
- Tela inicial de seleção de fases
- Desbloqueio progressivo: concluir uma fase libera a próxima
- Progresso de fases salvo localmente em `progress.json`
- Fase de heavy metal em pixel art com tempestade, palco industrial e parallax
- Mapa de campanha dark com rota entre três palcos e nós de seleção
- Obstáculos temáticos: amplificadores, cases, tijolos, vigas e tubulações
- Personagem animado em pixel art: idle, caminhada, pulo, queda, ataque e dano

## Instalação

No terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pygame
```

No Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install pygame
```

## Executar

```bash
python3 main.py
```

## Estrutura

```text
riff_run_pygame/
├── main.py
├── settings.py
├── player.py
├── objects.py
├── level.py
├── README.md
└── assets/
    ├── images/
    └── sounds/
```

## Próximas etapas recomendadas

1. Adicionar música e efeitos sonoros.
2. Criar seleção de personagem.
3. Adicionar checkpoints.
4. Criar as dimensões de AC/DC e Avenged Sevenfold.
