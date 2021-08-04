import pygame
import pygame.gfxdraw
import sys
import random
import math

screen = pygame.display.set_mode((600, 600))
pygame.init()

fpsclock = pygame.time.Clock()

font = pygame.font.SysFont('simhei', 40)

def fill_text(surface, font, text, pos, color=(0, 0, 0), shadow=False, center=False):
    text1 = font.render(text, True, color)
    text_rect = text1.get_rect()
    if shadow:
        text2 = font.render(text, True, (255 - color[0], 255 - color[1], 255 - color[2]))
        for p in [(pos[0] - 1, pos[1] - 1),
                  (pos[0] + 1, pos[1] - 1),
                  (pos[0] - 1, pos[1] + 1),
                  (pos[0] + 1, pos[1] + 1)]:
            if center:
                text_rect.center = p
            else:
                text_rect.x = p[0]
                text_rect.y = p[1]
            surface.blit(text2, text_rect)
    if center:
        text_rect.center = pos
    else:
        text_rect.x = pos[0]
        text_rect.y = pos[1]
    surface.blit(text1, text_rect)

class Ball:
    def __init__(self, x, y, r=5):
        self.x = x
        self.y = y
        self.speedy = 0
        self.speedx = 0
        self.lastx = x
        self.lasty = y
        self.r = r
        self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)
    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.r)
    def correct(self):
        if -0.2 <= self.speedx <= 0.2:
            self.speedx = 0
        if -0.2 <= self.speedy <= 0.2:
            self.speedy = 0
    def update(self):
        self.lastx = self.x
        self.lasty = self.y
        self.y += self.speedy
        self.x += self.speedx
        self.rect = pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)
        self.speedx *= 0.98
        self.speedy *= 0.98
        self.correct()
        if not self.r <= self.x < 600 - self.r:
            if self.r >= self.x:
                self.x = self.r
            elif self.x > 600 - self.r:
                self.x = 599 - self.r
            self.speedx *= -0.9
        if not self.r <= self.y < 600 - self.r:
            if self.r >= self.y:
                self.y = self.r
            elif self.y > 600 - self.r:
                self.y = 599 - self.r
            self.speedy *= -0.9
        for ball in balls[balls.index(self):]:
            if ball is not self:
                if ball.rect.colliderect(self.rect):
                    speedx1 = self.speedx
                    speedy1 = self.speedy
                    speedx2 = ball.speedx
                    speedy2 = ball.speedy
                    self.speedx = speedx1 * -0.49 + speedx2 * 0.45
                    self.speedy = speedy1 * -0.49 + speedy2 * 0.45
                    ball.speedx = speedx2 * -0.49 + speedx1 * 0.45
                    ball.speedy = speedy2 * -0.49 + speedy1 * 0.45
        self.draw()
    def update_event(self, event):
        pass

class PlayerBall(Ball):
    def __init__(self, x, y):
        Ball.__init__(self, x, y)
        self.draging = False
    def draw(self):
        if self.draging:
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my - self.y, mx - self.x)
            cosa = math.cos(angle) * 1024
            sina = math.sin(angle) * 1024
            pygame.draw.aaline(screen, (150, 150, 150), (mx - cosa, my - sina), (mx, my))
            pygame.draw.circle(screen, (230, 180, 80), (mx, my), self.r)
            pygame.draw.circle(screen, (255, 210, 110), (mx - 2, my - 2), 2)
            pygame.draw.circle(screen, (255, 210, 110), (mx, my - 3), 1)
            pygame.draw.circle(screen, (255, 240, 130), (mx - 2, my - 2), 1)
        pygame.draw.circle(screen, (230, 230, 230), (self.x, self.y), self.r)
    def update_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.draging = True
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.draging:
                    self.speedx = (self.x - event.pos[0]) / 30
                    self.speedy = (self.y - event.pos[1]) / 30
                    self.draging = False
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)

class Object:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def draw(self):
        pass
    def update(self, ball):
        pass

