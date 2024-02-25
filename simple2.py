import pygame
import sys
import librosa
import numpy as np
import lib.beat as beat
import random
pygame.init()
pygame.mixer.init()

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

black = (0, 0, 0)
white = (255, 255, 255)

font = pygame.font.Font(None, 36)

def load_and_detect_beats(song_path):
    y, sr = librosa.load(song_path)
    beat_times_combi = beat.detect_combi_beats(y, sr)
    sub_times = beat.detect_beats(y, sr, freq_range='sub')
    low_times = beat.detect_beats(y, sr, freq_range='low')
    mid_times = beat.detect_beats(y, sr, freq_range='mid')
    high_mid_times = beat.detect_beats(y, sr, freq_range='high_mid')
    high_times = beat.detect_beats(y, sr, freq_range='high')

    all_beat_times = np.unique(np.concatenate(
        [beat_times_combi, sub_times, low_times, mid_times, high_mid_times, high_times]))
    all_beat_times.sort()
    return all_beat_times

def filter_beats(beat_times, min_interval=0.5):
    filtered_beats = [beat_times[0]]
    for time in beat_times[1:]:
        if time - filtered_beats[-1] >= min_interval:
            filtered_beats.append(time)
    return np.array(filtered_beats)

song_path = './flim.mp3'
beat_times = load_and_detect_beats(song_path)
filtered_beat_times = filter_beats(beat_times)

pygame.mixer.music.load(song_path)
pygame.mixer.music.play(0)

def resize_sprite(image, scale_factor):
    size = round(image.get_width() * scale_factor), round(image.get_height() * scale_factor)
    return pygame.transform.scale(image, size)

original_sprite1 = pygame.image.load('left.png')
original_sprite2 = pygame.image.load('right.png')
original_sprite3 = pygame.image.load('up.png')
original_sprite4 = pygame.image.load('down.png')

scale_factor = 0.75
sprite1 = resize_sprite(original_sprite1, scale_factor)
sprite2 = resize_sprite(original_sprite2, scale_factor)
sprite3 = resize_sprite(original_sprite3, scale_factor)
sprite4 = resize_sprite(original_sprite4, scale_factor)

# Mapping keys to sprites
key_to_sprite = {pygame.K_LEFT: sprite1, pygame.K_RIGHT: sprite2, pygame.K_UP: sprite3, pygame.K_DOWN: sprite4}

class Arrow:
    def __init__(self, sprite, x, y, display_time, key):
        self.sprite = sprite
        self.x = x
        self.y = y
        self.display_time = display_time
        self.hit = False
        self.key = key  # The key that needs to be pressed to hit this arrow

arrows = []
x_positions = [200, 300, 400, 500]
y_variation = [0, 50, -50]

beat_time_x_positions = {}

for beat_time in filtered_beat_times:
    available_x_positions = x_positions.copy()
    chosen_y_variation = np.random.choice(y_variation)

    if beat_time in beat_time_x_positions:
        for used_x in beat_time_x_positions[beat_time]:
            if used_x in available_x_positions:
                available_x_positions.remove(used_x)

    if not available_x_positions:
        chosen_x = np.random.choice(x_positions)
    else:
        chosen_x = np.random.choice(available_x_positions)

    # Select a random key from the dictionary
    chosen_key = random.choice(list(key_to_sprite.keys()))
    chosen_sprite = key_to_sprite[chosen_key]
    arrow = Arrow(chosen_sprite, chosen_x, chosen_y_variation, beat_time, chosen_key)

    if beat_time not in beat_time_x_positions:
        beat_time_x_positions[beat_time] = [chosen_x]
    else:
        beat_time_x_positions[beat_time].append(chosen_x)

    arrows.append(arrow)


score = 0
last_key_pressed = ""

clock = pygame.time.Clock()
fps = 60
start_time = pygame.time.get_ticks()

running = True
while running:
    current_time = pygame.time.get_ticks() - start_time
    ms_per_beat = current_time / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            last_key_pressed = key_name.upper()
            for arrow in arrows:
                if not arrow.hit and abs(ms_per_beat - arrow.display_time) <= 0.5:
                    if event.key == arrow.key:
                        score += 1  # Correct key pressed
                        arrow.hit = True
                    else:
                        score -= 1  # Wrong key pressed
                    break

    screen.fill(black)

    for arrow in arrows:
        time_until_display = arrow.display_time - ms_per_beat
        if 0 <= time_until_display <= 1 and not arrow.hit:
            screen.blit(arrow.sprite, (arrow.x, (screen_height / 2) + arrow.y))

    score_text = font.render(f"Score: {score}", True, white)
    key_text = font.render(f"Last Key: {last_key_pressed}", True, white)
    screen.blit(score_text, (10, screen_height - 70))
    screen.blit(key_text, (10, screen_height - 35))

    pygame.display.flip()
    clock.tick(fps)
