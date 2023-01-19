import os

import csv
import random
import sqlite3

import pygame

pygame.init()
# параметры экрана
WIDTH = 800
HEIGHT = 640
scrolling = 200
BG = (218, 165, 32)
ROWS = 16
screen_scr = 0
bgScr = 0
COLS = 150
all_images = list()
# загрузка картинок
for i in range(21):
    im = pygame.image.load("imges/blocks/" + str(i) + ".png")
    im = pygame.transform.scale(im, (40, 40))
    all_images.append(im)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60
# загружаем картинки кнопок
startButton = pygame.image.load('imges/background/start_btn.png').convert_alpha()
exitButton = pygame.image.load('imges/background/exit_btn.png').convert_alpha()
restartButton = pygame.image.load('imges/background/restart_btn.png').convert_alpha()
back = pygame.image.load('imges/background/back.png').convert_alpha()
pygame.display.set_caption("Stalker")
connection = sqlite3.connect("stalker.sqlite")
re = connection.cursor().execute("SELECT * FROM player").fetchall()


GRAVITY = 2
font = pygame.font.SysFont('Futura', 40)
level = 2
all_world = []
# загрузка музыки
pygame.mixer.music.load('audio/music.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.2)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.2)
for r in range(ROWS):
    a = [-1] * COLS
    all_world.append(a)
# загрузка карты

with open("level" + str(level) + ".csv", newline='') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for x, ro in enumerate(r):

        for y, block in enumerate(ro):
            all_world[x][y] = int(block)

started = False

# прорисовка текста
def drawText(text, color, x, y):
    im = font.render(text, True, color)
    screen.blit(im, (x, y))

# класс группы спрайтов
class SpriteGroup(pygame.sprite.Group):

    def __init_(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)

# прорисовка фона
def forFon():
    screen.fill((0, 0, 0))
    w = back.get_width()

    for i in range(5):
        screen.blit(back, (w * i - bgScr, 0))

# класс спрайтов
class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


sprite_group = SpriteGroup()


# класс игрока
class Player(Sprite):
    def __init__(self, pX, pY, k, skorost, typePlayer, faza, am):
        # все переменные персонажа и врага
        super().__init__(sprite_group)
        self.a = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"]
        self.sprites = list()
        self.faza_now = 0
        self.action = 0
        self.isJump = False
        self.strelba = False
        self.typePlayer = typePlayer
        self.am = list(re[0])[-1]

        self.jumpSpeed = -55
        self.go_right = False
        self.go_left = False
        self.health = list(re[0])[2]
        self.Maxhealth = 5
        self.kolvoPul = 0
        self.deathList = []
        if typePlayer == "stalker":
            faza_type = ['calm', 'running', 'jumping', 'death']
            for h in faza_type:
                temp_list = []
                kolvo = len(os.listdir('imges/' + typePlayer + '/' + h))
                for i in range(kolvo):
                    img = pygame.image.load('imges/' + typePlayer + '/' + h + '/' + self.a[i] + '.png').convert_alpha()
                    img = pygame.transform.scale(img,
                                                 (int(img.get_width() * k), int(img.get_height() * k)))
                    temp_list.append(img)
                self.sprites.append(temp_list)

        if typePlayer == "enemy":
            faza_type = ['calm', 'running', 'running', 'death']
            for animation in faza_type:
                temp_list = []
                kolvo = len(os.listdir(f'imges/{typePlayer}/{animation}'))
                for i in range(kolvo):
                    img = pygame.image.load(f'imges/{typePlayer}/{animation}/{i}.png').convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * k), int(img.get_height() * k)))
                    temp_list.append(img)
                self.sprites.append(temp_list)
        self.image = self.sprites[self.action][self.faza_now]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.center = (pX, pY)
        self.pos = (pX, pY)
        self.k = k
        self.jump = False
        self.vlevoVpravo = 1
        self.menyem = False

        self.upDateTime = pygame.time.get_ticks()
        self.skorost = 5
        self.live = True
        self.cy = 0
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

    def drawPlayer(self):
        if self.typePlayer == 'enemy' and self.action == 3 and self.faza_now == 6:
            self.kill()

        if self.vlevoVpravo == 1:
            screen.blit(self.image, self.rect)
        else:
            screen.blit(pygame.transform.flip(self.image, -1, False), self.rect)

    def update(self):

        self.check_live()
        if self.typePlayer == "stalker":
            self.updatePlayer()
        else:
            self.update_enemy()
        if self.kolvoPul > 0:
            self.kolvoPul -= 1

    def updatePlayer(self):
        if self.health == 0:
            self.live = False

        self.image = self.sprites[self.action][self.faza_now]
        if pygame.time.get_ticks() - self.upDateTime > 100:
            self.faza_now += 1
            self.upDateTime = pygame.time.get_ticks()
        if self.faza_now >= len(self.sprites[self.action]):
            if self.action == 3:

                self.faza_now = len(self.sprites[self.action]) - 1
            else:

                self.faza_now = 0

    def check_live(self):
        if self.health <= 0:
            self.live = False
            self.health = 0
            self.skorost = 0
            self.proverka(3)

    def proverka(self, act):

        if self.action != act:
            self.action = act
            self.faza_now = 0

            self.upDateTime = pygame.time.get_ticks()

    def update_enemy(self):
        if self.health == 0:
            self.live = False

        self.image = self.sprites[self.action][self.faza_now]

        if pygame.time.get_ticks() - self.upDateTime > 100:
            self.faza_now += 1
            self.upDateTime = pygame.time.get_ticks()
        if self.faza_now >= len(self.sprites[self.action]):
            if self.action == 3:
                self.faza_now = len(self.sprites[self.action]) - 1
            else:
                self.faza_now = 0

    def strelb(self):
        if self.kolvoPul == 0 and self.am > 0:
            self.kolvoPul = 20

            if self.typePlayer == "stalker":
                puly1 = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.vlevoVpravo),
                               self.rect.centery, self.vlevoVpravo, "stalker")
                puly_group.add(puly1)
                self.am -= 1
                shot_fx.play()
            else:
                puly1 = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.vlevoVpravo),
                               self.rect.centery, self.vlevoVpravo, "enemy")
                puly_group.add(puly1)
                self.am -= 1
                shot_fx.play()

    def move(self):
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
        if self.rect.bottom > HEIGHT:
            self.health = 0
        newLevel = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            newLevel = True

        global screen_scr
        screen_scr = 0
        couldGoRight = True
        couldGoLeft = True
        dx = 0
        nY = 0
        if self.jump and not self.isJump:
            self.cy = -20
            self.jump = False
            self.isJump = True
        self.cy += GRAVITY
        if self.cy > 10:
            self.cy = 0
        nY += self.cy

        for block in world.world:
            if block[1].colliderect(self.rect.x, self.rect.y + nY, self.width, self.height):
                if self.cy >= 0:
                    self.cy = 0
                    nY = block[1].top - self.rect.bottom
                    self.isJump = False
                elif self.cy < 0:
                    self.cy = 0
                    nY = block[1].bottom - self.rect.top

        for block in world.world:
            if block[1].colliderect(self.rect.x + self.skorost, self.rect.y, self.width, self.height):
                couldGoRight = False
                dx = 0
                break
            else:
                couldGoRight = True
                dx = 0

        for block in world.world:
            if block[1].colliderect(self.rect.x - self.skorost, self.rect.y, self.width, self.height):
                couldGoLeft = False
                break
            else:
                couldGoLeft = True

        if self.go_left and couldGoLeft and self.rect.left - self.skorost > 0:
            self.rect.x -= self.skorost
            dx = -self.skorost
            self.menyem = True
            self.vlevoVpravo = -1
        if self.go_right and couldGoRight and self.rect.right + self.skorost < WIDTH:
            self.rect.x += self.skorost
            self.menyem = True
            dx = self.skorost
            self.vlevoVpravo = 1
        self.rect.y += nY

        if bgScr < world.len * 40 - WIDTH:
            if self.rect.right > WIDTH - scrolling:
                self.rect.x -= self.skorost
                screen_scr += -self.skorost
            if self.rect.left < scrolling and bgScr > abs(dx):
                self.rect.x += self.skorost
                screen_scr += self.skorost

        return screen_scr, newLevel

    def move_ai(self, go_left, go_right):

        if self.rect.bottom > HEIGHT:
            self.health = 0

        couldGoRight = True
        couldGoLeft = True
        dx = 0
        nY = 0
        dy = 0
        self.cy += GRAVITY
        if self.cy > 10:
            self.cy = 0
        nY += self.cy

        for block in world.world:
            if block[1].colliderect(self.rect.x, self.rect.y + nY, self.width, self.height):
                if self.cy >= 0:
                    self.cy = 0
                    nY = block[1].top - self.rect.bottom
                    self.isJump = False
                elif self.cy < 0:
                    self.cy = 0
                    nY = block[1].bottom - self.rect.top

        for block in world.world:
            if block[1].colliderect(self.rect.x + 5, self.rect.y - 20, self.width, self.height):
                couldGoRight = False
                break
            else:
                couldGoRight = True
        for block in world.world:
            if block[1].colliderect(self.rect.x - 5, self.rect.y - 20, self.width, self.height):
                couldGoLeft = False
                break
            else:
                couldGoLeft = True
        couldGoRightWater = True
        couldGoLeftWater = True
        for block in world.waterList:
            if block[1].colliderect(self.rect.x + 5, self.rect.y + 40, self.width, self.height):
                couldGoRightWater = False

                break
            else:
                couldGoRightWater = True

        for block in world.waterList:
            if block[1].colliderect(self.rect.x - 5, self.rect.y + 40, self.width, self.height):
                couldGoLeftWater = False
                break
            else:
                couldGoLeftWater = True

        self.rect.y += nY

        if self.rect.bottom > HEIGHT:
            self.health = 0

        if self.health > 0:
            if go_left and couldGoLeft and couldGoLeftWater:
                dx += -5
                self.menyem = True
                self.vlevoVpravo = -1
            if go_right and couldGoRight and couldGoRightWater:
                dx += 5
                self.menyem = False
                self.vlevoVpravo = 1

            self.cy += GRAVITY
            if self.cy > 10:
                self.cy
            dy += self.cy

            self.rect.x += dx

            self.rect.x += screen_scr
            self.rect.y += dy

    def ai(self):
        if self.live and stalker.live:
            if self.idling == False and random.randint(1, 200) == 1:
                self.proverka(0)
                self.idling = True
                self.idling_counter = 50
            if self.vision.colliderect(stalker.rect):
                self.proverka(0)
                self.strelb()
            else:
                if self.idling == False:
                    if self.vlevoVpravo == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move_ai(ai_moving_left, ai_moving_right)
                    self.proverka(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.vlevoVpravo, self.rect.centery)

                    if self.move_counter > 40:
                        self.vlevoVpravo *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False


