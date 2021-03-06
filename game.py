from turtle import update
import pygame as pg 
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

def jogar_novamente():
    global run
    global morto
    cont_frames = 1
    while morto:
        if cont_frames <= 480 :
            if cont_frames <= 40:
                display.blit(game_over_img[0], (0,0)) 

            elif cont_frames <= 280:
                display.blit(game_over_img[2], (0,0))    

            elif cont_frames <= 480:
                display.blit(game_over_img[1], (0,0))    

            pg.display.update()
            cont_frames += 1
            for event in pg.event.get():

                if event.type == pg.QUIT:
                    pg.quit()

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                    
                    else:
                        Dama.vida = 3
                        run = True
                        morto = False
                        Dama.posicao_x = 1200
                        Dama.posicao_y = 500
                        Dama.tempo_colisao = -3000                   
                
        else:
            cont_frames = 41

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
        self.ammo = 1
        self.vida = 1
        self.tempo_colisao = -3000

        self.cima = True
        self.direita = False
        self.esquerda = False
        self.baixo = False
        
    def desenhar(self):
        pg.draw.circle(display, self.cor, (self.posicao_x, self.posicao_y), self.raio)
        
    def andar(self):
        keys = pg.key.get_pressed()
    
        if keys[pg.K_LEFT] and self.posicao_x >= 490:
            self.posicao_x -= self.velocidade

            self.esquerda = True
            self.cima = False
            self.direita = False
            self.baixo = False

        if keys[pg.K_RIGHT] and self.posicao_x <= 1440: 
            self.posicao_x += self.velocidade

            self.direita = True
            self.cima = False
            self.esquerda = False
            self.baixo = False


        if keys[pg.K_UP] and self.posicao_y >= 275:
            self.posicao_y -= self.velocidade

            self.cima = True
            self.direita = False
            self.esquerda = False
            self.baixo = False

        if keys[pg.K_DOWN] and self.posicao_y <= 735:
            self.posicao_y += self.velocidade

            self.baixo = True
            self.cima = False
            self.direita = False
            self.esquerda = False
    
    def barra_de_vida(self):      
        
        if self.vida >= 1:           
            pg.draw.circle(display, (254,0,123), (220,120), 10) 

        if self.vida >= 2:           
            pg.draw.circle(display, (254,0,123), (245,120), 10) 
        
        if self.vida >= 3:
            pg.draw.circle(display, (254,0,123), (270,120), 10)

    def imortal(self): 
        if self.tempo_colisao > pg.time.get_ticks() - 3000:
            self.cor = (125, 125, 0)
            return True
        
        return False

    def tomar_dano(self):
        if self.imortal():
            return

        self.tempo_colisao = pg.time.get_ticks()
        self.vida -= 1

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
        self.walkDelay = 40
        self.largura = 0
        self.altura = 0

#Clase espec??fica, recebe os par??metros do boss, mas prioriza o que for dado dentro dela

class Torre(Boss):
    def andar(self):
        if self.walkCount <= 0: # o Boss anda "2" vezes antes de parar
            distanciaX = Dama.posicao_x - self.bossX # Distancia entre o player e o boss na posi????o X
            distanciaY = Dama.posicao_y - self.bossY # Distancia entre o player e o boss na posi????o Y

            if self.bossX <= Dama.posicao_x and distanciaX >= 0: # Direita
                self.bossX += (self.velI + 32)
                sombra.posicao_X += (self.velI + 32)
                self.is_jump = True
                
            elif self.bossX > Dama.posicao_x and distanciaX < 0: # Esquerda
                self.bossX -= (self.velI + 32)
                sombra.posicao_X -= (self.velI + 32)
                self.is_jump = True
                
            if self.bossY <= Dama.posicao_y and distanciaY >= 0: # Baixo
                self.bossY += self.velI
                sombra.posicao_Y += self.velI
                self.is_jump = True
            
            elif self.bossY > Dama.posicao_y and distanciaY < 0: # Cima
                self.bossY -= self.velI
                sombra.posicao_Y -= self.velI
                self.is_jump = True

    def desenhar(self):
        pg.draw.circle(display, self.cor, (self.bossX, self.bossY), self.raio)

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
            pg.draw.circle(display, (54,54,54), (self.posicao_X, self.posicao_Y,), self.raio)

