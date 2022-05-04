from msilib.schema import Class
from turtle import Screen, screensize
from typing_extensions import Self
from matplotlib.pyplot import draw
import pygame as pg 
import sys 
import utils.constants as constants
import utils.matrix_transformations as mt
import sprite_mananger.sprite_mananger as sm
import random

clock = pg.time.Clock()
display = pg.display.set_mode(constants.WINDOW_SIZE, 0, 32)

tile_sheet_image = pg.image.load('./resources/atlas/iso_tileset1.png')
tile_sheet = sm.SpriteManganger(tile_sheet_image)

block_black_floor = tile_sheet.get_image(0, constants.FLOOR_SIZE, constants.FLOOR_SIZE, 4, (0, 0, 0))

block_white_floor = tile_sheet.get_image(1, constants.FLOOR_SIZE, constants.FLOOR_SIZE, 4, (0, 0, 0))

def calcularDistanciaPontos(xA,xB,yA,yB):
    return (((xB-xA)**2)+((yB-yA)**2))**(1/2)

#CONTADORES DE TEMPO SPAWN ITENS

static_timer = None
last_item_time = None

#PLAYER

class Player(object):
    def __init__(self, posicao_x, posicao_y) -> None:
        self.posicao_x = posicao_x
        self.posicao_y = posicao_y
        self.velocidade = 5
        self.raio = 20
        self.cor = (0,0,123)
        self.hitbox = (self.posicao_x, self.posicao_y, self.raio)
        
        pg.draw.circle(display, self.cor, (self.posicao_x,self.posicao_y), self.raio)
        pg.display.update()

    def desenhar(self):
        pg.draw.circle(display, self.cor, (self.posicao_x, self.posicao_y), self.raio)
        
    def andar(self):
        keys = pg.key.get_pressed()
    
        if keys[pg.K_LEFT] and self.posicao_x >= 490:
            self.posicao_x -= self.velocidade
        if keys[pg.K_RIGHT] and self.posicao_x <= 1440: 
            self.posicao_x += self.velocidade
        if keys[pg.K_UP] and self.posicao_y >= 275:
            self.posicao_y -= self.velocidade
        if keys[pg.K_DOWN] and self.posicao_y <= 735:
            self.posicao_y += self.velocidade

#BOSS

class Boss(object):
    def __init__(self, bossX, bossY):
        self.bossX = bossX
        self.bossY = bossY
        self.velI = 32
        self.raio = 20
        self.cor = (255,0,0)
        self.vida = 100
        self.walkCount = 2
        self.jump_count = 10
        self.is_jump = True
        self.largura = 0
        self.altura = 0

#Clase específica, recebe os parâmetros do boss, mas prioriza o que for dado dentro dela
class Torre(Boss):
    def andar(self):
        if self.walkCount <= 0: # o Boss anda "2" vezes antes de parar
                if distanciaX > 2 or distanciaX < -1: # Para o boss n ficar travando numa posição especifica (passível de mudança)
                    if self.bossX < Dama.posicao_x and distanciaX > 0: # Direita
                        self.bossX += (torre.velI + 32)
                        sombra.posicao_X += (torre.velI + 32)
                        self.is_jump = True
                        
                    elif self.bossX > Dama.posicao_x and distanciaX < 0: # Esquerda
                        self.bossX -= (torre.velI + 32)
                        sombra.posicao_X -= (torre.velI + 32)
                        self.is_jump = True
                    
                if distanciaY > 2 or distanciaY < -1:
                    if self.bossY < Dama.posicao_y and distanciaY > 0: # Baixo
                        self.bossY += self.velI
                        sombra.posicao_Y += self.velI
                        self.is_jump = True
                    
                    elif self.bossY > Dama.posicao_y and distanciaY < 0: # Cima
                        self.bossY -= self.velI
                        sombra.posicao_Y -= self.velI
                        self.is_jump = True

    def pular(self):
        self.is_jump = True
        if self.jump_count >= -10:
            self.bossY -= (self.jump_count ** 3) / 25
            self.jump_count -= 1

        else:
            self.is_jump = False
            self.jump_count = 10


