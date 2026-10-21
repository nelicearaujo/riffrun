# Documento Técnico Coletivo do Jogo

**Jogo:** Riff Run  
**Versão documentada:** estado do diretório de trabalho em 20/10/2026  
**Repositório:** https://github.com/nelicearaujo/riffrun  
**Commit-base identificado:** `6975e69` — “Adiciona jogo Riff Run com mapa dark e fases progressivas”  

> Este documento descreve o que foi localizado no código-fonte e validado no ambiente disponível. Informações que não aparecem no repositório, como integrantes, divisão de tarefas, cronograma oficial de sprints e vídeo de demonstração, estão identificadas como pendentes de preenchimento pela equipe.

## 1. Identificação do projeto

### 1.1 Caracterização

| Item | Descrição | Situação |
|---|---|---|
| Nome | Riff Run | Implementado |
| Gênero | Plataforma 2D com ação, exploração lateral e coleta de itens | Implementado |
| Motor/biblioteca | Pygame 2.6.1, executado sobre SDL | Validado no ambiente |
| Linguagem | Python 3.9.6 | Validado no ambiente |
| Persistência | Arquivo local `progress.json` em formato JSON | Implementada |
| Resolução | 1280 × 720 pixels | Implementada |
| Taxa de atualização | 60 FPS | Configurada em `settings.py` |
| Controle de versão | Git, repositório hospedado no GitHub | Identificado |

### 1.2 Integrantes e responsabilidades

O código e o histórico disponível não registram a composição completa da equipe nem a divisão individual das atividades. A tabela abaixo deve ser preenchida coletivamente antes da entrega, usando os nomes reais e as evidências correspondentes.

| Integrante | Responsabilidades realizadas | Componentes relacionados | Evidência |
|---|---|---|---|
| `[nome do integrante 1]` | `[descrever atividades efetivamente realizadas]` | `[arquivos, sistemas ou telas]` | `[commit, tarefa, branch ou outra evidência]` |
| `[nome do integrante 2]` | `[descrever atividades efetivamente realizadas]` | `[arquivos, sistemas ou telas]` | `[commit, tarefa, branch ou outra evidência]` |
| `[nome do integrante 3]` | `[descrever atividades efetivamente realizadas]` | `[arquivos, sistemas ou telas]` | `[commit, tarefa, branch ou outra evidência]` |
| `[nome do integrante 4, se houver]` | `[descrever atividades efetivamente realizadas]` | `[arquivos, sistemas ou telas]` | `[commit, tarefa, branch ou outra evidência]` |

O commit-base foi registrado no Git como autoria de `nelicearaujo`; esse dado é apenas metadado do repositório e não substitui o registro das contribuições individuais da equipe.

### 1.3 Cronograma de sprints

O cronograma fornecido pelo professor não está presente no repositório. Portanto, não é possível afirmar quais tarefas pertencem a cada sprint sem consultar o material oficial. A equipe deve substituir a tabela abaixo pelo cronograma real, mantendo a distinção entre concluído, parcial e pendente.

| Sprint oficial | Tarefas previstas | Entregas efetivamente realizadas | Pendências |
|---|---|---|---|
| `[Sprint 1]` | `[copiar do cronograma do professor]` | `[registrar o que foi entregue]` | `[registrar o que ficou pendente]` |
| `[Sprint 2]` | `[copiar do cronograma do professor]` | `[registrar o que foi entregue]` | `[registrar o que ficou pendente]` |
| `[Sprint 3]` | `[copiar do cronograma do professor]` | `[registrar o que foi entregue]` | `[registrar o que ficou pendente]` |
| `[outras sprints]` | `[copiar do cronograma do professor]` | `[registrar o que foi entregue]` | `[registrar o que ficou pendente]` |

## 2. Visão geral e regras do jogo

### 2.1 Objetivo

