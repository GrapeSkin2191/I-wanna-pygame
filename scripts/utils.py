import os

import pygame

BASE_IMG_PATH = 'data/images/'
BASE_SND_PATH = 'data/sounds/'


def load_image(path, alpha=True):
    img = pygame.image.load(BASE_IMG_PATH + path)
    return img.convert_alpha() if alpha else img.convert()


def load_images(path, alpha=True):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name, alpha))
    return images


def load_images_to_dict(path, alpha=True):
    images = {}
    for img_name in os.listdir(BASE_IMG_PATH + path):
        images[os.path.splitext(img_name)[0]] = load_image(path + '/' + img_name, alpha)
    return images


def load_sound(path, vol=0.5):
    sound = pygame.mixer.Sound(BASE_SND_PATH + path)
    sound.set_volume(vol)
    return sound