class Sombra(object): 
    def __init__(self):
        self.raio = torre.raio
        self.posicao_X = torre.bossX - (self.raio // 2) + (torre.raio // 2)
        self.posicao_Y = torre.bossY - (self.raio // 2) + (torre.raio // 2)

    def desenhar(self):
        if torre.is_jump:
            pg.draw.circle(display, (250, 250, 250), (self.posicao_X, self.posicao_Y,), self.raio)

Dama = Player(1200,500)
torre = Torre(constants.WINDOW_SIZE[0] // 2, constants.WINDOW_SIZE[1] // 2) 
sombra = Sombra()            

#COLETÁVEIS

class coletaveis(object):
    def __init__(self, color, tamanho, posicao_coletavel_x, posicao_coletavel_y) -> None:
        self.color = color
        self.tamanho = tamanho
        self.posicao_coletavel_x = posicao_coletavel_x
        self.posicao_coletavel_y = posicao_coletavel_y
        self.hitbox = (self.posicao_coletavel_x, self.posicao_coletavel_y, self.tamanho)

cords_item_Verde = mt.mudanca_base(random.randint(1,8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
item_Verde = coletaveis((61,145,64), 10, cords_item_Verde[0], cords_item_Verde[1])

cords_item_roxo = mt.mudanca_base(random.randint(1,8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
item_Roxo = coletaveis((138,43,226), 10, cords_item_roxo[0], cords_item_roxo[1])

item_Verde_coletado = False

Game_over = False
game_over_img = pg.image.load('game_over.jpg')

#MAIN LOOP


run = True
while run:
    display.fill((146, 244, 255))

#SAIR DO JOGO        
    for event in pg.event.get():
        if event.type == pg.QUIT:            
            run = False
#CONSTRUÇÂO DO TABULEIRO           

    for row in range(8):
        for col in range(8):
            block_coords = mt.mudanca_base(row, col, constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
            if (row % 2 == 0 and col % 2 == 0) or (row % 2 == 1 and col % 2 == 1):
                display.blit(block_white_floor, block_coords)
            else:
                display.blit(block_black_floor, block_coords)

#DESENHO DO COLETÁVEL MAIS ATRIBUTO
    pg.draw.circle(display, item_Verde.color, (item_Verde.posicao_coletavel_x, item_Verde.posicao_coletavel_y), item_Verde.tamanho )

    
#DESENHO DO PLAYER E MOVIMENTAÇÂO COM OOP
 
    Dama.desenhar()
    Dama.andar()

#DESENHO DO BOOS E MOVIMENTAÇÃO COM OOP 
    if torre.vida > 0: # Se a vida da torre for < 0, a torre morre
        pg.draw.circle(display, torre.cor, (torre.bossX, torre.bossY), torre.raio)
    
        distanciaX = Dama.posicao_x - torre.bossX # Distancia entre o player e o boss na posição X
        distanciaY = Dama.posicao_y - torre.bossY # Distancia entre o player e o boss na posição Y

        if not torre.is_jump: #Caso não esteja pulando, anda
            torre.andar()

        else: #Pula e desenha a sombra
            torre.pular()
            sombra.desenhar()

        torre.walkCount += 1
        if torre.walkCount >= 40: #Velocidade do boss
            torre.walkCount = 0

        if not torre.is_jump: #Para ele não bater no player em cima no meio do pulo
            if calcularDistanciaPontos(Dama.posicao_x, torre.bossX, Dama.posicao_y, torre.bossY) <= 40:
                while True:
                    display.blit(game_over_img,(0,0))
                    pg.display.update()    
                    pg.time.delay(1500)
                    pg.quit()       

#MUDANÇA DE LUGAR DO ITEM / IDENTIFICAÇÃO SE ITEM FOI COLETADO
    if item_Verde_coletado == True:
        if last_item_time>3000:
            cords_item_Verde = mt.mudanca_base(random.randint(1, 8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
            item_Verde = coletaveis((61,145,64), 10, cords_item_Verde[0], cords_item_Verde[1])
            item_Verde_coletado = False
            Dama.velocidade -= 3
            Dama.cor  = (0,0,255)

            
#IDENTIFICAÇÃO DE COLISÃO COM O ITEM
        
    distanciaPlayerObjeto=calcularDistanciaPontos(Dama.posicao_x, item_Verde.posicao_coletavel_x, Dama.posicao_y, item_Verde.posicao_coletavel_y)
    if distanciaPlayerObjeto<=20:
        if Dama.velocidade<12:
            Dama.velocidade += 3
            Dama.cor = (0,238,238)
            item_Verde = item_Roxo

        item_Verde.posicao_coletavel_x = 0
        item_Verde.posicao_coletavel_y = 0
        item_Verde.color = (146, 244, 255)
        item_Verde.tamanho = 0
        static_timer = pg.time.get_ticks()
    
        item_Verde_coletado = True
    
#COOLDOWN DE SPAWN DE ITENS
    if static_timer:
        last_item_time = pg.time.get_ticks() - static_timer

    pg.display.update()
    clock.tick(60)
    