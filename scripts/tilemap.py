import json

import pygame


NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]


class TileMap:
    def __init__(self, game):
        self.game = game
        self.map_type = ''
        self.background = (0, 0, 0)
        self.solid_tile = {}
        self.tile = {}
        self.tile_size = 0
        self.offgrid_tiles = []
        self.player_pos = ()
        self.room_to = ''

    def tiles_around(self, pos, solid=True):
        tile_dict = self.solid_tile if solid else self.tile
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in tile_dict:
                tiles.append(tile_dict[check_loc])
        return tiles

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos, True):
            rects.append(
                pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size,
                            self.tile_size))
        return rects

    def extract(self, tile_id: str, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if tile['type'] == tile_id:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        delete = []
        for loc in self.solid_tile:
            tile = self.solid_tile[loc]
            if tile['type'] == tile_id:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    delete.append(loc)
        for loc in delete:
            self.solid_tile.pop(loc)

        delete = []
        for loc in self.tile:
            tile = self.tile[loc]
            if tile['type'] == tile_id:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    delete.append(loc)
        for loc in delete:
            self.tile.pop(loc)

        return matches

    def load(self, path: str):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.map_type = map_data['map_type']
        self.background = map_data['background']
        self.tile_size = map_data['tile_size']
        self.solid_tile = map_data['solid_tile']
        self.tile = map_data['tile']
        self.offgrid_tiles = map_data['offgrid']
        if self.map_type == 'title':
            self.room_to = map_data['room_to']
        elif self.map_type == 'select':
            pass
        else:
            self.player_pos = map_data['player']

    def save(self, path: str):
        f = open(path, 'w')
        json.dump({
            'map_type': self.map_type,
            'background': self.background,
            'player': self.player_pos,
            'tile_size': self.tile_size,
            'solid_tile': self.solid_tile,
            'tile': self.tile,
            'offgrid': self.offgrid_tiles
        }, f)
        f.close()
