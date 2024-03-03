import math
import random
import time

import pygame


class AnimatedSprite:
    def __init__(self, game, e_type, img_dur=5):
        self.game = game
        self.type = e_type
        self.image = None
        self.images = ()
        self.img_duration = img_dur
        self.flip = False
        self.frame = 0

    def set_action(self, action):
        self.images = self.game.assets[self.type + ('/' + action if action != '' else '')]

    def update_animation(self):
        self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        self.image = self.images[int(self.frame / self.img_duration)]


class SpikeSprite(pygame.sprite.Sprite):
    def __init__(self, game, top_left):
        super().__init__()
        self.game = game
        self.image = self.game.assets['spike']
        self.rect = self.image.get_rect()
        self.rect.topleft = top_left
        self.mask = pygame.mask.from_surface(self.image)


class SpikeManage:
    def __init__(self, game):
        self.game = game
        self.player_killer_group = pygame.sprite.Group()

        for i in range(0, 800, 32):
            self.generate(i, 0)

    def generate(self, x: int, y: int):
        SpikeSprite(self.game, (x, y)).add(self.player_killer_group)

    def update(self):
        self.player_killer_group.update()
        self.player_killer_group.draw(self.game.screen)


class Blood(pygame.sprite.Sprite):
    def __init__(self, game, center):
        super().__init__()
        self.game = game
        self.image = random.choice(self.game.assets['blood']).convert_alpha()
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
        elif self.rect.right + self.hspeed > self.game.screen.get_width():
            self.hspeed = self.game.screen.get_width() - self.rect.right
            self.vspeed = 0
            self.gravity = 0
        if self.rect.bottom + self.vspeed > self.game.screen.get_height():
            self.hspeed = 0
            self.vspeed = self.game.screen.get_height() - self.rect.bottom
            self.gravity = 0
        self.rect = self.rect.move(self.hspeed, self.vspeed)


class BloodManage:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.blood_group = pygame.sprite.Group()
        self.death_time = 0

    def update(self):
        if time.time() <= self.death_time:
            for _ in range(40):
                Blood(self.game, self.player.rect.center).add(self.blood_group)
        self.blood_group.update()
        self.blood_group.draw(self.game.screen)


class BulletSprite(pygame.sprite.Sprite):
    def __init__(self, game, player):
        super().__init__()
        self.game = game
        self.images = self.game.assets['bullet']
        self.image = self.images[0]
        self.img_duration = 5
        self.frame = 0

        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center

        self.hspeed = (-1 if player.flip else 1) * 15
        self.death_time = time.time() + 1

    def update_animation(self):
        self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        self.image = self.images[int(self.frame / self.img_duration)]

    def update(self):
        if (self.rect.left + self.hspeed < 0 or self.rect.right + self.hspeed > self.game.screen.get_width() or
                time.time() > self.death_time):
            self.kill()
        self.rect = self.rect.move(self.hspeed, 0)
        self.update_animation()


class BulletManage:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.bullet_group = pygame.sprite.Group()
        self.limit = 4

    def generate(self):
        if len(self.bullet_group) < self.limit:
            self.game.sfx['shoot'].play()
            BulletSprite(self.game, self.player).add(self.bullet_group)

    def update(self):
        self.bullet_group.update()
        self.bullet_group.draw(self.game.screen)


class PlayerSprite(AnimatedSprite):
    def __init__(self, center, game):
        super().__init__(game, 'player', 7)
        self.rect = self.game.assets['maskPlayer'].get_rect()
        self.mask = pygame.mask.from_surface(self.game.assets['maskPlayer'])

        self.set_action('idle')

        self.rect.center = center
        self.spike_manage = self.game.spike_manage

        self.hspeed = 0
        self.vspeed = 0
        self.jump_speed = 8.5
        self.djump_speed = 7
        self.djump = True
        self.gravity = 0.3
        self.max_hspeed = 2
        self.max_vspeed = 9

        self.bullet_manage = BulletManage(self.game, self)

        self.blood_manage = BloodManage(self.game, self)
        self.game_over_show = 0
        self.dead = False

    def kill(self):
        self.game_over_show = time.time() + 0.75
        self.blood_manage.death_time = time.time() + 0.4
        self.dead = True
        pygame.mixer.music.load('data/sounds/sndOnDeath.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

    def shoot(self):
        self.bullet_manage.generate()

    def jump(self):
        if self.rect.bottom >= self.game.screen.get_height():
            self.vspeed = -self.jump_speed
            self.djump = True
            self.game.sfx['jump'].play()
        elif self.djump:
            self.vspeed = -self.djump_speed
            # self.djump = False  # FIXME double jump
            self.game.sfx['djump'].play()

    def vjump(self):
        self.vspeed *= 0.45

    def update(self):
        if self.dead:
            self.blood_manage.update()
            if time.time() > self.game_over_show:
                self.game.screen.blit(self.game.assets['game_over'], (0, 140))
            return

        # collision with player killers
        if pygame.sprite.spritecollideany(self, self.spike_manage.player_killer_group, pygame.sprite.collide_mask):
            self.kill()

        # get left & right key input
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.hspeed = self.max_hspeed
            self.set_action('run')
            self.flip = False
        elif key_pressed[pygame.K_LEFT]:
            self.hspeed = -self.max_hspeed
            self.set_action('run')
            self.flip = True
        else:
            self.hspeed = 0
            self.set_action('idle')

        # gravity
        self.vspeed += self.gravity

        # collision with room edges & max vspeed limit
        if self.rect.left + self.hspeed < 0 or self.rect.right + self.hspeed > self.game.screen.get_width():
            self.hspeed = 0
        if abs(self.vspeed) > self.max_vspeed:
            self.vspeed = (self.vspeed > 0) * self.max_vspeed
        if self.rect.bottom + self.vspeed > self.game.screen.get_height():
            self.vspeed = self.game.screen.get_height() - self.rect.bottom

        if self.rect.bottom < self.game.screen.get_height():
            if self.vspeed < -0.05:
                self.set_action('jump')
            if self.vspeed > 0.05:
                self.set_action('fall')

        # move the player
        self.rect = self.rect.move(self.hspeed, self.vspeed)

        self.bullet_manage.update()
        self.update_animation()
        self.game.screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect.move(-10, -11))
