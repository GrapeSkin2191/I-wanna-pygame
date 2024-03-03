import sys

import pygame

from scripts.sprites import PlayerSprite, SpikeManage
from scripts.utils import load_image, load_images, load_sound, Animation


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
        self.full_screen = False

        self.assets = {
            'maskPlayer': load_image('player/maskPlayer.png'),
            'player/idle': load_images('player/idle'),
            'player/fall': load_images('player/fall'),
            'player/jump': load_images('player/jump'),
            'player/run': load_images('player/run'),
            'bullet': load_images('bullet'),
            'game_over': load_image('sprGAMEOVER.png'),
            'spike': load_image('sprSpike.png'),
            'blood': load_images('blood')
        }

        self.sfx = {
            'jump': load_sound('sndJump.wav'),
            'djump': load_sound('sndDjump.wav'),
            'shoot': load_sound('sndShoot.wav')
        }

        self.spike_manage = SpikeManage(self)
        self.player = PlayerSprite((self.screen.get_width() // 2, self.screen.get_height() // 2), self)

    def load_level(self):
        pass

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
                elif event.key == pygame.K_F2:
                    Game(self.size, self.fps).run()
                    self.stop()
                elif event.key == pygame.K_F4:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_q:
                    self.player.kill()
                elif event.key == pygame.K_z:
                    self.player.shoot()
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.player.jump()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.player.vjump()

    def run(self):
        pygame.mixer.music.load('data/sounds/bgm2014.ogg')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        while True:
            self.check_event()

            self.screen.fill((200, 255, 255))
            self.spike_manage.update()
            self.player.update()

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == '__main__':
    Game(SIZE, FPS).run()
