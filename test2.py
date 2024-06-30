import pygame
import sys
import os
import random
import csv
import time

pygame.init()

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("射击游戏")

clock = pygame.time.Clock()

img_list = []
for x in range(14):
    img = pygame.image.load(f"img/背景图片/atlas{x}.png")
    img = pygame.transform.scale(img, (20, 20))
    img_list.append(img)

# 玩家移动变量
move_left = False
move_right = False

# 定义颜色
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


# 定义精灵类
class role(pygame.sprite.Sprite):
    def __init__(self, role, x, y, scale, speed, health):
        super().__init__()
        self.speed = speed
        self.if_alive = True
        self.health = health
        self.max_health = health
        self.vel_y = 0
        self.jump = False
        self.in_air = False
        self.jump_count = 0
        self.role = role
        self.direction = "right"
        self.change_direction = False
        self.if_shoot = False
        self.count = 0
        self.animation_list = []
        self.frame_index = 0
        self.status_id = 0
        self.if_change = False
        self.gun = -1
        self.update_time = pygame.time.get_ticks()
        self.load_images(scale)
        self.image = self.animation_list[self.status_id][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def load_images(self, scale):
        status_list = ["idle", "run", "roll2", "attack", "die", "change"]
        if self.gun == 1:
            self.animation_list.clear()
            for status in status_list:
                temp = []
                number_of_frames = len(os.listdir(os.path.join("img", self.role, status + '1')))
                for i in range(number_of_frames):
                    img = pygame.image.load(
                        os.path.join("img", self.role, status + '1', f"contra-gun1-{status}_{i}.png"))
                    image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp.append(image)
                self.animation_list.append(temp)


        else:
            self.animation_list.clear()
            for status in status_list:
                temp = []
                number_of_frames = len(os.listdir(os.path.join("img", self.role, status + '0')))
                for i in range(number_of_frames):
                    img = pygame.image.load(
                        os.path.join("img", self.role, status + '0', f"contra-gun0-{status}_{i}.png"))
                    image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp.append(image)
                self.animation_list.append(temp)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.change_direction, False), self.rect)

    def move(self):
        move_x = 0
        move_y = 0

        if move_left:
            move_x = -self.speed
            self.change_direction = True
            self.direction = "left"
            self.status_id = 1
        if move_right:
            move_x = self.speed
            self.change_direction = False
            self.direction = "right"
            self.status_id = 1
        if self.jump:
            self.vel_y = -15
            self.jump = False

            self.status_id = 2
        if not move_left and not move_right and not self.jump:
            if self.if_alive:
                if self.if_shoot:
                    self.status_id = 3

                else:
                    self.status_id = 0

        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        move_y += self.vel_y

        # 检测与地面的碰撞
        for tile in world.objstacle_list:
            # 检测玩家与每个地面瓷砖x方向上的碰撞
            if tile[1].colliderect(self.rect.x + move_x, self.rect.y, self.width, self.height):
                move_x = 0
            # 检测玩家与瓷砖y方向上的碰撞
            if tile[1].colliderect(self.rect.x, self.rect.y + move_y, self.width, self.height):
                # 检测与地面底部的碰撞
                if self.vel_y < 0:
                    self.vel_y = 0
                    move_y = tile[1].bottom - self.rect.top
                # 检测与地面顶部的碰撞
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    move_y = tile[1].top - self.rect.bottom
                    self.jump_count = 0

        self.rect.x += move_x
        self.rect.y += move_y

    def shoot(self):
        self.status_id = 3
        self.if_shoot = True

        # 确定子弹类型
        type = "rocket" if self.gun == 1 else "bullet_main3"
        # rect.size[0]为子弹宽度，rect.size[1]为子弹高度，direction为子弹方向
        direction = 1 if self.direction == "right" else -1
        scale = 2
        bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * direction+scale*direction), self.rect.centery + 10, 5,
                        self.direction, type,scale)  # 创建一个向左射击的子弹对象
        bullet_group.add(bullet)  # 将子弹对象添加到精灵组中

    def die(self):
        if self.health <= 0:
            self.if_alive = False
            self.status_id = 4

    def change(self):
        self.frame_index = 0
        self.gun *= -1
        self.status_id = 5
        self.if_change = True

    def update_animation(self):
        animation_cooldown = 100

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.status_id]):
                self.frame_index = 0
            if self.status_id == 4:
                self.frame_index = len(self.animation_list[self.status_id]) - 1
                # 制造死亡时身体下落的效果
                self.count += 1
                if self.count <= 3:
                    self.rect.y += 10

            # 射击动画延迟设置
            if self.status_id == 3:
                self.count += 1
                if self.count == 3:
                    self.count = 0
                    self.if_shoot = False
                # 变换动画延迟设置
            if self.if_change:
                self.count += 1
                self.status_id = 5
                if self.count == 10:
                    self.count = 0
                    scale = 0.3
                    self.load_images(scale)
                    self.image = self.animation_list[self.status_id][self.frame_index]
                    self.if_change = False

            self.image = self.animation_list[self.status_id][self.frame_index]

    def update(self):
        self.die()
        if self.if_alive:
            self.move()
        self.update_animation()
        self.draw()


class enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, health, character):
        super().__init__()
        self.speed = speed
        self.move_left = True
        self.move_right = False
        self.if_alive = True
        self.health = health
        self.max_health = health
        self.character = character
        self.direction = "left"
        self.change_direction = False
        self.if_shoot = False
        self.shoot_cooldown = 0
        self.count = 0
        self.animation_list = []
        self.frame_index = 0
        self.status_id = 0
        self.update_time = pygame.time.get_ticks()
        self.load_images(scale)
        self.image = self.animation_list[self.status_id][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.move_count = 0
        self.if_stop = False
        self.stop_count = 0

    def load_images(self, scale):
        status_list = ["idle", "move", "attack"]
        self.animation_list.clear()
        for status in status_list:
            temp = []
            number_of_frames = len(os.listdir(f"img/enemy/{self.character}/{status}"))
            for i in range(number_of_frames):
                img = pygame.image.load(f"img/enemy/{self.character}/{status}/{self.character}-{status}_{i}.png")
                image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp.append(image)
            self.animation_list.append(temp)

    def check_alive(self):
        if self.health <= 0:
            self.if_alive = False
            self.kill()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.change_direction, False), self.rect)

    def move(self):
        move_x = 0
        move_y = 0

        if self.move_left:
            move_x = -self.speed
            self.change_direction = False
            self.direction = "left"
            self.status_id = 1

        if self.move_right:
            move_x = self.speed
            self.change_direction = True
            self.direction = "right"
            self.status_id = 1

        if not self.move_left and not self.move_right:
            if self.if_alive:
                self.status_id = 0

        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        move_y += self.vel_y

        # 检测与地面的碰撞
        for tile in world.objstacle_list:
            # 检测玩家与每个地面瓷砖x方向上的碰撞
            if tile[1].colliderect(self.rect.x + move_x, self.rect.y, self.width,
                                   self.height):  # 这里用self,width,height而不用self.image.get_width()是因为静止和奔跑的图片大小不一样，会导致碰撞检测出错
                move_x = 0
            # 检测玩家与瓷砖y方向上的碰撞
            if tile[1].colliderect(self.rect.x, self.rect.y + move_y, self.image.get_width(), self.image.get_height()):
                # 检测与地面底部的碰撞
                if self.vel_y < 0:
                    self.vel_y = 0
                    move_y = tile[1].bottom - self.rect.top
                # 检测与地面顶部的碰撞
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    move_y = tile[1].top - self.rect.bottom

        self.rect.x += move_x
        self.rect.y += move_y

    def shoot(self):
        self.status_id = 2
        self.if_shoot = True
        if self.direction == "left":
            direction = -1
        else:
            direction = 1

        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 50
            # 确定子弹类型
            if self.character == "miniboss":
                scale =4
            else:
                scale = 2
            # rect.size[0]为子弹宽度，rect.size[1]为子弹高度，direction为子弹方向
            bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * direction+scale*direction), self.rect.centery + 10, 5,
                            self.direction, self.character+"_bullet",scale)  # 创建一个向左射击的子弹对象
            bullet_group.add(bullet)  # 将子弹对象添加到精灵组中

    def update_animation(self):
        animation_cooldown = 100

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.status_id]):
                self.frame_index = 0

            # 射击动画延迟设置
            if self.status_id == 3:
                self.count += 1
                if self.count == 3:
                    self.count = 0
                    self.if_shoot = False
            self.image = self.animation_list[self.status_id][self.frame_index]

    def ai(self):
        if self.if_alive:
            if self.if_stop == False and random.randint(0, 200) == 1:
                self.status_id = 0
                self.if_stop = True
                self.stop_count = 50

            if abs(self.rect.centerx -player.rect.centerx)<400:
                if player.if_alive:
                    if self.rect.centerx -player.rect.centerx > 0:
                        if self.direction == "right":
                            self.change_direction = False
                            self.direction = "left"
                            self.move_left = True
                            self.move_right = False
                            self.draw()


                    elif self.rect.centerx -player.rect.centerx <0:
                       if self.direction=="left":
                            self.change_direction = True
                            self.direction = "right"
                            self.move_left = False
                            self.move_right = True
                            self.draw()


                    self.shoot()

            else:
                if self.if_stop == False:
                    if self.direction == "right":
                        self.move_right = True
                        self.move_left = False

                    else:
                        self.move_left = True
                        self.move_right = False

                    self.move()
                    self.move_count += 1
                    direction = 1 if self.direction == "right" else -1


                    if self.move_count == 100:
                        direction *= -1
                        self.move_count *= -1
                        self.direction = "right" if direction == 1 else "left"


                else:
                    self.stop_count -= 1
                    if self.stop_count <= 0:
                        self.if_stop = False

    def update(self):
        self.check_alive()
        self.ai()
        self.update_animation()
        self.draw()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


