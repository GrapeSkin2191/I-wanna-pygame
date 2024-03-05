import json

import pygame


class TileMap:
    def __init__(self, game):
        self.game = game
        self.player_pos = ()
        self.tilemap = {}
        self.tile_size = 0
        self.offgrid_tiles = []

    def extract(self, tile_id: str, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if tile['type'] == tile_id:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        delete = []
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if tile['type'] == tile_id:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    delete.append(loc)
        for loc in delete:
            self.tilemap.pop(loc)

        return matches

    def load(self, path: str):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.player_pos = map_data['player']
        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