# класс healthbar
class Bar():
    def __init__(self, x, y, now, max):
        self.x = x
        self.y = y
        self.now = now
        self.max = max

    def draw(self, now):
        self.now = now
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 150 * (stalker.health / 5), 20))
        pygame.draw.rect(screen, (255, 255, 255), (self.x - 2, self.y - 2, 154, 24), 1)


# класс кнопки
class Button():
    def __init__(self, x, y, image, k):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * k), int(height * k)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action


# класс для воды
class WaterBlock(Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + 20, y + (40 - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scr


# блок конца уровня
class ExitBlock(Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + 20, y + (40 - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scr


# класс декора
class Decor(Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + 20, y + (40 - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scr


# коробочки
class Box(Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)

        self.type = type
        self.image = pygame.image.load('imges/icons/' + type + '_box.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.x += screen_scr
        if pygame.sprite.collide_rect(self, stalker):
            if self.type == 'health':
                if stalker.health < 5:
                    stalker.health += 1
            elif self.type == 'ammo':
                if stalker.am < 20:
                    stalker.am = 20
                    connection = sqlite3.connect("stalker.sqlite")

                    re = connection.cursor().execute("SELECT * FROM player").fetchall()
                    connection.commit()
                    connection.close()

            self.kill()


# создание всех груп спрайтов
enemy_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
decor_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
puly_group = pygame.sprite.Group()


class AllWorld():
    def __init__(self):
        self.world = list()
        self.waterList = list()

    def load_world(self, d):
        self.len = len(all_world[0])
        for y, ro in enumerate(d):
            for x, block in enumerate(ro):
                # по номеру блока из csv понимаем какой тип
                if block >= 0:
                    im = all_images[block]
                    imRect = im.get_rect()
                    imRect.x = x * 40
                    imRect.y = y * 40
                    d = (im, imRect)
                    if block <= 8:
                        self.world.append(d)
                    elif 9 <= block <= 10:
                        self.waterList.append(d)
                        water = WaterBlock(im, x * 40, y * 40)
                        water_group.add(water)
                    elif 11 <= block <= 14:
                        dec = Decor(im, x * 40, y * 40)
                        decor_group.add(dec)
                    elif block == 15:

                        stalker = Player(x * 40, y * 40, 1.65, list(re[0])[2], "stalker", 0, list(re[0])[3])

                        healthBar = Bar(165, 45, stalker.health, stalker.Maxhealth)
                    elif block == 16:
                        enemy = Player(x * 40, y * 40, 1.65, 15, "enemy", 0, 20)
                        enemy_group.add(enemy)
                    elif block == 17:
                        box1 = Box(x * 40, y * 40 + 24, 'ammo')
                        box_group.add(box1)
                    elif block == 19:
                        box1 = Box(x * 40, y * 40 + 24, 'health')
                        box_group.add(box1)
                    elif block == 20:
                        exit = ExitBlock(im, x * 40, y * 40)
                        exit_group.add(exit)
        return stalker, healthBar

    def draw(self):
        for block in self.world:
            block[1][0] += screen_scr
            screen.blit(block[0], block[1])


world = AllWorld()
stalker, healthBar = world.load_world(all_world)


class Bullet(Sprite):
    def __init__(self, x, y, napravlenie, typePlayer):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.vlevovpavo = napravlenie
        self.typePlayer = typePlayer
        if self.typePlayer == "stalker":
            self.image = pygame.image.load('imges/icons/qbullet.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
        else:
            self.image = pygame.image.load('imges/icons/qbulletenemy.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)

    def update(self):
        self.rect.x += (self.vlevovpavo * self.speed) + screen_scr
        if self.rect.right < 0 or self.rect.left > WIDTH - 10:
            self.kill()
        for block in world.world:
            if block[1].colliderect(self.rect):
                self.kill()
        if pygame.sprite.spritecollide(stalker, puly_group, False):
            if stalker.live:
                stalker.health -= 1
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, puly_group, False):
                if stalker.live:
                    enemy.health -= 2
                    self.kill()


# метод для перезапуска презентации
def restart_level():
    enemy_group.empty()
    puly_group.empty()
    box_group.empty()
    decor_group.empty()
    water_group.empty()
    exit_group.empty()
    d = []
    for r in range(ROWS):
        a = [-1] * COLS
        d.append(a)
    return d


running = True
startB = Button(250, 200, startButton, 1)
exitB = Button(272, 400, exitButton, 1)
im = pygame.transform.scale(restartButton, (200, 90))
restartB = Button(300, 300, im, 1)
# игровой цикл
t = True
while running:
    pygame.display.update()
    clock.tick(FPS)
    if not t:
        # конечный экран
        screen.fill(BG)
        drawText("Вы прошли игру!", (0, 0, 0), 250, 250)
    else:
        if not started:
            pygame.display.flip()
            screen.fill(BG)
            if startB.draw(screen):
                started = True
            elif exitB.draw(screen):
                running = False
        else:
            # рисуем игру
            forFon()
            drawText('Количество пуль: ', (255, 255, 255), 10, 10)
            drawText('Здоровье: ', (255, 255, 255), 10, 40)
            stalker.update()
            stalker.drawPlayer()
            water_group.draw(screen)
            water_group.update()
            for enemy in enemy_group:
                pass
            world.draw()
            box_group.update()
            box_group.draw(screen)
            decor_group.draw(screen)
            decor_group.update()
            exit_group.draw(screen)
            exit_group.update()
            for enemy in enemy_group:
                enemy.ai()
                enemy.update()
                enemy.drawPlayer()
            healthBar.draw(stalker.health)
            for i in range(stalker.am):
                screen.blit(pygame.image.load('imges/icons/qbullet.png').convert_alpha(), (260 + (i * 10), 17))
            puly_group.update()
            puly_group.draw(screen)
            if not stalker.health:
                stalker.live = False

            if stalker.live:
                # обновляем данные в  бд
                connection = sqlite3.connect("stalker.sqlite")
                cur = connection.cursor()
                res1 = cur.execute("""UPDATE player SET ammo = ? WHERE id = 0 """, (stalker.am,)).fetchall()
                res2 = cur.execute("""UPDATE player SET health = ? WHERE id = 0 """, (stalker.health,)).fetchall()
                res2 = cur.execute("""UPDATE player SET level = ? WHERE id = 0 """, (level,)).fetchall()

                connection.commit()
                connection.close()
                if stalker.strelba:
                    stalker.strelb()
                if stalker.isJump:
                    stalker.proverka(2)
                elif stalker.go_left or stalker.go_right:
                    stalker.proverka(1)
                else:
                    stalker.proverka(0)

                screen_scr, newLevel = stalker.move()
                if newLevel and level == 2:
                    stalker.kill()
                    t = False
                    screen.fill(BG)
                    connection = sqlite3.connect("stalker.sqlite")
                    cur = connection.cursor()
                    res1 = cur.execute("""UPDATE player SET level = ? WHERE id = 0 """, (1,)).fetchall()

                    re = connection.cursor().execute("SELECT * FROM player").fetchall()

                    connection.commit()
                    connection.close()
                # запуск нового уровня
                if newLevel:
                    level += 1
                    bgScr = 0
                    if level <= 2:
                        all_world = restart_level()
                        with open("level" + str(level) + ".csv", newline='') as csvfile:
                            r = csv.reader(csvfile, delimiter=',')
                            for x, ro in enumerate(r):
                                for y, block in enumerate(ro):
                                    all_world[x][y] = int(block)
                        world = AllWorld()
                        stalker, healthBar = world.load_world(all_world)

                bgScr -= screen_scr

                pygame.display.update()
                puly_group.update()
                puly_group.draw(screen)

            else:

                screen_scr = 0

                if restartB.draw(screen):
                    bgScr = 0
                    connection = sqlite3.connect("stalker.sqlite")
                    cur = connection.cursor()
                    res1 = cur.execute("""UPDATE player SET ammo = ? WHERE id = 0 """, (20,)).fetchall()
                    res2 = cur.execute("""UPDATE player SET health = ? WHERE id = 0 """, (5,)).fetchall()
                    re = connection.cursor().execute("SELECT * FROM player").fetchall()

                    connection.commit()
                    connection.close()
                    # загрузка нового уровня
                    all_world = restart_level()
                    with open("level" + str(level) + ".csv", newline='') as csvfile:
                        r = csv.reader(csvfile, delimiter=',')
                        for x, ro in enumerate(r):
                            for y, block in enumerate(ro):
                                all_world[x][y] = int(block)
                    world = AllWorld()
                    stalker, healthBar = world.load_world(all_world)
    # реакция на нажатые клавиши
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.KEYDOWN:
            if stalker.live:
                if ev.key == pygame.K_a and t:
                    stalker.go_left = True
                if ev.key == pygame.K_d and t:
                    stalker.go_right = True
                if ev.key == pygame.K_w and t:
                    stalker.jump = True
                    jump_fx.play()
                if ev.key == pygame.K_SPACE and t:
                    stalker.strelba = True

            if ev.key == pygame.K_ESCAPE:
                running = False

        if ev.type == pygame.KEYUP:
            if ev.key == pygame.K_a:
                stalker.go_left = False
            if ev.key == pygame.K_d:
                stalker.go_right = False
            if ev.key == pygame.K_SPACE:
                stalker.strelba = False

pygame.quit()