class Health_bar(pygame.sprite.Sprite):
    def __init__(self, x, y, health, max_health):
        super().__init__()
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        # 计算血条的比率
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class prop(pygame.sprite.Sprite):
    def __init__(self, x, y, type, scale):
        super().__init__()
        img = pygame.image.load(f"img/prop/{type}.png")
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.type = type

    def update(self, player):

        if self.rect.colliderect(player.rect):

            if self.type == "health":
                if player.health < player.max_health:
                    player.health += 25
            elif self.type == "mine":
                player.health -= 30
                explosion_group.add(explosion(self.rect.centerx, self.rect.centery, 0.5))
            elif self.type == "coin":
                score = 100
            self.kill()

    def draw(self):
        screen.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, direction, type,scale):
        super().__init__()
        self.speed = speed
        self.direction = direction
        self.type = type
        self.image = pygame.image.load(f"{type}.png")
        self.scale = scale
        self.image = pygame.transform.scale(self.image, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, True if self.direction == "left" else False, False), self.rect)


    def update(self):

        if self.direction == "left":
            self.rect.x -= self.speed
        if self.direction == "right":
            self.rect.x += self.speed
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH:
            self.kill()

            # 检测子弹的碰撞
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.if_alive:
                player.health -= 10
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    if self.type == "bullet_main3":
                        enemy.health -= 25
                    else:
                        enemy.health -= 50
                        explosion_group.add(explosion(enemy.rect.centerx, enemy.rect.centery, 0.5))
                    self.kill()


class explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        self.images = []
        for i in range(1, 5):
            img = pygame.image.load(os.path.join("img", "explosion", f"exp{i}.png"))
            image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(image)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.update_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.update_time > 50:
            self.update_time = pygame.time.get_ticks()
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]
                self.frame_index += 1