O jogador controla um vocalista em um palco industrial de temática heavy metal. O objetivo é atravessar a fase lateral, superar buracos, plataformas e inimigos, coletar mini guitarras para aumentar a pontuação e alcançar o instrumento final localizado no fim do percurso. Ao tocar no instrumento final, a fase é concluída.

O jogo possui um mapa de campanha com três nós. A Fase 1 e a Fase 2 possuem construções de nível próprias. A Fase 3 pode ser desbloqueada e selecionada quando a progressão permite, mas ainda reutiliza a construção da Fase 1; por isso, seu conteúdo exclusivo está **parcialmente implementado**.

### 2.2 Mecânicas implementadas

| Funcionalidade | Descrição | Situação |
|---|---|---|
| Movimentação | Movimento horizontal com velocidade constante, usando A/D ou setas esquerda/direita | Implementada |
| Pulo | Pulo condicionado ao personagem estar sobre uma plataforma, usando Espaço, W ou seta para cima | Implementado |
| Gravidade | Aplicação de aceleração vertical com limite de velocidade de queda | Implementada |
| Colisão com plataformas | Ajuste separado de colisões horizontais e verticais | Implementada |
| Câmera lateral | Câmera acompanha o personagem e é limitada à largura do nível | Implementada |
| Buracos | Trechos sem chão fazem o personagem cair; a queda causa dano e reposiciona o personagem | Implementada |
| Coleta | Mini guitarras desaparecem ao serem tocadas e somam um ponto | Implementada |
| Pontuação | HUD mostra a pontuação no formato `RIFFS pontos/15` | Implementada |
| Inimigos | Inimigos patrulham intervalos horizontais definidos por fase | Implementada |
| Ataque | Clique esquerdo cria uma área de ataque temporária na direção do personagem e elimina inimigos atingidos | Implementado |
| Vida/energia | O personagem inicia com 3 unidades de energia e recebe invulnerabilidade temporária após dano | Implementada |
| Game Over | Ao chegar a zero de energia, a tela de derrota é exibida | Implementado |
| Vitória | Colisão com o instrumento final exibe a tela de conclusão | Implementada |
| Repetição | Tecla R reinicia a fase após vitória ou derrota | Implementada |
| Mapa de campanha | Seleção por teclado, mouse ou teclas 1, 2 e 3 | Implementada |
| Desbloqueio | Concluir uma fase libera a próxima e grava o progresso localmente | Implementado |
| Áudio | Não foram encontrados arquivos de áudio funcionais nem chamadas de reprodução | Não implementado |
| Checkpoints | Não foram encontrados checkpoints intermediários | Não implementado |
| Seleção de personagem | Não foi encontrada tela ou sistema de seleção | Não implementado |

### 2.3 Entradas do jogador

| Entrada | Ação |
|---|---|
| A ou seta esquerda | Mover para a esquerda |
| D ou seta direita | Mover para a direita |
| Espaço, W ou seta para cima | Pular quando estiver no chão |
| Clique esquerdo durante a fase | Atacar |
| Setas, A/D ou W/S no mapa | Alterar fase selecionada |
| Enter ou Espaço no mapa | Iniciar a fase selecionada, se desbloqueada |
| Teclas 1, 2 e 3 no mapa | Selecionar e iniciar diretamente uma fase desbloqueada |
| Esc | Sair do jogo no mapa ou voltar ao mapa durante a fase |
| R | Reiniciar após vitória ou Game Over |
| M ou Enter após vitória | Voltar ao mapa |

### 2.4 Regras e resultados observáveis

