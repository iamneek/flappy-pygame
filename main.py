import pygame
import random
from pygame import mixer

clock = pygame.time.Clock()
fps = 60
white = (255, 255, 255)
color2 = (0, 48, 73)
score = 0
pass_pipe = False
pygame.init()
font = pygame.font.SysFont('Bauhaus 93', 60)
font2 = pygame.font.SysFont('arialrounded', 16)
font2.set_italic(True)
font2.set_bold(True)
ground_scroll = 0
scroll_speed = 4
screen = pygame.display.set_mode((500, 800))
pygame.display.set_caption("Flappy Bird")
icon = pygame.image.load('Assets/yellowbird-midflap.png')
BG = pygame.image.load('Assets/background-day.png')
BASE = pygame.image.load('Assets/base.png')
pygame.display.set_icon(icon)
highscore = 0
pipe_gap = 150
flying = False
game_over = False
pipe_timing = 1500
last_pipe = pygame.time.get_ticks() - pipe_timing

restart_btn = pygame.image.load('Assets/restart.png')


def draw_score(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_high_score(text, font, color, x, y):
    img = font.render(f"Highscore: {text}", True, color)
    screen.blit(img, (x, y))


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Assets/pipe.png')
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        if not game_over:
            self.rect.x -= scroll_speed
            if self.rect.right < 0:
                self.kill()


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.imgnames = ["midflap", "downflap", "upflap"]
        self.images = []
        self.index = 0
        self.counter = 0
        for i in self.imgnames:
            img = pygame.image.load(f'Assets/yellowbird-{i}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            self.vel += 0.5
            if self.vel > 14:
                self.vel = 14
            if self.rect.bottom < 630:
                self.rect.y += int(self.vel)
        if not game_over:
            if pygame.key.get_pressed()[pygame.K_SPACE] == 1 and not self.clicked:
                self.clicked = True
                jump_sound = mixer.Sound("Assets/jump.wav")
                jump_sound.play()
                self.vel = -8
            if pygame.key.get_pressed()[pygame.K_SPACE] == 0:
                self.clicked = False
            self.counter += 1
            if not game_over:
                flap_cooldown = 10
                if self.counter >= flap_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images):
                        self.index = 0
                self.image = self.images[self.index]

            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)

    def reset(self):
        self.rect.x = 100
        self.rect.y = int(800 / 2)
        self.vel = 0
        self.index = 0
        self.image = self.images[self.index]


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


def reset():
    global flying, game_over, game_over_sound_played
    pipe_group.empty()
    flappy.reset()
    scores = 0
    flying = False
    game_over = False
    game_over_sound_played = False
    return scores


bird_group = pygame.sprite.Group()
flappy = Bird(100, int(800 / 2))
bird_group.add(flappy)

pipe_group = pygame.sprite.Group()

running = True

restart_btn_inst = Button(500 // 2 - 50, 800 // 2 - 100, restart_btn)

game_over_sound_played = False
try:
    with open("highscore.txt", "r") as file:
        highscore = file.read()
except FileNotFoundError:
    highscore = highscore

while running:

    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not flying and not game_over:
            flying = True

    screen.fill("white")
    screen.blit(BG, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
    pipe_group.update()
    screen.blit(BASE, (ground_scroll, 0))

    if game_over:
        if not game_over_sound_played:
            over_sound = mixer.Sound("Assets/hit.wav")
            over_sound.play()
            game_over_sound_played = True
        if restart_btn_inst.draw():
            score = reset()

    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and not pass_pipe:
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score_sound = mixer.Sound("Assets/coin.wav")
                score_sound.set_volume(0.1)
                score_sound.play()
                score += 1
                pass_pipe = False

    if score > int(highscore):
        with open("highscore.txt", "w") as file:
            highscore = file.write(str(score))
        with open("highscore.txt", "r") as file:
            highscore = file.read()

    draw_high_score(highscore, font2, color2, 360, 20)
    draw_score(str(score), font, white, int(245), 20)
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    if flappy.rect.bottom >= 625:
        game_over = True
        screen.blit(BASE, (0, 0))

    if not game_over and flying:
        pipe_height = random.randint(-100, 100)
        pipe_timing = random.randint(900, 1500)
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_timing:
            pipe_btm = Pipe(500, int(800 / 2) + pipe_height, -1)
            pipe_group.add(pipe_btm)
            pipe_top = Pipe(500, int(800 / 2) + pipe_height, 1)
            pipe_group.add(pipe_top)
            last_pipe = time_now

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 38:
            ground_scroll = 0

    pygame.display.update()

pygame.quit()