# img_list = []
# for x in range(14):
# 	img = pygame.image.load(f"img/背景图片/atlas{x}.png")
# 	img = pygame.transform.scale(img, (TILE_SIZE,TILE_SIZE))
# 	img_list.append(img)
#
ROWS = 25
COLS = 500
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21

class World():
    def __init__(self):
        self.objstacle_list = []  # 障碍列表

    def process_data(self, data):
        # 迭代每个值更每个元素的值
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    if 0 <= tile <= 13:
                        img = pygame.image.load(f"img/背景图片/atlas{tile}.png")
                        img_rect = img.get_rect()
                        img_rect.x = x * TILE_SIZE
                        img_rect.y = y * TILE_SIZE
                        tile_data = (img, img_rect)
                        self.objstacle_list.append(tile_data)
                    elif tile==21:
                        player= role("player", x * TILE_SIZE, y * TILE_SIZE, 0.3, 5, 100)
                        health_bar = Health_bar(10, 10, player.health, player.max_health)
                    elif tile==22:
                        enemy1 =enemy(x * TILE_SIZE, y * TILE_SIZE,  0.3, 1, 100,"enemy1")
                        enemy_group.add(enemy1)
                    elif tile==23:
                        enemy2 =enemy(x * TILE_SIZE, y * TILE_SIZE,  0.3, 1, 100,"enemy2")
                        enemy_group.add(enemy2)
                    elif tile==24:
                        enemy3 =enemy(x * TILE_SIZE, y * TILE_SIZE,  0.3, 1, 100,"enemy3")
                        enemy_group.add(enemy3)
                    elif tile==25:
                        sniper =enemy(x * TILE_SIZE, y * TILE_SIZE,  0.3, 1, 100,"sniper")
                        enemy_group.add(sniper)
                    elif tile==26:
                        miniboss =enemy(x * TILE_SIZE, y * TILE_SIZE,  0.3, 1, 100,"miniboss")
                        enemy_group.add(miniboss)
                    elif tile==18:
                        prop_group.add(prop(x * TILE_SIZE, y * TILE_SIZE, "coin", 0.3))
                    elif tile==19:
                        prop_group.add(prop(x * TILE_SIZE, y * TILE_SIZE, "health", 0.5))
                    elif tile==20:
                        prop_group.add(prop(x * TILE_SIZE, y * TILE_SIZE, "mine", 0.4))
        return player,health_bar


    def draw(self):
        for tile in self.objstacle_list:
            screen.blit(tile[0], tile[1])


# 创建空白瓷砖列表
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# 加载级别地图数据
with open("3.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for y, row in enumerate(reader):
        for x, tile in enumerate(row):
            world_data[y][x] = int(tile)






# 创建道具
prop_group = pygame.sprite.Group()



enemy_group = pygame.sprite.Group()


bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


world = World()
player,health_bar=world.process_data(world_data)






bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
run = True

while run:
    clock.tick(120)
    screen.fill((144, 201, 120))

    world.draw()

    # 绘制血条
    health_bar.draw(player.health)

    # 道具
    prop_group.update(player)
    prop_group.draw(screen)

    # 角色
    player.update()

    enemy_group.update()

    # 移动角色
    keys = pygame.key.get_pressed()
    move_left = keys[pygame.K_LEFT]
    move_right = keys[pygame.K_RIGHT]
    # player.jump = keys[pygame.K_UP]
    # if keys[pygame.K_SPACE]: 原本方案，但发现按一次空格会导致子弹持续射击
    #     player.shoot()

    for bullet in bullet_group:
        bullet.update()
        bullet.draw()

    # 绘制爆炸
    explosion_group.update()
    explosion_group.draw(screen)

    # 碰撞检测

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
            if event.key == pygame.K_UP:
                if player.jump_count < 2:
                    player.jump = True
                    player.jump_count += 1
            if event.key == pygame.K_c:
                player.change()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                pass

    pygame.display.update()

pygame.quit()
sys.exit()