1. O personagem começa com 3 unidades de energia.
2. O contato com um inimigo reduz uma unidade, desde que a invulnerabilidade não esteja ativa.
3. Após receber dano, o personagem fica invulnerável por 80 frames e recebe impulso vertical para cima.
4. Cair abaixo da tela causa dano e reposiciona o personagem em `(120, 500)`.
5. O ataque só pode ser iniciado quando o contador de ataque está zerado; a área de dano fica ativa durante uma janela intermediária da animação.
6. Cada mini guitarra coletada soma 1 ponto e não reaparece durante a execução atual da fase.
7. O jogador não precisa coletar todas as 15 guitarras para alcançar a vitória; a condição de vitória implementada é a colisão com o instrumento final.
8. Ao alcançar o instrumento final, a fase fica concluída e a próxima fase é liberada, até o limite de três fases.
9. O encerramento pelo evento de janela termina o laço principal e chama `pygame.quit()`.

## 3. Arquitetura e organização do código

### 3.1 Arquivos e módulos

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Inicialização do Pygame, criação da janela, carregamento de progresso, menus, loop principal, tratamento de eventos, atualização, colisões, HUD, vitória, Game Over e encerramento |
| `settings.py` | Constantes globais: resolução, FPS, gravidade, velocidade, força do pulo, largura do nível e posição do chão |
| `player.py` | Classe `Player`, entrada do personagem, movimento, gravidade, colisão, ataque, dano, invulnerabilidade, animação, desenho e carregamento da spritesheet |
| `objects.py` | Classes visuais e interativas `Platform`, `Guitar`, `Enemy` e `GoalInstrument`, além de funções auxiliares de desenho |
| `level.py` | Classe `Level`, construção das fases, plataformas, guitarras, inimigos, atualização dos inimigos e desenho dos objetos |
| `progress.json` | Estado local do número de fases desbloqueadas |
| `tests/test_game.py` | Testes automatizados das entidades, construção das fases e regras centrais do jogador |
| `assets/images/` | Fundo da Fase 1, fundo da Fase 2 e spritesheet do personagem |
| `assets/sounds/` | Diretório reservado, sem arquivos sonoros funcionais identificados |
| `README.md` | Descrição do protótipo, instalação, execução, estrutura e próximas etapas |

### 3.2 Interação entre os componentes

O módulo `main.py` instancia `Player` e `Level`. A cada frame, o personagem recebe as plataformas do nível para atualizar seu movimento e suas colisões. O nível atualiza os inimigos, enquanto o laço principal verifica coleta de guitarras, ataques contra inimigos, dano por contato, queda e colisão com o objetivo. Depois da atualização, o nível e o personagem são desenhados com deslocamento da câmera.

O `Level` usa as classes de `objects.py` para compor as fases. `Player` usa a spritesheet de `assets/images/` e as constantes de `settings.py`. O mapa e o sistema de progressão ficam em `main.py`; a leitura e a gravação do estado são feitas em `progress.json`.

### 3.3 Estados principais

O jogo utiliza a variável `screen_mode`, com os estados `menu` e `playing`. Durante `playing`, as flags `victory` e `game_over` impedem novas atualizações quando uma condição terminal é atingida. A função `reset_game` cria um novo `Player` e um novo `Level` para a fase selecionada.

## 4. Linguagem, bibliotecas e ambiente

Python é uma linguagem de alto nível, interpretada, de tipagem dinâmica e com suporte a orientação a objetos. No projeto, ela organiza o jogo em módulos e classes, facilitando a separação entre o laço principal, o personagem, os objetos e a construção dos níveis.

O jogo utiliza:

- **Pygame 2.6.1:** janela, eventos, teclado, mouse, relógio, superfícies, imagens, retângulos de colisão, desenho 2D e sprites.
- **SDL, por meio do Pygame:** camada de janela e entrada utilizada pelo motor.
- **`pathlib`:** construção de caminhos portáveis para os assets e para `progress.json`.
- **`json`:** serialização e leitura do progresso local.
- **`os` e `sys`:** leitura da variável opcional de captura de tela e encerramento do programa.
- **Git/GitHub:** versionamento e distribuição do código.

O ambiente validado possui Python 3.9.6 em `.venv` e Pygame 2.6.1. A instalação prevista está documentada no `README.md` com criação de ambiente virtual e instalação de Pygame.

