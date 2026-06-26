import pygame
import sys
import random
import math
import os

pygame.init()

# =========================
# MÚSICA (OST)
# =========================
pygame.mixer.init()

try:
    pygame.mixer.music.load("ost-fodona.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except:
    print("Arquivos de áudio não encontrados. Rodando sem som.")

volume_normal = 0.3
volume_pause = 0.1

# =========================
# SONS 🔊
# =========================
som_dash = pygame.mixer.Sound("dash.mp3") if os.path.exists("dash.mp3") else None
som_morte = pygame.mixer.Sound("death.mp3") if os.path.exists("death.mp3") else None
som_pulo1 = pygame.mixer.Sound("jump-1.mp3") if os.path.exists("jump-1.mp3") else None
som_pulo2 = pygame.mixer.Sound("jump-2.mp3") if os.path.exists("jump-2.mp3") else None
som_queda = pygame.mixer.Sound("land.mp3") if os.path.exists("land.mp3") else None
som_moeda = pygame.mixer.Sound("coin.mp3") if os.path.exists("coin.mp3") else None
som_desabamento = pygame.mixer.Sound("crumble.mp3") if os.path.exists("crumble.mp3") else None
som_vitoria_fase = pygame.mixer.Sound("level-clear.mp3") if os.path.exists("level-clear.mp3") else None

def tocar_som(som):
    if som: som.play()

# CONFIG
LARGURA, ALTURA = 900, 500
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Celeste Fan Game")
clock = pygame.time.Clock()

# CORES
PRETO = (25, 15, 35)         
BRANCO = (225, 215, 255)     
ROXO_ESPINHO = (180, 150, 230) 
AZUL = (80, 180, 255)
ROXO = (150, 80, 255)
AMARELO = (255, 220, 100)
OURO = (255, 200, 50)

# CORES DO PARALLAX (Estilo Celeste)
COR_FUNDO_CEU = (35, 25, 50)
COR_MONTANHA_DISTANTE = (45, 35, 65)
COR_MONTANHA_MEDIA = (60, 45, 85)
COR_COLINA_PROXIMA = (80, 60, 110)

# HUD
fonte = pygame.font.SysFont("arial", 25)
mortes = 0
tempo_inicio = pygame.time.get_ticks()

# PAUSE / STATUS / SISTEMA DE FASES
pausado = False
venceu = False
fase_atual = 1  

# TRANSICÃO DE FASE
transicao_fase_alvo = None
transicao_alpha = 0
transicao_estado = "parado"  # "parado", "escurecendo", "clareando"

# PLAYER
player = pygame.Rect(50, 300, 24, 24)
player_float_x = float(player.x)
player_float_y = float(player.y)

vel_x = 0; vel_y = 0
gravidade = 0.55
forca_pulo = -10.5          
forca_segundo_pulo = -8.5    
aceleracao = 0.6; friccao = 0.4; vel_max = 5.5

# DASH
dash_speed = 13; dash_timer = 0; dash_cd = 30; dash_cd_timer = 0
dashing = False; dash_dir = (0, 0); pode_dash = True

# DOUBLE JUMP
pulos_max = 2; pulos_restantes = 2

# CAMERA
camera_x = 0; camera_y = 0; camera_suave = 0.1

# SHAKE
shake_timer = 0; shake_int = 5

# CONTROLE CHÃO
no_chao = False
no_chao_anterior = False

# FX
particulas = []; trail = []
vento = []

def particula(x, y, cor):
    for _ in range(8):
        particulas.append([x, y,
            random.uniform(-2, 2),
            random.uniform(-2, 2),
            random.randint(3, 6), cor])

def poeira_impacto(x, y, intensidade):
    total_particulas = int(10 + intensidade * 2)
    for _ in range(total_particulas):
        particulas.append([
            x, y,
            random.uniform(-3, 3),
            random.uniform(-1, -intensidade/2),
            random.randint(4, 9),
            (200, 200, 250)
        ])

def vento_dash(x, y, direcao):
    for _ in range(6):
        ang = math.atan2(direcao[1], direcao[0])
        vento.append([
            x, y,
            math.cos(ang)*random.uniform(2, 6),
            math.sin(ang)*random.uniform(2, 6),
            random.randint(10, 20),
            random.randint(6, 12)
        ])

# NEVE
neve = []
for _ in range(100):
    neve.append([random.randint(0, 1200), random.randint(0, 600),
                 random.uniform(1.5, 3.5), random.randint(2, 3)])

# ==========================================
# DESIGN DAS FASES
# ==========================================

# --- FASE 1 ---
plataformas_fase1 = [
    pygame.Rect(0, 400, 130, 150),     
    pygame.Rect(130, 330, 190, 220),   
    pygame.Rect(320, 420, 140, 130),   
    pygame.Rect(460, 210, 210, 340),   
    pygame.Rect(670, 420, 180, 130),   
    pygame.Rect(850, 150, 250, 400)    
]
espinhos_fase1 = [
    pygame.Rect(320, 400, 35, 20), pygame.Rect(355, 400, 35, 20),
    pygame.Rect(390, 400, 35, 20), pygame.Rect(425, 400, 35, 20),
    pygame.Rect(670, 400, 36, 20), pygame.Rect(706, 400, 36, 20),
    pygame.Rect(742, 400, 36, 20), pygame.Rect(778, 400, 36, 20),
    pygame.Rect(814, 400, 36, 20)
]
estrela_fase1 = pygame.Rect(940, 80, 40, 40)

# --- FASE 2 ---
plataformas_fase2 = [pygame.Rect(0, 430, 1200, 100)]  
espinhos_fase2 = []
largura_espinho = 35
for i in range(4): espinhos_fase2.append(pygame.Rect(200 + i * largura_espinho, 400, largura_espinho, 30))
for i in range(4): espinhos_fase2.append(pygame.Rect(450 + i * largura_espinho, 400, largura_espinho, 30))
for i in range(4): espinhos_fase2.append(pygame.Rect(700 + i * largura_espinho, 400, largura_espinho, 30))
moeda_fase2 = pygame.Rect(75, 190, 30, 50) 
moeda_coletada = False
pilar_fase2 = pygame.Rect(0, 0, 140, 160)
pilar_vel_y = 0
pilar_rachado = False
estrela_fase2 = pygame.Rect(880, 385, 45, 45)

# --- FASE 3 ---
plataformas_fase3 = [pygame.Rect(0, 320, 320, 200), pygame.Rect(320, 450, 880, 70)]
espinhos_fase3 = [pygame.Rect(320 + i * 36, 420, 36, 30) for i in range(22)]
pilar_fase3 = pygame.Rect(500, 0, 80, 260)
moeda_fase3 = pygame.Rect(120, 180, 30, 50) 
moeda_fase3_coletada = False
estrela_fase3 = pygame.Rect(800, 370, 45, 45)

# --- FASE 4 ---
plataformas_fase4 = [
    pygame.Rect(0, 450, 1200, 50),     
    pygame.Rect(250, 250, 80, 200),    
    pygame.Rect(520, 310, 80, 140),    
    pygame.Rect(850, 350, 200, 100)    
]
espinhos_fase4 = []
for i in range(0, 7): espinhos_fase4.append(pygame.Rect(i * 35, 425, 35, 25))
espinhos_meio_x = [335, 370, 405, 440, 475]
for x_pos in espinhos_meio_x: espinhos_fase4.append(pygame.Rect(x_pos, 425, 35, 25))
for i in range(17, 24): espinhos_fase4.append(pygame.Rect(i * 36, 425, 36, 25))
espinho_topo_pilar2 = pygame.Rect(545, 285, 30, 25)
espinhos_fase4.append(espinho_topo_pilar2)
moeda_fase4 = pygame.Rect(120, 250, 30, 50) 
moeda_fase4_coletada = False
estrela_fase4 = pygame.Rect(920, 290, 45, 45)

# --- FASE 5 (FASE FINAL POLIDA) ---
plataformas_fase5 = [
    pygame.Rect(0, 270, 190, 230),     # Bloco de início esquerdo
    pygame.Rect(290, 180, 140, 320),   # Pilar central alto
    pygame.Rect(430, 410, 150, 90),    # Chão rebaixado após o pilar central
    pygame.Rect(580, 310, 90, 190),    # Primeiro degrau da montanha direita
    pygame.Rect(670, 240, 70, 260),    # Segundo degrau mais alto
    pygame.Rect(740, 160, 460, 340),   # Topo final da montanha da direita
    pygame.Rect(280, 0, 160, 80)       # Suporte reajustado para espinhos superiores
]

espinhos_fase5 = [
    # Espinho solitário no fundo do vão profundo
    pygame.Rect(495, 385, 30, 25),
    
    # Espinhos superiores (TETO) - LARGURA AUMENTADA para preencher melhor o bloco
    pygame.Rect(295, 80, 65, 30),
    pygame.Rect(360, 80, 65, 30),
    
    # Espinhos do topo do pilar central
    pygame.Rect(325, 155, 35, 25),
    pygame.Rect(370, 155, 35, 25),
    
    # NOVO: Espinhos nos cantos e quinas da escadinha da direita
    pygame.Rect(580, 285, 25, 25),  # Canto superior do primeiro degrau
    pygame.Rect(670, 215, 25, 25)   # Canto superior do segundo degrau
]

estrela_fase5 = pygame.Rect(790, 85, 45, 45)


# Variáveis dinâmicas da fase ativa
plataformas = plataformas_fase1
espinhos = espinhos_fase1
estrela = estrela_fase1

def disparar_transicao(proxima_fase):
    global transicao_fase_alvo, transicao_estado, transicao_alpha
    if transicao_estado == "parado":
        transicao_fase_alvo = proxima_fase
        transicao_estado = "escurecendo"
        transicao_alpha = 0

def carregar_fase(fase):
    global plataformas, espinhos, estrela, fase_atual, player 
    global moeda_coletada, moeda_fase3_coletada, moeda_fase4_coletada
    global pilar_rachado, pilar_fase2, pilar_vel_y
    global player_float_x, player_float_y, vel_x, vel_y
    
    fase_atual = fase
    
    if fase == 1:
        plataformas = plataformas_fase1
        espinhos = espinhos_fase1
        estrela = estrela_fase1
        resetar_posicao()
    elif fase == 2:
        plataformas = plataformas_fase2
        espinhos = espinhos_fase2
        estrela = estrela_fase2
        moeda_coletada = False
        pilar_rachado = False
        pilar_vel_y = 0
        pilar_fase2 = pygame.Rect(0, 0, 140, 160) 
        player.topleft = (40, 395)
        player_float_x = float(player.x); player_float_y = float(player.y)
        vel_x = vel_y = 0
    elif fase == 3:
        plataformas = plataformas_fase3
        espinhos = espinhos_fase3
        estrela = estrela_fase3
        moeda_fase3_coletada = False
        player.topleft = (50, 280)
        player_float_x = float(player.x); player_float_y = float(player.y)
        vel_x = vel_y = 0
    elif fase == 4:
        plataformas = plataformas_fase4
        espinhos = espinhos_fase4
        estrela = estrela_fase4
        moeda_fase4_coletada = False
        player.topleft = (278, 210)
        player_float_x = float(player.x); player_float_y = float(player.y)
        vel_x = vel_y = 0
    elif fase == 5:
        plataformas = plataformas_fase5
        espinhos = espinhos_fase5
        estrela = estrela_fase5
        player.topleft = (45, 230) 
        player_float_x = float(player.x); player_float_y = float(player.y)
        vel_x = vel_y = 0

def resetar_posicao():
    global player_float_x, player_float_y, vel_x, vel_y, pulos_restantes, pode_dash, no_chao, moeda_coletada, pilar_rachado, pilar_vel_y
    if fase_atual == 1:
        player.topleft = (50, 300)
    elif fase_atual == 2:
        player.topleft = (40, 395)
        if not moeda_coletada:
            pilar_fase2.y = 0
            pilar_vel_y = 0
            pilar_rachado = False
    elif fase_atual == 3:
        player.topleft = (50, 280)
    elif fase_atual == 4:
        player.topleft = (278, 210)
    elif fase_atual == 5:
        player.topleft = (45, 230)
            
    player_float_x = float(player.x)
    player_float_y = float(player.y)
    vel_x = vel_y = 0
    pulos_restantes = pulos_max
    pode_dash = True
    no_chao = False

# LOOP PRINCIPAL
while True:
    clock.tick(60)

    for t in trail[:]:
        t[2] -= 1
        if t[2] <= 0:
            trail.remove(t)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pausado = not pausado

            if not pausado and not venceu and transicao_estado == "parado":
                if event.key == pygame.K_SPACE:
                    if pulos_restantes > 0:
                        no_chao = False 

                        if pulos_restantes == 2:
                            vel_y = forca_pulo 
                            particula(player.centerx, player.bottom, BRANCO)
                            tocar_som(som_pulo1)
                        else:
                            vel_y = forca_segundo_pulo 
                            particula(player.centerx, player.bottom, AMARELO)
                            tocar_som(som_pulo2)

                        pulos_restantes -= 1

                if event.key == pygame.K_LSHIFT and dash_cd_timer == 0 and pode_dash:
                    dashing = True
                    dash_timer = 10
                    dash_cd_timer = dash_cd
                    pode_dash = False
                    no_chao = False

                    tocar_som(som_dash)

                    teclas = pygame.key.get_pressed()
                    dx = teclas[pygame.K_d] - teclas[pygame.K_a]
                    dy = teclas[pygame.K_s] - teclas[pygame.K_w]

                    if dx == 0 and dy == 0: dx = 1

                    mag = math.hypot(dx, dy)
                    dash_dir = (dx/mag, dy/mag)

                    vento_dash(player.centerx, player.centery, dash_dir)
                    particula(player.centerx, player.centery, AZUL)
                    shake_timer = 8

    try:
        pygame.mixer.music.set_volume(volume_pause if pausado else volume_normal)
    except:
        pass

    if pausado:
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(80)
        overlay.fill((0, 0, 0))
        TELA.blit(overlay, (0, 0))
        texto = fonte.render("PAUSADO", True, BRANCO)
        TELA.blit(texto, (20, 20))
        pygame.display.update()
        continue

    # ATUALIZAÇÃO DA TRANSIÇÃO DE FASE (FADE)
    if transicao_estado == "escurecendo":
        transicao_alpha += 15  # Velocidade do fecho de tela
        if transicao_alpha >= 255:
            transicao_alpha = 255
            if transicao_fase_alvo == "VITORIA":
                venceu = True
            else:
                carregar_fase(transicao_fase_alvo)
            transicao_estado = "clareando"
            
    elif transicao_estado == "clareando":
        transicao_alpha -= 15
        if transicao_alpha <= 0:
            transicao_alpha = 0
            transicao_estado = "parado"

    if not venceu and transicao_estado != "escurecendo":
        # Movimentação Horizontal
        teclas = pygame.key.get_pressed()
        move = teclas[pygame.K_d] - teclas[pygame.K_a]

        if move != 0:
            vel_x += move * aceleracao
        else:
            if vel_x > 0: vel_x -= friccao
            elif vel_x < 0: vel_x += friccao
            if abs(vel_x) < friccao: vel_x = 0

        vel_x = max(-vel_max, min(vel_max, vel_x))

        # Lógica do Dash
        if dashing:
            vel_x = dash_dir[0] * dash_speed
            vel_y = dash_dir[1] * dash_speed
            dash_timer -= 1
            trail.append([player.x, player.y, 12])
            vento_dash(player.centerx, player.centery, dash_dir)

            if dash_timer <= 0:
                dashing = False
                vel_x *= 0.5
                vel_y *= 0.5
        else:
            vel_y += gravidade

        if dash_cd_timer > 0: dash_cd_timer -= 1

        # Lógica do Pilar Cadente (Fase 2)
        if fase_atual == 2 and pilar_rachado:
            pilar_vel_y += 0.25  
            pilar_fase2.y += int(pilar_vel_y)

        # --- SISTEMA DE COLISÕES ---
        no_chao_anterior = no_chao
        no_chao = False

        # Movimentação Eixo X
        player_float_x += vel_x
        player.x = round(player_float_x)
        
        for plat in plataformas:
            if player.colliderect(plat):
                if vel_x > 0: player.right = plat.left
                elif vel_x < 0: player.left = plat.right
                player_float_x = float(player.x)

        # Movimentação Eixo Y
        player_float_y += vel_y
        player.y = round(player_float_y)
        
        for plat in plataformas:
            if player.colliderect(plat):
                if vel_y > 0:  
                    player.bottom = plat.top
                    vel_y = 0
                    no_chao = True
                elif vel_y < 0:  
                    player.top = plat.bottom
                    vel_y = 0
                player_float_y = float(player.y)

        if no_chao:
            pode_dash = True
            pulos_restantes = pulos_max

        if no_chao and not no_chao_anterior:
            tocar_som(som_queda)
            poeira_impacto(player.centerx, player.bottom, 4)
            shake_timer = 4

        # Coleta de Moedas
        if fase_atual == 2 and not moeda_coletada:
            if player.colliderect(moeda_fase2):
                moeda_coletada = True
                pilar_rachado = True
                tocar_som(som_moeda)
                tocar_som(som_desabamento)
                shake_timer = 25  

        if fase_atual == 3 and not moeda_fase3_coletada:
            if player.colliderect(moeda_fase3):
                moeda_fase3_coletada = True
                tocar_som(som_moeda)

        if fase_atual == 4 and not moeda_fase4_coletada:
            if player.colliderect(moeda_fase4):
                moeda_fase4_coletada = True
                tocar_som(som_moeda)

        # Verificação de mortes
        if fase_atual == 2 and player.colliderect(pilar_fase2):
            tocar_som(som_morte); mortes += 1; resetar_posicao(); shake_timer = 12

        if fase_atual == 3 and player.colliderect(pilar_fase3):
            tocar_som(som_morte); mortes += 1; resetar_posicao(); shake_timer = 12

        for espinho in espinhos:
            if player.colliderect(espinho):
                tocar_som(som_morte)
                mortes += 1
                resetar_posicao()
                shake_timer = 12

        # Disparadores de transição ao colidir com a estrela
        if player.colliderect(estrela):
            tocar_som(som_vitoria_fase) 
            if fase_atual == 1: disparar_transicao(2)
            elif fase_atual == 2: disparar_transicao(3)
            elif fase_atual == 3: disparar_transicao(4)
            elif fase_atual == 4: disparar_transicao(5)
            elif fase_atual == 5: disparar_transicao("VITORIA")

        # Abismo
        if player.y > 550:
            tocar_som(som_morte)
            mortes += 1
            resetar_posicao()

    # ATUALIZAÇÃO DA CÂMERA
    alvo_x = player.centerx - LARGURA // 2
    camera_x += (alvo_x - camera_x) * camera_suave
    camera_x = max(0, min(camera_x, 350)) 
    camera_y = 0  

    # Screenshake
    offset_x = random.randint(-shake_int, shake_int) if shake_timer > 0 else 0
    offset_y = random.randint(-shake_int, shake_int) if shake_timer > 0 else 0
    if shake_timer > 0: shake_timer -= 1

    # Atualizar vento FX
    for v in vento[:]:
        v[0] += v[2]; v[1] += v[3]; v[4] -= 1
        v[2] *= 0.95; v[3] *= 0.95
        if v[4] <= 0: vento.remove(v)

    # Atualizar Neve
    for floco in neve:
        floco[1] += floco[2]
        floco[0] += random.choice([-0.5, 0, 0.5])
        if floco[1] > 500:
            floco[0] = random.randint(0, 1200)
            floco[1] = -10

    # RENDERIZAÇÃO (DRAW)
    TELA.fill(COR_FUNDO_CEU) 

    # Parallax
    para1_x = -(camera_x * 0.15) + offset_x
    montanhas_distantes = [
        [(100, 450), (250, 220), (400, 450)],
        [(350, 450), (550, 180), (750, 450)],
        [(700, 450), (880, 250), (1060, 450)]
    ]
    for montanha in montanhas_distantes:
        pontos = [(p[0] + para1_x, p[1] + offset_y) for p in montanha]
        pygame.draw.polygon(TELA, COR_MONTANHA_DISTANTE, pontos)

    para2_x = -(camera_x * 0.35) + offset_x
    montanhas_medias = [
        [(-50, 480), (100, 290), (250, 480)],
        [(200, 480), (380, 260), (560, 480)],
        [(500, 480), (680, 300), (860, 480)],
        [(800, 480), (1000, 270), (1200, 480)]
    ]
    for montanha in montanhas_medias:
        pontos = [(p[0] + para2_x, p[1] + offset_y) for p in montanha]
        pygame.draw.polygon(TELA, COR_MONTANHA_MEDIA, pontos)

    para3_x = -(camera_x * 0.6) + offset_x
    colinas_proximas = [
        [(0, 500), (150, 380), (350, 500)],
        [(300, 500), (500, 360), (700, 500)],
        [(650, 500), (850, 390), (1100, 500)]
    ]
    for colina in colinas_proximas:
        pontos = [(p[0] + para3_x, p[1] + offset_y) for p in colina]
        pygame.draw.polygon(TELA, COR_COLINA_PROXIMA, pontos)

    def draw_rect(rect, cor):
        pygame.draw.rect(TELA, cor,
            (rect.x - camera_x + offset_x,
             rect.y - camera_y + offset_y,
             rect.w, rect.h))

    # Neve
    for floco in neve:
        pygame.draw.circle(TELA, (200, 200, 250),
            (int(floco[0] - camera_x + offset_x),
             int(floco[1] - camera_y + offset_y)),
            floco[3])

    # FX Vento / Trail / Partículas
    for v in vento:
        alpha = max(0, min(255, int(255 * (v[4] / 20))))
        surf = pygame.Surface((v[5], int(v[5]/3)), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (150, 200, 255, alpha), (0, 0, v[5], int(v[5]/3)))
        TELA.blit(surf, (v[0] - camera_x + offset_x, v[1] - camera_y + offset_y))

    for t in trail:
        alpha = max(0, min(255, t[2] * 20))
        surf = pygame.Surface((player.w, player.h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (100, 100, 255, alpha), (0, 0, player.w, player.h))
        TELA.blit(surf, (t[0] - camera_x + offset_x, t[1] - camera_y + offset_y))

    for p in particulas[:]:
        p[0] += p[2]; p[1] += p[3]; p[4] -= 0.15
        if p[4] <= 0:
            particulas.remove(p)
            continue
        pygame.draw.circle(TELA, p[5], (int(p[0] - camera_x + offset_x), int(p[1] - camera_y + offset_y)), int(p[4]))

    # Plataformas Sólidas
    for plat in plataformas:
        draw_rect(plat, BRANCO)

    # Elementos dinâmicos das fases antigas
    if fase_atual == 2:
        draw_rect(pilar_fase2, BRANCO)
        if pilar_rachado:
            px = pilar_fase2.x - camera_x + offset_x
            py = pilar_fase2.y - camera_y + offset_y
            pygame.draw.line(TELA, PRETO, (px + 20, py), (px + 60, py + 80), 3)
            pygame.draw.line(TELA, PRETO, (px + 60, py + 80), (px + 40, py + 160), 3)

    if fase_atual == 3:
        draw_rect(pilar_fase3, BRANCO)
        p1 = (pilar_fase3.centerx - camera_x + offset_x, pilar_fase3.bottom + 20 - camera_y + offset_y)
        p2 = (pilar_fase3.left - camera_x + offset_x, pilar_fase3.bottom - camera_y + offset_y)
        p3 = (pilar_fase3.right - camera_x + offset_x, pilar_fase3.bottom - camera_y + offset_y)
        pygame.draw.polygon(TELA, BRANCO, [p1, p2, p3])

    # Desenhar Espinhos (Com suporte a espinhos de teto)
    for espinho in espinhos:
        if fase_atual == 5 and espinho.top < 100:  # Espinhos do teto da fase final
            p1 = (espinho.centerx - camera_x + offset_x, espinho.bottom - camera_y + offset_y)
            p2 = (espinho.left - camera_x + offset_x, espinho.top - camera_y + offset_y)
            p3 = (espinho.right - camera_x + offset_x, espinho.top - camera_y + offset_y)
        else:  # Espinhos padrão voltados para CIMA
            p1 = (espinho.centerx - camera_x + offset_x, espinho.top - camera_y + offset_y)
            p2 = (espinho.left - camera_x + offset_x, espinho.bottom - camera_y + offset_y)
            p3 = (espinho.right - camera_x + offset_x, espinho.bottom - camera_y + offset_y)
            
        pygame.draw.polygon(TELA, ROXO_ESPINHO, [p1, p2, p3])

    # Moedas
    if fase_atual == 2 and not moeda_coletada:
        mx = moeda_fase2.x - camera_x + offset_x; my = moeda_fase2.y - camera_y + offset_y
        pygame.draw.ellipse(TELA, OURO, (mx, my, moeda_fase2.w, moeda_fase2.h))
        pygame.draw.ellipse(TELA, AMARELO, (mx + 4, my + 4, moeda_fase2.w - 8, moeda_fase2.h - 8))

    if fase_atual == 3 and not moeda_fase3_coletada:
        mx = moeda_fase3.x - camera_x + offset_x; my = moeda_fase3.y - camera_y + offset_y
        pygame.draw.ellipse(TELA, OURO, (mx, my, moeda_fase3.w, moeda_fase3.h))
        pygame.draw.ellipse(TELA, AMARELO, (mx + 4, my + 4, moeda_fase3.w - 8, moeda_fase3.h - 8))

    if fase_atual == 4 and not moeda_fase4_coletada:
        mx = moeda_fase4.x - camera_x + offset_x; my = moeda_fase4.y - camera_y + offset_y
        pygame.draw.ellipse(TELA, OURO, (mx, my, moeda_fase4.w, moeda_fase4.h))
        pygame.draw.ellipse(TELA, AMARELO, (mx + 4, my + 4, moeda_fase4.w - 8, moeda_fase4.h - 8))

    # Estrela objetivo
    draw_rect(estrela, AMARELO)

    # Jogador
    cor_player = AZUL if pode_dash else ROXO
    draw_rect(player, cor_player)

    # HUD / Cronômetro
    if not venceu:
        tempo_ms = pygame.time.get_ticks() - tempo_inicio
        tempo_seg = tempo_ms // 1000
        minutos = tempo_seg // 60
        segundos = tempo_seg % 60
    
    txt_tempo = fonte.render(f"{minutos:02}:{segundos:02}", True, BRANCO)
    TELA.blit(txt_tempo, (LARGURA - 100, 20))

    txt_mortes = fonte.render(f"💀 {mortes}", True, BRANCO)
    TELA.blit(txt_mortes, (20, 20))
    
    txt_fase = fonte.render(f"FASE {fase_atual}", True, BRANCO)
    TELA.blit(txt_fase, (LARGURA // 2 - 40, 20))

    # RENDERIZAÇÃO DA TRANSIÇÃO DE FASE (EFEITO FADE)
    if transicao_alpha > 0:
        surf_transicao = pygame.Surface((LARGURA, ALTURA))
        surf_transicao.fill((0, 0, 0))
        surf_transicao.set_alpha(transicao_alpha)
        TELA.blit(surf_transicao, (0, 0))

    # Tela de Vitória Final
    if venceu:
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.set_alpha(150)
        overlay.fill((20, 10, 30))
        TELA.blit(overlay, (0, 0))
        
        txt_win = fonte.render("VOCÊ ZEROU O JOGO COMPLETO!", True, AMARELO)
        txt_sub = fonte.render(f"Parabéns! Tempo final: {minutos:02}:{segundos:02} | Mortes totais: {mortes}", True, BRANCO)
        TELA.blit(txt_win, (LARGURA // 2 - 170, ALTURA // 2 - 30))
        TELA.blit(txt_sub, (LARGURA // 2 - 240, ALTURA // 2 + 10))

    pygame.display.update()