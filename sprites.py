import pygame as pg
from settings import *


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename)
        self.spritesheet = pg.Surface.convert_alpha(self.spritesheet)

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height), pg.SRCALPHA)
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.flipping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = pg.transform.scale(self.standing_frames_l[0], (144, 144))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = pg.math.Vector2(1000, 500)
        self.vel = pg.math.Vector2(0, 0)
        self.acc = pg.math.Vector2(0, 0)

    def load_images(self):
        self.standing_frames_l = [self.game.spritesheet.get_image(0, 0, 48, 48),
                                  self.game.spritesheet.get_image(48, 0, 48, 48),
                                  self.game.spritesheet.get_image(96, 0, 48, 48),
                                  self.game.spritesheet.get_image(144, 0, 48, 48)]
        self.standing_frames_r = []
        for frame in self.standing_frames_l:
            frame.set_colorkey(BLACK)
            self.standing_frames_r.append(pg.transform.flip(frame, True, False))

        self.walk_frames_l = [self.game.spritesheet.get_image(0, 48, 48, 48),
                              self.game.spritesheet.get_image(48, 48, 48, 48),
                              self.game.spritesheet.get_image(96, 48, 48, 48),
                              self.game.spritesheet.get_image(144, 48, 48, 48)]
        self.walk_frames_r = []
        for frame in self.walk_frames_l:
            frame.set_colorkey(BLACK)
            self.walk_frames_r.append(pg.transform.flip(frame, True, False))

        self.jump_frames_l = [self.game.spritesheet.get_image(0, 96, 48, 48),
                              self.game.spritesheet.get_image(48, 96, 48, 48),
                              self.game.spritesheet.get_image(96, 96, 48, 48),
                              self.game.spritesheet.get_image(144, 96, 48, 48),
                              self.game.spritesheet.get_image(0, 144, 48, 48)]
        self.jump_frames_r = []
        for frame in self.jump_frames_l:
            frame.set_colorkey(BLACK)
            self.jump_frames_r.append(pg.transform.flip(frame, True, False))

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def jump(self):
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def update(self):
        self.animate()
        self.acc = pg.math.Vector2(0, PLAYER_GRAVITY)
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.flipping = False
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.flipping = True
            self.acc.x = PLAYER_ACC

        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc

        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = WIDTH
        if self.pos.x < 0:
            self.pos.x = 0

        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        if self.walking:
            if now - self.last_update > 120:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                    self.image = pg.transform.scale(self.image, (144, 144))
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                    self.image = pg.transform.scale(self.image, (144, 144))
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        if self.jumping:
            if self.vel.y < 0:
                self.current_frame = 0
            else:
                self.current_frame = 4
            bottom = self.rect.bottom
            if not self.flipping:
                self.image = self.jump_frames_l[self.current_frame]
                self.image = pg.transform.scale(self.image, (144, 144))
            else:
                self.image = self.jump_frames_r[self.current_frame]
                self.image = pg.transform.scale(self.image, (144, 144))
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom

        if not self.jumping and not self.walking:
            if now - self.last_update > 250:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames_l)
                bottom = self.rect.bottom
                if not self.flipping:
                    self.image = self.standing_frames_l[self.current_frame]
                    self.image = pg.transform.scale(self.image, (144, 144))
                else:
                    self.image = self.standing_frames_r[self.current_frame]
                    self.image = pg.transform.scale(self.image, (144, 144))
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom


class Ground(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = GROUND_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.spritesheet.get_image(0, 264, 96, 24)
        self.image = pg.transform.scale(self.image, (288, 72))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Urns(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = URN_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.spritesheet.get_image(96, 240, 48, 48)
        self.image = pg.transform.scale(self.image, (144, 144))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Lamps(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = URN_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.spritesheet.get_image(144, 240, 48, 48)
        self.image = pg.transform.scale(self.image, (144, 144))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Fire(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = FIRE_LAYER
        self.groups = game.all_sprites, game.lights
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.load_images()
        self.current_frame = 0
        self.last_update = 0
        self.image = self.fire_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def load_images(self):
        self.fire_frames = [self.game.spritesheet.get_image(0, 192, 48, 48),
                            self.game.spritesheet.get_image(48, 192, 48, 48),
                            self.game.spritesheet.get_image(96, 192, 48, 48),
                            self.game.spritesheet.get_image(144, 192, 48, 48)]
        for frame in self.fire_frames:
            frame.set_colorkey(BLACK)

    def update(self):
        self.animate()

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 120:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.fire_frames)
            self.image = self.fire_frames[self.current_frame]
            self.image = pg.transform.scale(self.image, (144, 144))
            