## 5. Persistência de dados

### 5.1 Informação armazenada

O arquivo `progress.json` armazena o campo `unlocked_phases`, que indica quantas fases estão desbloqueadas. No estado observado do projeto, o arquivo contém:

```json
{
  "unlocked_phases": 3
}
```

O valor é limitado entre 1 e 3 ao ser carregado. Quando uma fase é concluída, o jogo grava o maior valor entre o progresso atual e a próxima fase liberada.

### 5.2 Justificativa técnica

A persistência local é necessária para que o desbloqueio das fases permaneça entre execuções, sem exigir banco de dados, servidor ou conta de usuário. JSON é suficiente para esse único número e mantém a implementação simples, legível e compatível com um protótipo desktop.

Pontuação, vida, estado dos inimigos e guitarras coletadas não são persistidos: eles pertencem à execução atual e são reiniciados ao iniciar ou repetir uma fase.

### 5.3 Limitações observadas

Se a leitura do arquivo falhar, a função de carregamento retorna 2 como valor padrão. Esse comportamento mantém o jogo executável, mas pode liberar a Fase 2 mesmo quando não existe progresso válido. Essa decisão deve ser revisada caso o requisito seja iniciar sempre com apenas a Fase 1 desbloqueada.

## 6. Fluxo de execução

1. O programa importa os módulos e inicializa o Pygame.
2. A janela de 1280 × 720 pixels, as fontes e o relógio de 60 FPS são criados.
3. Os fundos são carregados a partir de `assets/images/`; se um carregamento falhar, o jogo usa uma cor de fundo alternativa.
4. O progresso é lido de `progress.json`.
5. O jogo começa no mapa de campanha, com a fase selecionada e os nós desbloqueados desenhados.
6. O jogador navega no mapa e inicia uma fase desbloqueada.
7. `reset_game` cria o jogador e a fase. A fase constrói suas plataformas, coletáveis, inimigos e objetivo.
8. A cada frame, os eventos são processados, o personagem e os inimigos são atualizados, e as colisões são avaliadas.
9. A câmera acompanha o personagem; o cenário, o nível, o personagem e o HUD são desenhados.
10. Ao alcançar o objetivo, a tela de vitória é exibida e o progresso é salvo. Ao perder toda a energia, a tela de Game Over é exibida.
11. O jogador pode reiniciar a fase, voltar ao mapa ou encerrar pelo evento de saída/tecla Esc.
12. No encerramento, o Pygame é finalizado com `pygame.quit()`.

## 7. Testes e qualidade

### 7.1 Testes executados

Os testes automatizados estão em `tests/test_game.py` e foram executados a partir da raiz do projeto (`/Users/nelic/Downloads/riff_run_pygame`) com o interpretador `.venv/bin/python`. A suíte usa `unittest` e configura o Pygame em modo headless (`SDL_VIDEODRIVER=dummy` e `SDL_AUDIODRIVER=dummy`), sem abrir uma janela durante a execução.

| Teste | Procedimento | Resultado observado | Situação |
|---|---|---|---|
| Compilação dos módulos | Execução de `py_compile` para `main.py`, `level.py`, `player.py`, `objects.py` e `settings.py` usando o Python configurado do projeto | Nenhum erro de sintaxe | Aprovado |
| Inicialização headless | Execução de `main.py` com `SDL_VIDEODRIVER=dummy` e `SDL_AUDIODRIVER=dummy` | O Pygame inicializou e encerrou com sucesso após gerar captura | Aprovado |
| Captura da tela inicial | Uso da variável `RIFF_RUN_SCREENSHOT` | Arquivo PNG de 1280 × 720 foi gerado; o mapa de campanha foi visualizado | Aprovado |
| Leitura do progresso | Inicialização com `progress.json` contendo três fases desbloqueadas | O menu exibiu os três nós como disponíveis | Aprovado no cenário observado |
| Testes automatizados | Execução de `.venv/bin/python -m unittest discover -s tests -v` na raiz do projeto | 9 testes aprovados em `tests/test_game.py` | Aprovado |
| Jogabilidade manual completa | Movimento, pulo, coleta, ataque, dano, Game Over, vitória e reinício em execução interativa | Não há registro automatizado ou evidência anexada de todos esses cenários | Ainda não testado formalmente |
| Persistência após vitória | Concluir uma fase e reabrir o jogo | Não há registro de execução desse cenário no repositório | Ainda não testado formalmente |

