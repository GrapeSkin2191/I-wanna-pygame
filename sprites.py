import math
import random
import time

import pygame


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, name: str):
        super().__init__()
        self.image = pygame.image.load(name).convert_alpha()
        self.rect = self.image.get_rect()


class GameOverSprite(BaseSprite):
    def __init__(self, game_manage):
        super().__init__('data/images/sprGAMEOVER.png')
        self.game_manage = game_manage
        self.rect.center = (400, 300)
        self.appear_time = time.time() + 1

    def update(self):
        if time.time() > self.appear_time:
            self.game_manage.screen.blit(self.image, self.rect)


class SpikeSprite(BaseSprite):
    def __init__(self, top_left: tuple[int, int]):
        super().__init__('data/images/sprSpike.png')
        self.rect.topleft = top_left
        self.mask = pygame.mask.from_surface(self.image)


class SpikeManage:
    def __init__(self, game_manage):
        self.game_manage = game_manage
        self.player_killer_group = pygame.sprite.Group()

        for i in range(0, 800, 32):
            self.generate(i, 0)

    def generate(self, x: int, y: int):
        SpikeSprite((x, y)).add(self.player_killer_group)

    def update(self):
        self.player_killer_group.update()
        self.player_killer_group.draw(self.game_manage.screen)


class Blood(pygame.sprite.Sprite):
    def __init__(self, game_manage, center):
        super().__init__()
        self.game_manage = game_manage
        image_list = ('data/images/sprBlood1.png', 'data/images/sprBlood2.png', 'data/images/sprBlood3.png')
        self.image = pygame.image.load(random.choice(image_list)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.gravity = random.uniform(0.1, 0.3)
        self.hspeed = random.uniform(-6.0, 6.0)
        self.vspeed = (1 if random.random() >= 0.5 else -1) * math.sqrt(36 - math.pow(self.hspeed, 2))

    def update(self):
        self.vspeed += self.gravity
        if self.rect.left + self.hspeed < 0:
            self.hspeed = -self.rect.left
            self.vspeed = 0
            self.gravity = 0
        elif self.rect.right + self.hspeed > self.game_manage.screen.get_width():
            self.hspeed = self.game_manage.screen.get_width() - self.rect.right
            self.vspeed = 0
            self.gravity = 0
        if self.rect.bottom + self.vspeed > self.game_manage.screen.get_height():
            self.hspeed = 0
            self.vspeed = self.game_manage.screen.get_height() - self.rect.bottom
            self.gravity = 0
        self.rect = self.rect.move(self.hspeed, self.vspeed)


class BloodManage:
    def __init__(self, game_manage, player):
        self.game_manage = game_manage
        self.player = player
        self.blood_group = pygame.sprite.Group()
        self.death_time = 0

    def update(self):
        if time.time() <= self.death_time:
            for _ in range(40):
                Blood(self.game_manage, self.player.rect.center).add(self.blood_group)
        self.blood_group.update()
        self.blood_group.draw(self.game_manage.screen)


class BulletSprite(BaseSprite):
    def __init__(self, game_manage, player):
        super().__init__('data/images/sprBullet1.png')
        self.image_list = (pygame.image.load('data/images/sprBullet1.png').convert_alpha(),
                           pygame.image.load('data/images/sprBullet2.png').convert_alpha())
        self.image_speed = 0.1
        self.image_cur = 0
        self.last_update = time.time()

        self.rect.center = player.rect.center
        self.game_manage = game_manage

        self.hspeed = player.direction * 15
        self.kill_time = self.last_update + 1

    def update(self):
        if (self.rect.left + self.hspeed < 0 or self.rect.right + self.hspeed > self.game_manage.screen.get_width() or
                self.kill_time <= time.time()):
            self.kill()

        self.rect.centerx += self.hspeed

        now = time.time()
        if now - self.last_update >= self.image_speed:
            self.image_cur = not self.image_cur
            self.image = self.image_list[self.image_cur]
            self.last_update = now


class BulletManage:
    def __init__(self, game_manage, player):
        self.game_manage = game_manage
        self.player = player
        self.bullet_group = pygame.sprite.Group()
        self.limit = 4

    def generate(self):
        if len(self.bullet_group) < self.limit:
            BulletSprite(self.game_manage, self.player).add(self.bullet_group)

    def update(self):
        self.bullet_group.update()
        self.bullet_group.draw(self.game_manage.screen)


class PlayerSprite(BaseSprite):
    def __init__(self, center: tuple[int, int], game_manage, spike_manage):
        super().__init__('data/images/maskPlayer.png')
        self.image_type = 0
        self.image_cur = 0
        self.image_dict = ((pygame.image.load('data/images/sprPlayerIdle1.png').convert_alpha(),
                            pygame.image.load('data/images/sprPlayerIdle2.png').convert_alpha(),
                            pygame.image.load('data/images/sprPlayerIdle3.png').convert_alpha(),
                            pygame.image.load('data/images/sprPlayerIdle4.png').convert_alpha()),
                           (pygame.image.load('data/images/sprPlayerFall1.png').convert_alpha(),
                            pygame.image.load('data/images/sprPlayerFall2.png').convert_alpha()),
                           (pygame.image.load('data/images/sprPlayerJump1.png').convert_alpha(),
                            pygame.image.load('data/images/sprPlayerJump2.png').convert_alpha()),
                           (pygame.image.load('data/images/sprPlayerRunning1.png').convert_alpha(),
                            pygame.image.load('data/images/sprPlayerRunning2.png').convert_alpha(),
                            pygame.image.load('data/images/sprPlayerRunning3.png').convert_alpha(),
                            pygame.image.load('data/images/sprPlayerRunning4.png').convert_alpha()))
        self.image_player = self.image_dict[0][0]
        self.direction = 1
        self.image_speed = 0.1
        self.last_update = time.time()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.center = center
        self.game_manage = game_manage
        self.spike_manage = spike_manage

        self.hspeed = 0
        self.vspeed = 0
        self.jump_speed = 8.5
        self.djump_speed = 7
        self.djump = True
        self.gravity = 0.35
        self.max_hspeed = 2
        self.max_vspeed = 9

        self.bullet_manage = BulletManage(self.game_manage, self)

        self.blood_manage = BloodManage(self.game_manage, self)
        self.gameover = None
        self.dead = False

        self.sounds = (pygame.mixer.Sound('data/sounds/sndJump.wav'),
                       pygame.mixer.Sound('data/sounds/sndDJump.wav'),
                       pygame.mixer.Sound('data/sounds/sndShoot.wav'))
        for sound in self.sounds:
            sound.set_volume(0.5)

    def kill(self):
        self.gameover = GameOverSprite(self.game_manage)
        self.blood_manage.death_time = time.time() + 0.4
        self.dead = True
        pygame.mixer.music.load('data/sounds/sndOnDeath.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

    def shoot(self):
        self.bullet_manage.generate()
        self.sounds[2].play()

    def jump(self):
        if self.rect.bottom >= self.game_manage.screen.get_height():
            self.vspeed = -self.jump_speed
            self.djump = True
            self.sounds[0].play()
        elif self.djump:
            self.vspeed = -self.djump_speed
            # self.djump = False  # FIXME double jump
            self.sounds[1].play()

    def vjump(self):
        self.vspeed *= 0.45

    def update(self):
        if self.dead:
            self.blood_manage.update()
            self.gameover.update()
            return

        # collision with player killers
        if pygame.sprite.spritecollideany(self, self.spike_manage.player_killer_group, pygame.sprite.collide_mask):
            self.kill()

        # get left & right key input
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.hspeed = self.max_hspeed
            self.image_type = 3
            if self.direction == -1:
                self.image_player = pygame.transform.flip(self.image_player, 1, 0)
                self.direction = 1
        elif key_pressed[pygame.K_LEFT]:
            self.hspeed = -self.max_hspeed
            self.image_type = 3
            if self.direction == 1:
                self.image_player = pygame.transform.flip(self.image_player, 1, 0)
                self.direction = -1
        else:
            self.hspeed = 0
            self.image_type = 0

        # gravity
        self.vspeed += self.gravity

        # collision with room edges & max vspeed limit
        if self.rect.left + self.hspeed < 0 or self.rect.right + self.hspeed > self.game_manage.screen.get_width():
            self.hspeed = 0
        if abs(self.vspeed) > self.max_vspeed:
            self.vspeed = (self.vspeed > 0) * self.max_vspeed
        if self.rect.bottom + self.vspeed > self.game_manage.screen.get_height():
            self.vspeed = self.game_manage.screen.get_height() - self.rect.bottom

        if self.rect.bottom < self.game_manage.screen.get_height():
            if self.vspeed < -0.05:
                self.image_type = 2
            if self.vspeed > 0.05:
                self.image_type = 1

        # move the player
        self.rect = self.rect.move(self.hspeed, self.vspeed)

        # change player image
        now = time.time()
        if now - self.last_update >= self.image_speed:
            self.image_cur += 1
            if self.image_cur >= len(self.image_dict[self.image_type]):
                self.image_cur = 0
            self.image_player = self.image_dict[self.image_type][self.image_cur]
            if self.direction == -1:
                self.image_player = pygame.transform.flip(self.image_player, 1, 0)
            self.last_update = now

        self.game_manage.screen.blit(self.image_player, self.rect.move(-10, -11))
        self.bullet_manage.update()
