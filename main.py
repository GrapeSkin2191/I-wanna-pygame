import sys

import pygame

from scripts.sprites import PlayerSprite, SpikeManage, BlockManage
from scripts.tilemap import TileMap
from scripts.utils import load_image, load_images, load_images_to_dict, load_sound

SIZE = (800, 608)
FPS = 60


class Game:
    def __init__(self, size: tuple[int, int], fps: int):
        pygame.init()
        pygame.display.set_caption('I wanna pygame')
        pygame.display.set_icon(pygame.image.load('fruit32.ico'))

        self.size = size
        self.fps = fps
        self.screen = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.time = 0

        self.assets = {
            'maskPlayer': load_image('player/maskPlayer.png'),
            'player/idle': load_images('player/idle'),
            'player/fall': load_images('player/fall'),
            'player/jump': load_images('player/jump'),
            'player/run': load_images('player/run'),
            'bullet': load_images('bullet'),
            'game_over': load_image('GAMEOVER.png'),
            'spike': load_image('spike.png'),
            'blood': load_images('blood'),
            'block': load_images_to_dict('block')
        }

        self.sfx = {
            'jump': load_sound('sndJump.wav'),
            'djump': load_sound('sndDjump.wav'),
            'shoot': load_sound('sndShoot.wav')
        }

        self.tilemap = None
        self.block_manage = None
        self.spike_manage = None
        self.player = None

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.block_manage = BlockManage(self)
        for block in self.tilemap.extract('block', True):
            self.block_manage.create(block['variant'], block['pos'], block['flip'])

        self.spike_manage = SpikeManage(self)
        for spike in self.tilemap.extract('spike'):
            self.spike_manage.create(spike['pos'], spike['flip'])

        self.player = PlayerSprite(self, self.tilemap.player_pos)

    def stop(self):
        pygame.quit()
        sys.exit()

    def check_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.stop()
                elif event.key == pygame.K_F2:  # TODO may cause problems
                    self.run()
                elif event.key == pygame.K_F4:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_q:
                    self.player.die()
                elif event.key == pygame.K_z:
                    self.player.shoot()
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.player.jump()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.player.vjump()

    def run(self):
        self.time = 0
        self.tilemap = TileMap(self)

        self.load_level('Stage01')

        pygame.mixer.music.load('data/sounds/bgm2014.ogg')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        while True:
            self.time += 1
            self.check_event()

            self.screen.fill((200, 255, 255))
            self.spike_manage.update()
            self.block_manage.update()
            self.player.update()

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == '__main__':
    Game(SIZE, FPS).run()