### 7.2 Problemas e pendências identificados

- A Fase 3 aparece no mapa e pode ser desbloqueada, mas `Level` só possui uma construção específica para a Fase 2; a Fase 3 cai no fluxo padrão da Fase 1.
- O `README.md` registra ausência de música e efeitos sonoros, seleção de personagem e checkpoints como próximas etapas.
- A suíte automatizada cobre regras centrais dos módulos de objetos, fases e jogador; ainda não cobre o loop completo de `main.py` nem uma jogabilidade interativa ponta a ponta.
- Não foi localizada evidência versionada de vídeo de demonstração, roteiro de testes ou relatório de bugs.
- A função de carregamento de progresso usa 2 como fallback em caso de erro de leitura, comportamento que pode ser incompatível com a regra de começar pela Fase 1.

### 7.3 Próximos testes recomendados

1. Testar manualmente cada entrada do menu e confirmar que fases bloqueadas não iniciam.
2. Confirmar que A/D, setas, Espaço, W, clique esquerdo, Esc, R e M produzem os resultados esperados.
3. Coletar todas as 15 guitarras de cada fase e confirmar a contagem do HUD.
4. Testar contato com inimigo, invulnerabilidade, queda em buraco, três danos e Game Over.
5. Derrotar inimigos com ataques voltados para a esquerda e para a direita.
6. Concluir as Fases 1 e 2, reiniciar o programa e confirmar a persistência do desbloqueio.
7. Testar arquivo `progress.json` ausente, inválido e somente leitura, registrando o comportamento desejado.
8. Criar testes específicos para a Fase 3 quando seu conteúdo próprio for implementado.

## 8. Contribuições individuais e integração

### 8.1 Componentes integrados

O estado atual integra os seguintes componentes:

- `main.py` coordena eventos, estados, colisões e telas.
- `player.py` fornece a entidade jogável e suas animações.
- `level.py` constrói os percursos da Fase 1 e da Fase 2.
- `objects.py` fornece plataformas, coletáveis, inimigos e objetivo.
- `settings.py` centraliza parâmetros físicos e de tela.
- `assets/images/` fornece os elementos visuais externos.
- `progress.json` mantém o desbloqueio entre execuções.

### 8.2 Registro individual

Não é tecnicamente seguro atribuir cada componente a uma pessoa somente a partir do código atual. Para atender à exigência de contribuição individual, a equipe deve completar esta tabela com base no histórico do Git, nas tarefas do professor e no relato de cada integrante.

| Integrante | Atividade específica | Decisão técnica ou resultado | Evidência para anexar |
|---|---|---|---|
| `[nome]` | `[ex.: implementação do movimento e colisão]` | `[descrever decisão efetivamente tomada]` | `[commit/arquivo/tarefa]` |
| `[nome]` | `[ex.: criação dos objetos e obstáculos]` | `[descrever decisão efetivamente tomada]` | `[commit/arquivo/tarefa]` |
| `[nome]` | `[ex.: menu, mapa e persistência]` | `[descrever decisão efetivamente tomada]` | `[commit/arquivo/tarefa]` |
| `[nome]` | `[ex.: arte, testes ou integração]` | `[descrever decisão efetivamente tomada]` | `[commit/arquivo/tarefa]` |

### 8.3 Integração