class Wall(Object):
    def __init__(self, x, y, width, height):
        Object.__init__(self, x, y)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    def draw(self):
        pygame.draw.rect(screen, (255, 255, 240), self.rect)
    def update(self, ball):
        if self.rect.colliderect(ball.rect):
            if self.x - ball.r <= ball.x <= self.x + self.width + ball.r:
                if self.x - ball.r <= ball.lastx <= self.x + self.width + ball.r:
                    if ball.y > ball.lasty:
                        ball.y = self.y - ball.r
                    elif ball.y < ball.lasty:
                        ball.y = self.y + self.height + ball.r
                    ball.speedy *= -0.9
            if self.y - ball.r <= ball.y <= self.y + self.height + ball.r:
                if self.y - ball.r <= ball.lasty <= self.y + self.height + ball.r:
                    if ball.x > ball.lastx:
                        ball.x = self.x - ball.r
                    elif ball.x < ball.lastx:
                        ball.x = self.x + self.width + ball.r
                    ball.speedx *= -0.9

class MoveWall(Object):
    def __init__(self, x, y, width, height):
        Object.__init__(self, x, y)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.speedx = 0
        self.speedy = 0
    def draw(self):
        pygame.draw.rect(screen, (215, 215, 200), self.rect)
    def update(self, ball):
        self.x += self.speedx
        self.y += self.speedy
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speedx *= 0.8
        self.speedy *= 0.8
        if -0.1 <= self.speedx <= 0.1:
            self.speedx = 0
        if -0.1 <= self.speedy <= 0.1:
            self.speedy = 0
        if not 0 <= self.x < 600 - self.width:
            if 0 >= self.x:
                self.x = 0
            elif self.x > 600 - self.width:
                self.x = 599 - self.width
            self.speedx *= -0.8
        if not 0 <= self.y < 600 - self.height:
            if 0 >= self.y:
                self.y = 0
            elif self.y > 600 - self.height:
                self.y = 599 - self.height
            self.speedy *= -0.8
        if self.rect.colliderect(ball.rect):
            if self.x - ball.r <= ball.x <= self.x + self.width + ball.r:
                if self.x - ball.r <= ball.lastx <= self.x + self.width + ball.r:
                    if ball.y > ball.lasty:
                        ball.y = self.y - ball.r
                    elif ball.y < ball.lasty:
                        ball.y = self.y + self.height + ball.r
                    ball.speedy *= -0.9
            if self.y - ball.r <= ball.y <= self.y + self.height + ball.r:
                if self.y - ball.r <= ball.lasty <= self.y + self.height + ball.r:
                    if ball.x > ball.lastx:
                        ball.x = self.x - ball.r
                    elif ball.x < ball.lastx:
                        ball.x = self.x + self.width + ball.r
                    ball.speedx *= -0.9
            self.speedx -= ball.speedx / 2
            self.speedy -= ball.speedy / 2

class Slow(Object):
    def __init__(self, x, y, width, height):
        Object.__init__(self, x, y)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    def draw(self):
        pygame.draw.rect(screen, (120, 120, 120), self.rect)
        for i in range(self.x, self.x + self.width, 20):
            pygame.draw.line(screen, (200, 200, 200), (i, self.y), (i, self.y + self.height))
        for i in range(self.y, self.y + self.height, 20):
            pygame.draw.line(screen, (200, 200, 200), (self.x, i), (self.x + self.width, i))
    def update(self, ball):
        if (self.x - ball.r <= ball.x < self.x + self.width + ball.r and
            self.y - ball.r <= ball.y < self.y + self.height + ball.r):
            ball.speedx *= 0.9
            ball.speedy *= 0.9

class Fast(Object):
    def __init__(self, x, y, width, height):
        Object.__init__(self, x, y)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    def draw(self):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        for i in range(self.x, self.x + self.width, 20):
            pygame.draw.line(screen, (120, 120, 120), (i, self.y), (i, self.y + self.height))
        for i in range(self.y, self.y + self.height, 20):
            pygame.draw.line(screen, (120, 120, 120), (self.x, i), (self.x + self.width, i))
    def update(self, ball):
        if (self.x - ball.r <= ball.x < self.x + self.width + ball.r and
            self.y - ball.r <= ball.y < self.y + self.height + ball.r):
            ball.speedx *= 1.1
            ball.speedy *= 1.1

