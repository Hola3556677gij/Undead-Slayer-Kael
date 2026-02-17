import pygame as pg
import random

# Inicialización optimizada
pg.init()
W, H = 854, 480
win = pg.display.set_mode((W, H))
clock = pg.time.Clock()

# --- CONSTANTES ---
ORO_AMBAR = (255, 180, 0)
C_CAPA = (150, 10, 10)
C_SANGRE = (130, 0, 0)
LIMITE_MUN = {"ARCO": 5, "ESPADA": 15, "CUCHILLO": 30}

# --- ESTADO ---
kx, ky = 150, 310
hp, score, bajas = 100, 0, 0
municion = LIMITE_MUN.copy()
arma_actual = "ARCO"
zombies, proyectiles, manchas = [], [], []
game_over = False

# --- OPTIMIZACIÓN: DIBUJO ÚNICO DE PERSONAJES ---
def crear_sprite(mat, cols, sz=6):
    s = pg.Surface((len(mat[0])*sz, len(mat)*sz), pg.SRCALPHA)
    for r, row in enumerate(mat):
        for c, char in enumerate(row):
            if char in cols:
                pg.draw.rect(s, cols[char], (c*sz, r*sz, sz, sz))
    return s

# Matrices de diseño
K_MAT = ["....LLLL....", "...LSSSSLL..", "..LSSBSSSL..", "..AABBBBAA..", ".RRRRRRRRRR.", ".RRRRRRRRRR.", "..AA....AA..", "..AA....AA.."]
Z_MAT = ["....GGGG....", "...GGEGGEG..", "...GGGGGG...", "....GGGG....", "..XXGGGGXX..", "..XXGGGGXX..", "...GG..GG...", "...XX..XX..."]
k_cols = {'L': (220, 220, 230), 'S': (190, 160, 140), 'B': (40, 30, 20), 'A': (35, 35, 40), 'R': C_CAPA}
z_cols = {'G': (60, 80, 60), 'E': (255, 0, 0), 'X': (40, 40, 50)}

# Sprites pre-dibujados (Esto hace que vaya fluido)
spr_kael = crear_sprite(K_MAT, k_cols)
spr_zombie = crear_sprite(Z_MAT, z_cols)

# Fondo pre-renderizado
fondo_edificios = pg.Surface((W, H))
fondo_edificios.fill((5, 5, 10))
for i in range(8):
    ex, eh = i * 140 + random.randint(-20, 20), random.randint(150, 350)
    pg.draw.rect(fondo_edificios, (20, 20, 25), (ex, H-60-eh, 90, eh))
    for _ in range(4):
        pg.draw.rect(fondo_edificios, (10, 10, 15), (ex+random.randint(10,60), H-60-eh+random.randint(30, eh-40), 15, 20))

# --- BUCLE PRINCIPAL ---
while True:
    # 1. Dibujar fondo estático (Súper rápido)
    win.blit(fondo_edificios, (0, 0))
    pg.draw.rect(win, (15, 15, 20), (0, 385, W, 100)) # Suelo
    for s in manchas: pg.draw.circle(win, C_SANGRE, (s[0], s[1]), s[2])

    mx, my = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()[0]
    btn_atq = pg.Rect(W-140, H-140, 100, 100)

    for ev in pg.event.get():
        if ev.type == pg.QUIT: pg.quit()
        if ev.type == pg.MOUSEBUTTONDOWN and not game_over:
            # Cambio de arma
            if my < 80:
                if mx < 130: arma_actual = "ARCO"
                elif 130 < mx < 260: arma_actual = "ESPADA"
                elif 260 < mx < 390: arma_actual = "CUCHILLO"
            
            # Ataque
            if btn_atq.collidepoint(mx, my) and municion[arma_actual] > 0:
                municion[arma_actual] -= 1
                if arma_actual == "ARCO":
                    proyectiles.append([kx + 50, ky + 25])
                else:
                    rango = 110 if arma_actual == "ESPADA" else 70
                    for z in zombies[:]:
                        if abs(z[0] - kx) < rango:
                            zombies.remove(z); score += 25; bajas += 1
                            manchas.append([z[0]+20, 395, random.randint(10,20)])
                
                if bajas >= 4:
                    municion = LIMITE_MUN.copy()
                    bajas = 0

    if not game_over:
        # Movimiento fluido
        if click and mx < W/2 and my > 200: 
            kx += 8 if mx > 150 else -8
        
        # Spawn y Lógica
        if random.randint(1, 60) == 1: zombies.append([W, 320])

        for f in proyectiles[:]:
            f[0] += 25
            pg.draw.rect(win, (255, 255, 255), (f[0], f[1], 15, 4))
            if f[0] > W: proyectiles.remove(f)
            for z in zombies[:]:
                if pg.Rect(z[0], 320, 50, 70).collidepoint(f[0], f[1]):
                    zombies.remove(z); proyectiles.remove(f)
                    score += 20; bajas += 1; break

        for z in zombies[:]:
            z[0] -= 4 if (z[0] - kx) > 35 else 0
            if (z[0] - kx) <= 35:
                hp -= 1.8; kx -= 5 # Daño real
            win.blit(spr_zombie, (z[0], 320))

        # Dibujar a Kael
        win.blit(spr_kael, (kx, ky))

        # UI Optimizada
        f = pg.font.SysFont("monospace", 18, bold=True)
        win.blit(f.render(f"{arma_actual}: {municion[arma_actual]} | RECARGA: {bajas}/4", True, ORO_AMBAR), (20, 80))
        pg.draw.rect(win, (255, 0, 0), (20, H-30, hp * 2, 15)) # Vida
        pg.draw.circle(win, (150, 0, 0), btn_atq.center, 50) # Botón
        
        # Botones de arma
        for i, a in enumerate(["ARCO", "ESPADA", "CUCHILLO"]):
            col = ORO_AMBAR if arma_actual == a else (70, 70, 80)
            pg.draw.rect(win, col, (20 + i*115, 20, 105, 40), 0 if arma_actual == a else 2)
            win.blit(f.render(a, True, (0,0,0) if arma_actual == a else (200,200,200)), (30 + i*115, 30))

        if hp <= 0: game_over = True
    else:
        win.fill((0,0,0))
        win.blit(f.render("CAÍSTE... TOCA PARA REINTENTAR", True, (200,0,0)), (W//2-180, H//2))
        if click: 
            hp, score, bajas, municion, zombies, manchas, game_over, kx = 100, 0, 0, LIMITE_MUN.copy(), [], [], False, 150

    pg.display.flip()
    clock.tick(60) # Mantiene 60 FPS estables
