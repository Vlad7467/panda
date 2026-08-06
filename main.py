#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panda Chaos — экшн-игра с видом от третьего лица.
Управляй пандой, уничтожай врагов, активируй шестиствольный пулемёт (чит-код "vlad").
Все спрайты генерируются через Agnes AI при первом запуске.
Работает на Android (сенсорное управление) и Windows.
"""

import pygame
import sys
import os
import json
import random
import math
import time
import requests
from io import BytesIO
from PIL import Image
import numpy as np

# ---------- КЛЮЧ AGNES ----------
AGNES_API_KEY = "sk-yYjSBLyi3pBaFhNRvu0YIfcl9EQjv7iI3x2FBXy8nOQOnE5p"
AGNES_URL = "https://apihub.agnes-ai.com/v1/images/generations"

# ---------- ИНИЦИАЛИЗАЦИЯ PYGAME ----------
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Настройки экрана (адаптируем под Android)
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
if WIDTH > 1000:  # для ПК
    WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Panda Chaos")
clock = pygame.time.Clock()
FPS = 60

# ---------- ЦВЕТА ----------
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
CYAN = (0,255,255)
ORANGE = (255,165,0)

# ---------- ФУНКЦИИ РАБОТЫ С AGNES (ГЕНЕРАЦИЯ СПРАЙТОВ) ----------
def generate_sprite(prompt, filename, size=(64,64)):
    headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "agnes-image-2.1-flash",
        "prompt": prompt,
        "n": 1,
        "size": f"{size[0]}x{size[1]}",
        "extra_body": {"response_format": "url"}
    }
    try:
        resp = requests.post(AGNES_URL, json=payload, headers=headers, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            img_url = data["data"][0]["url"]
            img_resp = requests.get(img_url, timeout=30)
            if img_resp.status_code == 200:
                img = Image.open(BytesIO(img_resp.content))
                img = img.resize(size, Image.Resampling.LANCZOS)
                img.save(filename)
                return pygame.image.load(filename).convert_alpha()
    except Exception as e:
        print(f"❌ Ошибка генерации {filename}: {e}")
    return None

def generate_sprites():
    os.makedirs("assets", exist_ok=True)
    sprites = {}
    prompts = {
        "panda.png": "A cute pixel art panda character, 64x64, game sprite, transparent background, standing pose",
        "chaingun.png": "A six-barrel rotary machine gun, pixel art, 64x64, game sprite, transparent background, detailed, military style",
        "enemy.png": "A scary pixel art monster, 64x64, game sprite, transparent background, red eyes, dark",
        "bullet.png": "A glowing yellow projectile, pixel art, 16x16, game sprite, transparent background",
        "bg_arena.png": "A dark futuristic arena background, pixel art, 800x600, game background, sci-fi",
        "ui_heart.png": "A pixel art heart, 24x24, game sprite, transparent background, red",
        "ui_ammo.png": "A pixel art ammo icon, 24x24, game sprite, transparent background, yellow"
    }
    for name, prompt in prompts.items():
        path = os.path.join("assets", name)
        if not os.path.exists(path):
            print(f"🔄 Генерация {name}...")
            surf = generate_sprite(prompt, path)
            if surf:
                sprites[name] = surf
            else:
                surf = fallback_sprite(name)
                if surf:
                    pygame.image.save(surf, path)
                    sprites[name] = surf
        else:
            sprites[name] = pygame.image.load(path).convert_alpha()
    return sprites

def fallback_sprite(name):
    if "panda" in name:
        s = pygame.Surface((64,64), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (50,50,50), (10,10,44,44))
        pygame.draw.circle(s, (255,255,255), (24,24), 8)
        pygame.draw.circle(s, (255,255,255), (40,24), 8)
        return s
    elif "chaingun" in name:
        s = pygame.Surface((64,64), pygame.SRCALPHA)
        pygame.draw.rect(s, (100,100,100), (10,20,44,24))
        for i in range(6):
            x = 14 + i*7
            pygame.draw.circle(s, (80,80,80), (x, 26), 4)
        return s
    elif "enemy" in name:
        s = pygame.Surface((64,64), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (100,0,0), (8,8,48,48))
        pygame.draw.circle(s, (255,0,0), (20,24), 6)
        pygame.draw.circle(s, (255,0,0), (44,24), 6)
        return s
    elif "bullet" in name:
        s = pygame.Surface((16,16), pygame.SRCALPHA)
        pygame.draw.circle(s, (255,255,0), (8,8), 6)
        return s
    elif "bg_arena" in name:
        s = pygame.Surface((800,600))
        s.fill((20,20,40))
        return s
    elif "ui_heart" in name:
        s = pygame.Surface((24,24), pygame.SRCALPHA)
        pygame.draw.polygon(s, (255,0,0), [(12,4), (4,12), (12,20), (20,12)])
        return s
    elif "ui_ammo" in name:
        s = pygame.Surface((24,24), pygame.SRCALPHA)
        pygame.draw.circle(s, (255,255,0), (12,12), 8)
        return s
    return None

# ---------- ЗВУКИ (синтез) ----------
def generate_tone(freq, duration=0.1, volume=0.3):
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = np.sin(2 * np.pi * freq * t) * volume
    wave = (wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(wave)

sounds = {
    "shoot": generate_tone(800, 0.05, 0.2),
    "explode": generate_tone(200, 0.3, 0.4),
    "hit": generate_tone(500, 0.1, 0.3),
    "chaingun": generate_tone(300, 0.03, 0.15),
}

# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------
def distance(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def angle_between(p1, p2):
    return math.atan2(p2[1]-p1[1], p2[0]-p1[0])

# ---------- ГЛАВНЫЙ КЛАСС ИГРЫ ----------
class Game:
    def __init__(self):
        self.sprites = generate_sprites()
        self.screen = screen
        self.clock = clock
        self.font = pygame.font.Font(None, 30)
        self.big_font = pygame.font.Font(None, 60)
        self.state = "menu"
        self.player = None
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.chaingun_active = False
        self.chaingun_cooldown = 0
        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.wave_delay = 0
        self.max_enemies = 5
        self.lives = 3
        self.cheat_code = ""
        self.cheat_activated = False
        self.touch_joystick = None
        self.touch_shoot = False
        self.mouse_pos = (WIDTH//2, HEIGHT//2)
        self.init_menu()

    def init_menu(self):
        pass

    def start_game(self):
        self.player = Player(WIDTH//2, HEIGHT//2, self.sprites["panda.png"])
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.chaingun_active = False
        self.chaingun_cooldown = 0
        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.wave_delay = 0
        self.max_enemies = 5
        self.lives = 3
        self.cheat_activated = False
        self.state = "playing"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_SPACE:
                        self.start_game()
                elif self.state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                    # Чит-код "vlad"
                    if event.key == pygame.K_v:
                        self.cheat_code += "v"
                    elif event.key == pygame.K_l:
                        self.cheat_code += "l"
                    elif event.key == pygame.K_a:
                        self.cheat_code += "a"
                    elif event.key == pygame.K_d:
                        self.cheat_code += "d"
                    else:
                        self.cheat_code = ""
                    if "vlad" in self.cheat_code:
                        self.cheat_activated = True
                        self.chaingun_active = True
                        self.cheat_code = ""
                        print("🔫 Шестиствольный пулемёт активирован!")
                elif self.state == "gameover" or self.state == "win":
                    if event.key == pygame.K_SPACE:
                        self.start_game()
            # Сенсорное управление (Android)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "playing":
                    # Определяем область касания для стрельбы (правая половина экрана)
                    if event.pos[0] > WIDTH//2:
                        self.touch_shoot = True
                    else:
                        # Левая половина — джойстик
                        self.touch_joystick = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                self.touch_shoot = False
                self.touch_joystick = None
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

        # Непрерывное управление с клавиатуры
        if self.state == "playing" and self.player:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = 1
            if dx != 0 or dy != 0:
                self.player.move(dx, dy)
            else:
                self.player.move(0, 0)
            # Стрельба по пробелу или левой кнопке мыши
            if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
                self.player.shoot()
            # Активация пулемёта по клавише "c"
            if keys[pygame.K_c] and self.cheat_activated:
                self.chaingun_active = not self.chaingun_active

    def update(self):
        if self.state != "playing":
            return
        # Обновление игрока
        self.player.update()
        # Сенсорное управление движением
        if self.touch_joystick:
            dx = self.touch_joystick[0] - self.player.rect.centerx
            dy = self.touch_joystick[1] - self.player.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 10:
                self.player.move(dx/dist, dy/dist)
        # Стрельба (сенсор)
        if self.touch_shoot:
            self.player.shoot()
        # Пулемёт
        if self.chaingun_active and self.chaingun_cooldown <= 0:
            if self.enemies:
                # стреляем по ближайшему врагу
                target = min(self.enemies, key=lambda e: distance(self.player.rect.center, e.rect.center))
                angle = angle_between(self.player.rect.center, target.rect.center)
                self.bullets.append(Bullet(self.player.rect.centerx, self.player.rect.centery, angle, speed=8, damage=2))
                sounds["chaingun"].play()
                self.chaingun_cooldown = 5
        else:
            self.chaingun_cooldown -= 1
        # Пули
        for b in self.bullets[:]:
            b.update()
            if b.rect.x < -20 or b.rect.x > WIDTH+20 or b.rect.y < -20 or b.rect.y > HEIGHT+20:
                self.bullets.remove(b)
                continue
            # столкновение с врагами
            for e in self.enemies[:]:
                if b.rect.colliderect(e.rect):
                    e.hp -= b.damage
                    self.bullets.remove(b)
                    sounds["hit"].play()
                    if e.hp <= 0:
                        self.enemies.remove(e)
                        self.score += 10
                        self.particles.append(Particle(e.rect.centerx, e.rect.centery, RED, 20))
                        sounds["explode"].play()
                    break
        # Враги
        for e in self.enemies[:]:
            e.update(self.player)
            if e.rect.colliderect(self.player.rect):
                self.lives -= 1
                self.enemies.remove(e)
                sounds["hit"].play()
                if self.lives <= 0:
                    self.state = "gameover"
                    return
        # Спавн врагов (волны)
        self.wave_delay += 1
        if self.wave_delay > 60 and len(self.enemies) < self.max_enemies:
            self.wave_delay = 0
            self.enemies_spawned += 1
            # спавним с краю
            side = random.choice(['top','bottom','left','right'])
            if side == 'top': x, y = random.randint(0,WIDTH), -30
            elif side == 'bottom': x, y = random.randint(0,WIDTH), HEIGHT+30
            elif side == 'left': x, y = -30, random.randint(0,HEIGHT)
            else: x, y = WIDTH+30, random.randint(0,HEIGHT)
            enemy = Enemy(x, y, self.sprites["enemy.png"])
            self.enemies.append(enemy)
        # Новая волна
        if self.enemies_spawned >= self.max_enemies and len(self.enemies) == 0:
            self.wave += 1
            self.max_enemies = min(20, 5 + self.wave * 2)
            self.enemies_spawned = 0
            self.wave_delay = 0
            if self.wave > 10:
                self.state = "win"
        # Частицы
        self.particles = [p for p in self.particles if p.update()]

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
            return
        if self.state == "gameover":
            self.draw_gameover()
            return
        if self.state == "win":
            self.draw_win()
            return

        # Фон
        screen.blit(self.sprites["bg_arena.png"], (0,0))
        # Игрок
        self.player.draw(screen, self.mouse_pos)
        # Пулемёт (если активен)
        if self.chaingun_active:
            gun_rect = self.sprites["chaingun.png"].get_rect()
            gun_rect.center = (self.player.rect.centerx + 30, self.player.rect.centery - 10)
            screen.blit(self.sprites["chaingun.png"], gun_rect)
        # Враги
        for e in self.enemies:
            e.draw(screen)
        # Пули
        for b in self.bullets:
            b.draw(screen)
        # Частицы
        for p in self.particles:
            p.draw(screen)
        # HUD
        lives_img = self.sprites["ui_heart.png"]
        for i in range(self.lives):
            screen.blit(lives_img, (10 + i*30, 10))
        score_text = self.font.render(f"Счёт: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 50))
        wave_text = self.font.render(f"Волна: {self.wave}", True, WHITE)
        screen.blit(wave_text, (10, 80))
        if self.chaingun_active:
            cg_text = self.font.render("🔥 ПУЛЕМЁТ АКТИВЕН", True, RED)
            screen.blit(cg_text, (WIDTH//2 - 100, 10))
        # Индикатор читов
        if self.cheat_activated:
            cheat_text = self.font.render("Чит-код VLAD активирован (C - включить/выключить пулемёт)", True, YELLOW)
            screen.blit(cheat_text, (10, HEIGHT-30))
        # Сенсорные подсказки
        if pygame.mouse.get_pressed()[0] == 0:
            hint = self.font.render("Касание слева — движение, справа — стрельба", True, (150,150,150))
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-60))
        pygame.display.flip()

    def draw_menu(self):
        screen.fill((10,10,30))
        title = self.big_font.render("PANDA CHAOS", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        sub = self.font.render("Нажми ПРОБЕЛ, чтобы начать", True, WHITE)
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 300))
        controls = self.font.render("WASD — движение, Пробел — стрельба, C — пулемёт (чит-код: vlad)", True, GRAY)
        screen.blit(controls, (WIDTH//2 - controls.get_width()//2, 400))
        pygame.display.flip()

    def draw_gameover(self):
        screen.fill((0,0,0))
        go = self.big_font.render("GAME OVER", True, RED)
        screen.blit(go, (WIDTH//2 - go.get_width()//2, 150))
        score = self.font.render(f"Счёт: {self.score} | Волна: {self.wave}", True, WHITE)
        screen.blit(score, (WIDTH//2 - score.get_width()//2, 300))
        restart = self.font.render("Нажми ПРОБЕЛ, чтобы начать заново", True, GRAY)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 400))
        pygame.display.flip()

    def draw_win(self):
        screen.fill((0,20,0))
        win = self.big_font.render("ВЫ ПОБЕДИЛИ!", True, GREEN)
        screen.blit(win, (WIDTH//2 - win.get_width()//2, 150))
        score = self.font.render(f"Счёт: {self.score}", True, WHITE)
        screen.blit(score, (WIDTH//2 - score.get_width()//2, 300))
        restart = self.font.render("Нажми ПРОБЕЛ, чтобы сыграть снова", True, GRAY)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 400))
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

# ---------- ИГРОВЫЕ ОБЪЕКТЫ ----------
class Player:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 4
        self.angle = 0
        self.shoot_cooldown = 0

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        if self.rect.x < 0: self.rect.x = 0
        if self.rect.y < 0: self.rect.y = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT

    def shoot(self):
        if self.shoot_cooldown <= 0:
            angle = angle_between(self.rect.center, pygame.mouse.get_pos())  # для ПК, для тач используем направление
            # если тач, то стреляем в направлении последнего касания
            # упростим: стреляем в сторону курсора мыши
            b = Bullet(self.rect.centerx, self.rect.centery, angle)
            game.bullets.append(b)
            sounds["shoot"].play()
            self.shoot_cooldown = 10
        else:
            self.shoot_cooldown -= 1

    def update(self):
        pass

    def draw(self, surf, mouse_pos):
        # Поворот спрайта в сторону мыши (или джойстика)
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        self.angle = math.degrees(math.atan2(dy, dx))
        rot_image = pygame.transform.rotate(self.image, -self.angle)
        rot_rect = rot_image.get_rect(center=self.rect.center)
        surf.blit(rot_image, rot_rect)

class Enemy:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1 + random.random()
        self.hp = 2

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.rect.x += self.speed * dx / dist
            self.rect.y += self.speed * dy / dist

    def draw(self, surf):
        surf.blit(self.image, self.rect)

class Bullet:
    def __init__(self, x, y, angle, speed=7, damage=1):
        self.image = game.sprites["bullet.png"] if hasattr(game, 'sprites') else None
        self.rect = self.image.get_rect() if self.image else pygame.Rect(x, y, 10, 10)
        self.rect.center = (x, y)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.damage = damage

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, self.rect)
        else:
            pygame.draw.circle(surf, YELLOW, self.rect.center, 6)

class Particle:
    def __init__(self, x, y, color, count=10):
        self.parts = []
        for _ in range(count):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(1, 4)
            self.parts.append([x, y, speed*math.cos(angle), speed*math.sin(angle), random.randint(10,30)])

    def update(self):
        for p in self.parts:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1
        self.parts = [p for p in self.parts if p[4] > 0]
        return len(self.parts) > 0

    def draw(self, surf):
        for p in self.parts:
            size = max(1, p[4]//5)
            pygame.draw.circle(surf, (255,200,100), (int(p[0]), int(p[1])), size)

# ---------- ГЛОБАЛЬНЫЙ ОБЪЕКТ ИГРЫ ----------
game = None

if __name__ == "__main__":
    game = Game()
    game.run()