A integração ocorre no laço principal: `main.py` fornece as plataformas ao jogador, atualiza o nível, verifica as interações entre as entidades e chama os métodos de desenho. O uso de retângulos (`pygame.Rect`) como representação das hitboxes mantém a comunicação entre os módulos simples e previsível.

## 9. Entregas, evidências e pendências

### 9.1 Situação das funcionalidades

| Item | Estado atual | Evidência |
|---|---|---|
| Protótipo jogável de plataforma | Implementado | `main.py`, `player.py`, `level.py` |
| Fase 1 heavy metal | Implementada | `Level.build_level` e `metal_storm_stage.png` |
| Fase 2 com tema de estrada/AC/DC | Implementada parcialmente/funcional no código | `Level.build_highway_level` e `visualFase2.jpeg` |
| Mapa de campanha com três nós | Implementado | `draw_map_menu` em `main.py` |
| Desbloqueio local | Implementado | `progress.json`, `load_unlocked_phases` e `save_unlocked_phases` |
| Fase 3 com conteúdo próprio | Pendente | O nível ainda usa o fluxo padrão da Fase 1 |
| Música e efeitos sonoros | Pendente | `assets/sounds/` não contém arquivos funcionais |
| Checkpoints | Pendente | Não há sistema correspondente no código |
| Seleção de personagem | Pendente | Não há sistema correspondente no código |
| Testes automatizados | Implementado parcialmente | `tests/test_game.py` cobre objetos, construção das fases e regras centrais do jogador; o loop completo ainda depende de teste manual |

### 9.2 Links e materiais

- **Repositório:** https://github.com/nelicearaujo/riffrun
- **Vídeo de demonstração:** `[inserir link real; não localizado no repositório]`
- **Cronograma de sprints:** `[inserir link ou referência ao arquivo fornecido pelo professor]`
- **Versão entregue:** `[inserir tag, commit ou data da versão final efetivamente submetida]`

As imagens existentes no projeto são evidências de recursos visuais implementados. A captura de inicialização realizada durante a validação deve ser anexada somente se a equipe desejar utilizá-la como evidência adicional e se ela for disponibilizada junto da entrega.

## 10. Utilização de inteligência artificial

### 10.1 Declaração referente a este documento

Foi utilizada assistência de inteligência artificial para inspecionar a organização do repositório, sintetizar o funcionamento observável do código, estruturar este documento e apoiar a validação de compilação e inicialização. A IA não substitui a revisão da equipe: os integrantes devem conferir cada descrição no código, executar os testes interativos pendentes e corrigir qualquer informação que não corresponda ao trabalho efetivamente realizado.

### 10.2 Revisão humana e validações

Os resultados documentados foram confrontados com os arquivos do projeto, o estado do Git e uma execução headless do jogo. A equipe deve acrescentar, antes da submissão, a declaração sobre qualquer uso anterior de IA na criação, implementação, arte, testes ou depuração do jogo, indicando:

- qual ferramenta foi utilizada;
- em qual etapa foi utilizada;
- quais sugestões foram aceitas, adaptadas ou rejeitadas;
- quais testes e revisões humanas confirmaram o funcionamento;
- quais partes foram produzidas integralmente pela equipe.

Não devem ser atribuídas à IA funcionalidades que não estejam presentes no código nem testes que não tenham sido executados.

## 11. Conclusão do estado atual

Riff Run é um protótipo funcional de plataforma 2D em Pygame, com mapa de campanha, duas construções de fase, movimentação, pulo, colisão, coletáveis, inimigos, ataque, energia, telas de vitória/Game Over, persistência do desbloqueio e uma suíte automatizada parcial. As principais pendências funcionais são a ausência de conteúdo próprio para a Fase 3, além de áudio, checkpoints, seleção de personagem e testes interativos ponta a ponta. O documento só deve ser considerado definitivo depois que a equipe preencher os integrantes, as responsabilidades, o cronograma de sprints, as evidências individuais e os links que não estão disponíveis no repositório.
