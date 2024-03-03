import sys

import pygame

from sprites import *


class GameManage:
    def __init__(self, size: tuple[int, int], fps: int):
        pygame.init()
        pygame.display.set_caption('I wanna pygame')
        pygame.display.set_icon(pygame.image.load('data/images/fruit32.ico'))

        pygame.mixer.music.load('data/sounds/bgm2014.ogg')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.size = size
        self.fps = fps
        self.screen = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.full_screen = False

        self.spike_manage = SpikeManage(self)
        self.player = PlayerSprite((self.screen.get_width() // 2, self.screen.get_height() // 2),
                                   self, self.spike_manage)

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
                    GameManage(self.size, self.fps).run()
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
        while True:
            self.check_event()

            self.screen.fill((200, 255, 255))
            self.spike_manage.update()
            self.player.update()

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == '__main__':
    GameManage((800, 608), 60).run()
