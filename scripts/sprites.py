import math
import random

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


class Block(pygame.sprite.Sprite):
    def __init__(self, game, variant, top_left, flip):
        super().__init__()
        self.game = game
        self.image = pygame.transform.flip(self.game.assets['block'][variant], flip[0], flip[1])
        self.rect = self.image.get_rect()
        self.rect.topleft = top_left


class BlockManage:
    def __init__(self, game):
        self.game = game
        self.block_group = pygame.sprite.Group()

    def create(self, variant, top_left, flip):
        Block(self.game, variant, top_left, flip).add(self.block_group)

    def update(self):
        self.block_group.update()
        self.block_group.draw(self.game.screen)


class SpikeSprite(pygame.sprite.Sprite):
    def __init__(self, game, top_left, flip):
        super().__init__()
        self.game = game
        self.image = pygame.transform.flip(self.game.assets['spike'], flip[0], flip[1])
        self.rect = self.image.get_rect()
        self.rect.topleft = top_left
        self.mask = pygame.mask.from_surface(self.image)


class SpikeManage:
    def __init__(self, game):
        self.game = game
        self.player_killer_group = pygame.sprite.Group()

    def create(self, top_left, flip):
        SpikeSprite(self.game, top_left, flip).add(self.player_killer_group)

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
        speed = random.uniform(3, 6)
        angle = random.uniform(0, math.pi * 2)
        self.hspeed = math.cos(angle) * speed
        self.vspeed = math.sin(angle) * speed

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
    def __init__(self, game, center, life):
        self.game = game
        self.center = center
        self.blood_group = pygame.sprite.Group()
        self.death_time = self.game.time + life

    def update(self):
        if self.game.time <= self.death_time:
            for _ in range(40):
                Blood(self.game, self.center).add(self.blood_group)
        self.blood_group.update()
        self.blood_group.draw(self.game.screen)


class BulletSprite(pygame.sprite.Sprite):
    def __init__(self, game, center, direction):
        super().__init__()
        self.game = game
        self.images = self.game.assets['bullet']
        self.img_duration = 5
        self.frame = 0
        self.rect = self.images[0].get_rect()
        self.rect.center = center

        self.hspeed = direction * 14
        self.life = 0
        self.death_time = self.game.time + 42

    def update_animation(self):
        self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        self.image = self.images[int(self.frame / self.img_duration)]

    def update(self):
        self.life += 1
        if (self.rect.left + self.hspeed < 0 or self.rect.right + self.hspeed > self.game.screen.get_width() or
                self.game.time > self.death_time):
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
            (BulletSprite(self.game, self.player.rect.center, (-1 if self.player.flip else 1))
             .add(self.bullet_group))

    def update(self):
        self.bullet_group.update()
        self.bullet_group.draw(self.game.screen)


class PlayerSprite(AnimatedSprite):
    def __init__(self, game, top_left):
        super().__init__(game, 'player', 7)
        self.rect = self.game.assets['maskPlayer'].get_rect()
        self.mask = pygame.mask.from_surface(self.game.assets['maskPlayer'])

        self.set_action('idle')

        self.rect.topleft = top_left

        self.hspeed = 0
        self.vspeed = 0
        self.jump_speed = 7
        self.djump_speed = 6
        self.has_djump = False
        self.gravity = 0.3
        self.max_hspeed = 2
        self.max_vspeed = 9
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.air_time = 0

        self.bullet_manage = BulletManage(self.game, self)
        self.blood_manage = None

        self.game_over_show = 0
        self.dead = False

    def die(self):
        self.blood_manage = BloodManage(self.game, self.rect.center, 20)
        self.game_over_show = self.game.time + 30
        self.dead = True
        pygame.mixer.music.load('data/sounds/sndOnDeath.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

    def shoot(self):
        self.bullet_manage.generate()

    def jump(self):
        if self.air_time <= 2:
            self.vspeed = -self.jump_speed
            self.has_djump = True
            self.game.sfx['jump'].play()
        elif self.has_djump:
            self.vspeed = -self.djump_speed
            # self.has_djump = False  # FIXME double jump
            self.game.sfx['djump'].play()

    def vjump(self):
        if self.vspeed < -0.05:
            self.vspeed *= 0.45

    def update(self):
        if self.dead:
            self.blood_manage.update()
            self.bullet_manage.update()
            if self.game.time > self.game_over_show:
                self.game.screen.blit(self.game.assets['game_over'], (0, 140))
            return

        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.rect.x += self.hspeed
        entity_rect = self.rect.copy()
        for rect in self.game.tilemap.physics_rects_around(self.rect.center):
            if entity_rect.colliderect(rect):
                if self.hspeed > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if self.hspeed < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.rect.x = entity_rect.x
        if self.collisions['left'] or self.collisions['right']:
            self.hspeed = 0

        self.rect.y += self.vspeed
        entity_rect = self.rect.copy()
        for rect in self.game.tilemap.physics_rects_around(self.rect.center):
            if entity_rect.colliderect(rect):
                if self.vspeed > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if self.vspeed < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.rect.y = entity_rect.y
        if self.collisions['up'] or self.collisions['down']:
            self.vspeed = 0

        if pygame.sprite.spritecollideany(self, self.game.spike_manage.player_killer_group, pygame.sprite.collide_mask):
            self.die()

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

        if self.collisions['down']:
            self.air_time = 0
        else:
            self.air_time += 1

        self.vspeed += self.gravity

        if abs(self.vspeed) > self.max_vspeed:
            self.vspeed = (self.vspeed > 0) * self.max_vspeed

        if self.air_time > 2:
            if self.vspeed < -0.05:
                self.set_action('jump')
            elif self.vspeed > 0.05:
                self.set_action('fall')

        self.bullet_manage.update()
        self.update_animation()
        self.game.screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect.move(-11, -11))
        # self.game.screen.blit(self.game.assets['maskPlayer'], self.rect)