Dama = Player(1200,500)
torre = Torre(constants.WINDOW_SIZE[0] // 2, constants.WINDOW_SIZE[1] // 2) 
sombra = Sombra()          

#PROJ??TIL

class Projetil(object):
    def __init__(self):
        self.color = (238,173,14)
        self.tamanho = 10
        self.posicao_projetil_x = 0
        self.posicao_projetil_y = 0
        self.range = 300
        self.destino = None
        self.hitbox = (self.posicao_projetil_x, self.posicao_projetil_y, self.tamanho)

    def desenhar(self):
        pg.draw.circle(display, projetil.color, (projetil.posicao_projetil_x, projetil.posicao_projetil_y), projetil.tamanho)

projetil = Projetil()

#COLET??VEIS

class coletaveis(object):
    def __init__(self, color, tamanho, posicao_coletavel_x, posicao_coletavel_y) -> None:
        self.color = color
        self.tamanho = tamanho
        self.posicao_coletavel_x = posicao_coletavel_x
        self.posicao_coletavel_y = posicao_coletavel_y
        self.hitbox = (self.posicao_coletavel_x, self.posicao_coletavel_y, self.tamanho)

cords_item_Verde = mt.mudanca_base(random.randint(1,8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
item_Verde = coletaveis((61,145,64), 10, cords_item_Verde[0], cords_item_Verde[1])

cords_item_vida_drop = mt.mudanca_base(random.randint(1,8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
Vida_item = coletaveis((255,0,226), 10, cords_item_vida_drop[0], cords_item_vida_drop[1])

posicao_da_bala_chao = [0,0]
arma_no_chao = coletaveis((238,173,14), 10, posicao_da_bala_chao[0], posicao_da_bala_chao[1])


item_Verde_coletado = False

item_vida_coletada = False

arma_no_chao_item = False

#ARRUMAR ESSA PARTE
Game_over = False
game_over_img = [pg.image.load('game_over.jpg'), pg.image.load('game_over_branco.jpg'), pg.image.load('game_over_vermelho.jpg')]
cont_img = 0

#MAIN LOOP

run = True
while run:
    display.fill((146, 244, 255))

#SAIR DO JOGO        
    for event in pg.event.get():
        if event.type == pg.QUIT:            
            run = False
#CONSTRU????O DO TABULEIRO           

    for row in range(8):
        for col in range(8):
            block_coords = mt.mudanca_base(row, col, constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
            if (row % 2 == 0 and col % 2 == 0) or (row % 2 == 1 and col % 2 == 1):
                display.blit(block_white_floor, block_coords)
            else:
                display.blit(block_black_floor, block_coords)

#DESENHO DO COLET??VEL MAIS ATRIBUTO
    pg.draw.circle(display, item_Verde.color, (item_Verde.posicao_coletavel_x, item_Verde.posicao_coletavel_y), item_Verde.tamanho )
    pg.draw.circle(display, Vida_item.color, (Vida_item.posicao_coletavel_x, Vida_item.posicao_coletavel_y), Vida_item.tamanho)

    
#DESENHO DO PLAYER E MOVIMENTA????O COM OOP
 
    Dama.desenhar()
    Dama.andar()
    Dama.barra_de_vida()
    Dama.imortal()

#BALA

    keys = pg.key.get_pressed()

    if keys[pg.K_SPACE] and Dama.posicao_y <= 735:
        if Dama.ammo > 0:
            if Dama.cima == True:
                projetil.destino = [Dama.posicao_x, Dama.posicao_y-projetil.range]
                posicao_da_bala_chao = projetil.destino
                
            if Dama.direita == True:
                projetil.destino = [Dama.posicao_x+projetil.range, Dama.posicao_y]
                posicao_da_bala_chao = projetil.destino

            if Dama.esquerda == True:
                projetil.destino = [Dama.posicao_x-projetil.range, Dama.posicao_y]
                posicao_da_bala_chao = projetil.destino

            if Dama.baixo == True:
                projetil.destino = [Dama.posicao_x, Dama.posicao_y+projetil.range]
                posicao_da_bala_chao = projetil.destino
        

#DESENHO DO BOOS E MOVIMENTA????O COM OOP 
    
    if torre.vida > 0: # Se a vida da torre for < 0, a torre morre
        torre.desenhar()

        if not torre.is_jump: #Caso n??o esteja pulando, anda
            torre.andar()

        else: #Pula e desenha a sombra
            torre.pular()
            sombra.desenhar()

        torre.walkCount += 1
        if torre.walkCount >= torre.walkDelay: #Velocidade do boss
            torre.walkCount = 0

        if not torre.is_jump: #Para ele n??o bater no player em cima no meio do pulo
            if calcularDistanciaPontos(Dama.posicao_x, torre.bossX, Dama.posicao_y, torre.bossY) <= 40 and not Dama.imortal():
                Dama.tomar_dano()
                              
                if Dama.vida == 0:
                    morto = True
                    
                    while morto and run:                       
                        jogar_novamente()

            else:
                Dama.cor = (0,0,123)

#MUDAN??A DE LUGAR DO ITEM / IDENTIFICA????O SE ITEM FOI COLETADO
    
    if item_Verde_coletado:
        
        if last_item_time > 3000:          
            cords_item_Verde = mt.mudanca_base(random.randint(1,8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
            item_Verde = coletaveis((61,145,64), 10, cords_item_Verde[0], cords_item_Verde[1])
            item_Verde_coletado = False
            Dama.velocidade -= 2
            Dama.cor  = (0,0,255)
    
    if item_vida_coletada:

        if last_item_time > 30000:

            cords_item_vida_drop = mt.mudanca_base(random.randint(1,8), random.randint(0,7), constants.FLOOR_SIZE*4, constants.MATRIZ_MUDA_BASE)
            Vida_item = coletaveis((255,0,226), 0, cords_item_vida_drop[0], cords_item_vida_drop[1])
            item_vida_coletada = False
                      
#IDENTIFICA????O DE COLIS??O COM O ITEM e CD para SPAWN
        
    distanciaPlayerObjeto = calcularDistanciaPontos(Dama.posicao_x, item_Verde.posicao_coletavel_x, Dama.posicao_y, item_Verde.posicao_coletavel_y)
    
    if distanciaPlayerObjeto <= 20:       
       
        Dama.velocidade += 2
        Dama.cor = (0,238,238)           
        item_Verde.posicao_coletavel_x = 0
        item_Verde.posicao_coletavel_y = 0
        item_Verde.color = (146, 244, 255)
        item_Verde.tamanho = 0
        static_timer = pg.time.get_ticks()
    
        item_Verde_coletado = True

    distanciaPlayerObjeto_2 = calcularDistanciaPontos(Dama.posicao_x, Vida_item.posicao_coletavel_x, Dama.posicao_y, Vida_item.posicao_coletavel_y)

    if distanciaPlayerObjeto_2 <= 20:
        if Dama.vida <= 3:
            Dama.vida += 1

        Vida_item.posicao_coletavel_x = 0
        Vida_item.posicao_coletavel_y = 0
        Vida_item.tamanho = 0
        static_timer = pg.time.get_ticks()
    
        item_vida_coletada = True
    
    distacia_da_bala_chao = calcularDistanciaPontos(Dama.posicao_x, posicao_da_bala_chao[0], Dama.posicao_y, posicao_da_bala_chao[1])

    if distacia_da_bala_chao <= 20:
        Dama.ammo = 1
        projetil.destino = None


    if static_timer:
        last_item_time = pg.time.get_ticks() - static_timer

#MOVIMENTA????O DO PROJ??TIL
   
    if Dama.ammo > 0:
        if Dama.cima:
            projetil.posicao_projetil_x = Dama.posicao_x
            projetil.posicao_projetil_y = Dama.posicao_y-20
            
        elif Dama.direita:
            projetil.posicao_projetil_x = Dama.posicao_x+20
            projetil.posicao_projetil_y = Dama.posicao_y
            
        elif Dama.esquerda:
            projetil.posicao_projetil_x = Dama.posicao_x-20
            projetil.posicao_projetil_y = Dama.posicao_y
            
        elif Dama.baixo:
            projetil.posicao_projetil_x = Dama.posicao_x
            projetil.posicao_projetil_y = Dama.posicao_y+20
            
    if projetil.destino != None:
        if not projetil.destino==(projetil.posicao_projetil_x, projetil.posicao_projetil_y):
            Dama.ammo = 0
            #
            if projetil.destino[0]>projetil.posicao_projetil_x:
                if (projetil.destino[0] - projetil.posicao_projetil_x)<5:
                    
                    projetil.posicao_projetil_x = projetil.destino[0]
                else:
                    projetil.posicao_projetil_x += 5
                    
            if projetil.destino[0]<projetil.posicao_projetil_x:
                if (projetil.posicao_projetil_x - projetil.destino[0])<5:
                    
                    projetil.posicao_projetil_x = projetil.destino[0]
                else:
                    projetil.posicao_projetil_x -= 5
            #
            if projetil.destino[1]>projetil.posicao_projetil_y:
                if (projetil.destino[1] - projetil.posicao_projetil_y)<5:
                    
                    projetil.posicao_projetil_y = projetil.destino[1]
                else:
                    projetil.posicao_projetil_y += 5
                    
            if projetil.destino[1]<projetil.posicao_projetil_y:
                if (projetil.posicao_projetil_y - projetil.destino[1])<5:
                    
                    projetil.posicao_projetil_y = projetil.destino[1]
                else:
                    projetil.posicao_projetil_y -= 5

    projetil.desenhar()
    pg.display.update()
    clock.tick(60)


    