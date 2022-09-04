# class pipe object
# class bird object
import pygame
import neat
import os
import time
import random

pygame.font.init()
GEN = 0
WIN_WIDTH = 500
WIN_HEIGHT = 800
images_path = "images/imgs"
BIRD_IMAGES = []
IMAGES = os.listdir(images_path)

STAT_FONT = pygame.font.SysFont("comicsans", 50)

for image in IMAGES:
    if image.startswith("bird"):
        BIRD_IMAGES.append(pygame.transform.scale2x(pygame.image.load(os.path.join(images_path, image))))
    elif image.startswith("base"):
        BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join(images_path, image)))
    elif image.startswith("bg"):
        BG_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join(images_path, image)))
    elif image.startswith("pipe"):
        PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join(images_path, image)))


class Bird:
    IMGS = BIRD_IMAGES
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        if displacement >= 16:
            displacement = 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, window):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)

        window.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    vel = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGE

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.vel

    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bot_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point = bird_mask.overlap(top_mask, top_offset)

        if top_point or bot_point:
            return True

        return False


class Base:
    vel = 5
    WIDTH = BASE_IMAGE.get_width()
    IMG = BASE_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


def draw_window(window, birds, pipes, base, score, gen):
    window.blit(BG_IMAGE, (0, 0))

    for pipe in pipes:
        pipe.draw(window)

    text = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    gen_text = STAT_FONT.render("Gen: " + str(gen), 1, (0, 0, 0))
    window.blit(gen_text, (10, 10))

    base.draw(window)
    for bird in birds:
        bird.draw(window)

    pygame.display.update()


def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    pipes = [Pipe(700)]
    base = Base(730)
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)
        for even in pygame.event.get():
            if even.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind += 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        removed = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                removed.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in removed:
            pipes.remove(r)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(window, birds, pipes, base, score, GEN)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 20)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