class Left(Object):
    def __init__(self, x, y, width, height):
        Object.__init__(self, x, y)
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.surface.fill((230, 230, 230))
        for i in range(-height // 2, width + height // 2, 40):
            pygame.draw.line(self.surface, (180, 180, 180), (i, 0), (i - height // 2, height // 2), 20)
            pygame.draw.line(self.surface, (180, 180, 180), (i - height // 2, height // 2), (i, height), 20)
    def draw(self):
        screen.blit(self.surface, (self.x, self.y))
    def update(self, ball):
        if (self.x - ball.r <= ball.x < self.x + self.width + ball.r and
            self.y - ball.r <= ball.y < self.y + self.height + ball.r):
            ball.x -= 5

class Right(Object):
    def __init__(self, x, y, width, height):
        Object.__init__(self, x, y)
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.surface.fill((230, 230, 230))
        for i in range(0, width + height, 40):
            pygame.draw.line(self.surface, (180, 180, 180), (i, 0), (i + height // 2, height // 2), 20)
            pygame.draw.line(self.surface, (180, 180, 180), (i + height // 2, height // 2), (i, height), 20)
    def draw(self):
        screen.blit(self.surface, (self.x, self.y))
    def update(self, ball):
        if (self.x - ball.r <= ball.x < self.x + self.width + ball.r and
            self.y - ball.r <= ball.y < self.y + self.height + ball.r):
            ball.x += 5

class Convex(Object):
    def __init__(self, x, y, r):
        Object.__init__(self, x, y)
        self.r = r
    def draw(self):
        for i in range(self.r):
            pygame.draw.circle(screen, (110 + 145 / self.r * i,) * 3, (self.x, self.y), self.r - i)
    def update(self, ball):
        distance = math.sqrt((self.x - ball.x) ** 2 + (self.y - ball.y) ** 2)
        if distance < self.r:
            angle = math.atan2(self.y - ball.y, self.x - ball.x)
            cosa = math.cos(angle) * self.r / 5 * (1 - distance / self.r)
            sina = math.sin(angle) * self.r / 5 * (1 - distance / self.r)
            ball.x -= cosa
            ball.y -= sina

class Concave(Object):
    def __init__(self, x, y, r):
        Object.__init__(self, x, y)
        self.r = r
    def draw(self):
        for i in range(self.r):
            pygame.draw.circle(screen, (110 / self.r * (self.r - i),) * 3, (self.x, self.y), self.r - i)
    def update(self, ball):
        distance = math.sqrt((self.x - ball.x) ** 2 + (self.y - ball.y) ** 2)
        if distance < self.r:
            if distance < self.r / 10:
                ball.x = self.x
                ball.y = self.y
            else:
                angle = math.atan2(self.y - ball.y, self.x - ball.x)
                cosa = math.cos(angle) * self.r / 5 * (1 - distance / self.r)
                sina = math.sin(angle) * self.r / 5 * (1 - distance / self.r)
                ball.x += cosa
                ball.y += sina

class Hole(Object):
    def __init__(self, x, y):
        Object.__init__(self, x, y)
        self.r = 20
    def draw(self):
        for i in range(self.r):
            pygame.draw.circle(screen, (100 / self.r * (self.r - i),) * 3, (self.x, self.y), self.r - i)
        pygame.draw.circle(screen, (150, 150, 150), (self.x, self.y), self.r, 1)
    def update(self, ball):
        global state
        distance = math.sqrt((self.x - ball.x) ** 2 + (self.y - ball.y) ** 2)
        if distance < self.r:
            if distance < self.r / 3:
                ball.x = self.x
                ball.y = self.y
                pygame.time.delay(500)
                balls.remove(ball)
                state = 'win'
            else:
                angle = math.atan2(self.y - ball.y, self.x - ball.x)
                cosa = math.cos(angle) * 5 * (1 - distance / self.r)
                sina = math.sin(angle) * 5 * (1 - distance / self.r)
                ball.x += cosa
                ball.y += sina

balls = [PlayerBall(300, 300)]
objects = [Convex(450, 450, 50),
           Concave(100, 100, 50),
           Wall(200, 200, 100, 10),
           MoveWall(100, 300, 100, 10),
           Slow(300, 100, 100, 100),
           Fast(300, 300, 100, 100),
           Left(250, 450, 100, 40),
           Right(250, 500, 100, 40),]
state = 'running'
shadow = pygame.Surface((600, 600)).convert_alpha()
alpha1 = 0
alpha2 = 0
while True:
    if state == 'running':
        screen.fill((100, 100, 100))
        for obj in objects:
            for ball in balls:
                obj.update(ball)
            obj.draw()
        for ball in balls:
            ball.update()
    elif state == 'win':
        pass
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        for ball in balls:
            ball.update_event(event)
    pygame.display.update()
    fpsclock.tick(60)
