import pygame
import sys
import random

pygame.init()

# =========================
# CONFIG
# =========================
LARGURA = 1000
ALTURA = 500
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Boss Fight - FINAL SYSTEM")

clock = pygame.time.Clock()

# CORES
BRANCO = (255,255,255)
AZUL = (0,0,255)
VERMELHO = (255,0,0)
AMARELO = (255,255,0)
PRETO = (0,0,0)
CIANO = (0,255,255)
ROXO = (150,0,150)
LARANJA = (255,140,0)
VERDE = (0,255,100)

CHAO = 350


# =========================
# CAMERA
# =========================
class Camera:
    def __init__(self):
        self.x = 0

    def update(self, target_x):
        self.x += (target_x - self.x - LARGURA // 2) * 0.08


# =========================
# PROJECTILE
# =========================
class Projectile:
    def __init__(self, x, y, vel):
        self.x = x
        self.y = y
        self.vel = vel

    def update(self):
        self.x += self.vel

    def draw(self, screen, cam):
        pygame.draw.circle(screen, ROXO,
                           (int(self.x - cam.x), int(self.y)), 6)

    def rect(self):
        return pygame.Rect(self.x, self.y, 12, 12)


# =========================
# PLAYER
# =========================
class Player:
    def __init__(self):
        self.x = 100
        self.y = CHAO
        self.w = 40
        self.h = 60

        self.vel = 5
        self.vida = 100

        self.vel_y = 0
        self.pulando = False

        # DASH (INVENCÍVEL)
        self.dash = False
        self.dash_timer = 0

        # PARry
        self.parry = False
        self.parry_timer = 0

        # ATAQUE
        self.attacking = False
        self.attack_timer = 0
        self.attack_cd = 0
        self.attack_window = False
        self.attack_used = False

        # DIREÇÃO
        self.facing = 1

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def attack_rect(self):
        if not self.attacking:
            return None

        return pygame.Rect(
            self.x + (self.facing * 60),
            self.y + 10,
            90,
            self.h - 20
        )

    def update(self, keys):

        # MOVIMENTO
        if keys[pygame.K_a] and not self.dash:
            self.x -= self.vel
            self.facing = -1

        if keys[pygame.K_d] and not self.dash:
            self.x += self.vel
            self.facing = 1

        # DASH (INVENCÍVEL)
        if self.dash:
            if keys[pygame.K_a]:
                self.x -= 15
            if keys[pygame.K_d]:
                self.x += 15

            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dash = False

        # ATAQUE
        if self.attacking:
            self.attack_timer -= 1

            if 5 <= self.attack_timer <= 7:
                self.attack_window = True
            else:
                self.attack_window = False

            if self.attack_timer <= 0:
                self.attacking = False
                self.attack_used = False

        if self.attack_cd > 0:
            self.attack_cd -= 1

        # PARry
        if self.parry:
            self.parry_timer -= 1
            if self.parry_timer <= 0:
                self.parry = False

        # PULO
        if self.pulando:
            self.y += self.vel_y
            self.vel_y += 1

            if self.y >= CHAO:
                self.y = CHAO
                self.pulando = False
                self.vel_y = 0

    def draw(self, screen, cam):
        cor = AZUL

        if self.dash:
            cor = AMARELO
        if self.parry:
            cor = CIANO
        if self.attacking:
            cor = VERDE

        pygame.draw.rect(screen, cor,
                         (self.x - cam.x, self.y, self.w, self.h))


# =========================
# BOSS
# =========================
class Boss:
    def __init__(self):
        self.x = 700
        self.y = CHAO
        self.w = 60
        self.h = 70

        self.vida = 200
        self.estado = "idle"
        self.timer = 140

        self.dash_dir = 1
        self.dash_dist = 0
        self.preparando = False

        self.projeteis = []

        # 💀 CRIT WINDOW
        self.crit = False
        self.crit_timer = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def take_damage(self, dmg, knock_dir=0):
        if self.crit:
            dmg *= 2  # 💥 CRIT DAMAGE DOBRADO

        self.vida -= dmg
        self.x += knock_dir * 10

    def update(self, player):

        # crit timer
        if self.crit:
            self.crit_timer -= 1
            if self.crit_timer <= 0:
                self.crit = False

        self.timer -= 1

        if self.timer <= 0 and self.estado == "idle":
            self.estado = random.choice(["dash", "tiro"])
            self.timer = 100

        # DASH
        if self.estado == "dash":
            if not self.preparando:
                self.preparando = True
                self.timer = 30
                self.dash_dir = 1 if player.x > self.x else -1
            else:
                if self.timer <= 0:
                    self.x += self.dash_dir * 25
                    self.dash_dist += 25

                    if self.dash_dist > 300:
                        self.estado = "idle"
                        self.preparando = False
                        self.dash_dist = 0
                        self.timer = 140

        # TIRO
        elif self.estado == "tiro":
            if self.timer % 25 == 0:
                dir = 1 if player.x > self.x else -1
                self.projeteis.append(Projectile(self.x, self.y, dir * 7))

            if self.timer <= 0:
                self.estado = "idle"
                self.timer = 160

        # projéteis range
        for p in self.projeteis[:]:
            p.update()
            if p.x < -200 or p.x > 2400:
                self.projeteis.remove(p)

    def draw(self, screen, cam):

        cor = VERMELHO

        if self.crit:
            cor = (255, 120, 120)

        pygame.draw.rect(screen, cor,
                         (self.x - cam.x, self.y, self.w, self.h))

        for p in self.projeteis:
            p.draw(screen, cam)


# =========================
# SETUP
# =========================
player = Player()
boss = Boss()
camera = Camera()

hitstop = 0
parry_freeze = 0


# =========================
# LOOP
# =========================
while True:
    clock.tick(60)

    freeze = hitstop > 0 or parry_freeze > 0

    if hitstop > 0:
        hitstop -= 1
    if parry_freeze > 0:
        parry_freeze -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            # PULO
            if event.key == pygame.K_SPACE and not player.pulando:
                player.pulando = True
                player.vel_y = -15

            # DASH (INVENCÍVEL)
            if event.key == pygame.K_LSHIFT:
                player.dash = True
                player.dash_timer = 10

            # PARry
            if event.key == pygame.K_f:
                player.parry = True
                player.parry_timer = 10

            # ATAQUE
            if event.key == pygame.K_j and player.attack_cd == 0:
                player.attacking = True
                player.attack_timer = 12
                player.attack_cd = 45

    if freeze:
        TELA.fill((255,255,255))
        player.draw(TELA, camera)
        boss.draw(TELA, camera)
        pygame.display.update()
        continue

    keys = pygame.key.get_pressed()

    player.update(keys)
    boss.update(player)
    camera.update(player.x)

    # =========================
    # ATAQUE
    # =========================
    if player.attacking and player.attack_window and not player.attack_used:
        ar = player.attack_rect()

        if ar and ar.colliderect(boss.rect()):
            boss.take_damage(10, 1 if player.facing == 1 else -1)
            hitstop = 3
            player.attack_used = True

    # =========================
    # PARRY → CRIT WINDOW
    # =========================
    for p in boss.projeteis[:]:
        if p.rect().colliderect(player.rect()):
            if player.parry:
                p.vel *= -1
                parry_freeze = 8
                hitstop = 2

                # 💥 CRIT WINDOW ATIVADO
                boss.crit = True
                boss.crit_timer = 180  # 3 segundos

            else:
                boss.projeteis.remove(p)

    # =========================
    # DRAW
    # =========================
    TELA.fill(BRANCO)

    player.draw(TELA, camera)
    boss.draw(TELA, camera)

    pygame.draw.rect(TELA, PRETO, (10,10, player.vida*2, 10))
    pygame.draw.rect(TELA, VERMELHO, (10,30, boss.vida, 10))

    pygame.display.update()