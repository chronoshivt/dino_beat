import tkinter as tk
import pygame
import librosa
import numpy as np
import lib.beat as beat  # Assuming this is a custom beat detection module

class Arrow:
    def __init__(self, canvas, direction, start_time, speed=2, target_y=400):
        self.canvas = canvas
        self.direction = direction
        self.start_time = start_time
        self.speed = speed
        self.target_y = target_y  # Y-coordinate of the target area
        self.start_y = -50  # Start above the canvas
        self.id = self.create_arrow()
        self.text_id = self.create_text()  # Create a text object for the time
        self.is_deleted = False

    def create_arrow(self):
        x_offset = {'Left': 50, 'Up': 250, 'Down': 350, 'Right': 150}.get(self.direction, 50)
        return self.canvas.create_polygon(x_offset, self.start_y, x_offset+50, self.start_y+50, x_offset, self.start_y+100, x_offset-50, self.start_y+50, fill={'Left': 'blue', 'Up': 'red', 'Down': 'yellow', 'Right': 'green'}.get(self.direction, 'grey'))

    def create_text(self):
        x_offset = {'Left': 50, 'Up': 250, 'Down': 350, 'Right': 150}.get(self.direction, 50)
        return self.canvas.create_text(x_offset, self.start_y - 10, text=f"{self.start_time:.2f}s", fill="white")

    def move(self):
        if not self.is_deleted:
            self.canvas.move(self.id, 0, self.speed)
            self.canvas.move(self.text_id, 0, self.speed)
            coords = self.canvas.coords(self.id)
            if not coords or coords[3] > self.canvas.winfo_height():
                self.delete_arrow()

    def hit_effect(self):
        # Enlarge and brighten the arrow for a split second
        self.canvas.itemconfig(self.id, fill='white')  # Make the arrow really bright
        self.canvas.scale(self.id, 0, 0, 2.5, 2.5)  # Enlarge the arrow slightly
        # Schedule the deletion of the arrow after the effect
        window.after(100, lambda: self.delete_arrow())  # Adjust the duration of the effect here

    def delete_arrow(self):
        if not self.is_deleted:
            self.canvas.delete(self.id)
            self.canvas.delete(self.text_id)
            self.is_deleted = True

def schedule_arrows(beats_info, canvas, duration, target_y=400, speed=2):
    arrows = []
    distance_to_target = target_y + 50  # Distance from arrow start to target area
    travel_time = distance_to_target / speed  # Time for arrow to reach target area

    def spawn_arrows():
        for band, beats in beats_info.items():
            for beat_time in beats:
                direction = get_direction_for_band(band)
                adjusted_start_time = beat_time - travel_time / 1000.0
                if adjusted_start_time > 0:
                    arrow = Arrow(canvas, direction, adjusted_start_time, speed, target_y)
                    arrows.append(arrow)
                    window.after(int(adjusted_start_time * 1000), lambda arrow=arrow: animate_arrow(arrow, duration))

    # Wait 4 seconds before starting to spawn arrows
    window.after(4000, spawn_arrows)

def play_song(path):
    pygame.mixer.init()
    def start_music():
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
    # Wait 4 seconds before starting music to sync with arrow spawn
    window.after(4000, start_music)

def audioToInt(audio):
    """Converts an audio signal into the int16 format."""
    return (audio * (32767 / np.max(np.abs(audio)))).astype(np.int16)

def load_song_and_beats(path):
    y, sr = librosa.load(path)
    beats_info = {
        'combi': beat.detect_combi_beats(y, sr),
        'sub': beat.detect_beats(y, sr, freq_range='sub'),
        'low': beat.detect_beats(y, sr, freq_range='low'),
        'mid': beat.detect_beats(y, sr, freq_range='mid'),
        'high_mid': beat.detect_beats(y, sr, freq_range='high_mid'),
        'high': beat.detect_beats(y, sr, freq_range='high')
    }
    return beats_info, librosa.get_duration(y=y, sr=sr)

def on_key_press(event):
    key = event.keysym
    log_message = f"Arrow key pressed: {key}"
    log_label.config(text=log_message)

def animate_arrow(arrow, duration):
    def move_arrow():
        if pygame.mixer.music.get_busy() and not arrow.is_deleted:  # Check if music is playing and arrow not deleted
            arrow.move()
            coords = arrow.canvas.coords(arrow.id)
            # Check if the arrow is within the target area
            if coords and arrow.target_y <= coords[3] <= arrow.target_y + arrow.speed:
                arrow.hit_effect()
            else:
                window.after(50, move_arrow)
    move_arrow()

def get_direction_for_band(band):
    mapping = {
        'combi': 'Down',
        'sub': 'Left',
        'low': 'Up',
        'mid': 'Right',
        'high_mid': 'Left',
        'high': 'Down'
    }
    return mapping.get(band, 'Up')

def draw_target_shapes(canvas):
    canvas.create_polygon(50, 350, 100, 400, 50, 450, 0, 400, fill='light blue')  # Target for Left arrow
    canvas.create_polygon(150, 350, 200, 400, 150, 450, 100, 400, fill='light green')  # Target for Right arrow
    canvas.create_polygon(250, 350, 300, 400, 250, 450, 200, 400, fill='light coral')  # Target for Up arrow
    canvas.create_polygon(350, 350, 400, 400, 350, 450, 300, 400, fill='light yellow')  # Target for Down arrow

window = tk.Tk()
window.title("Rhythm Beat Game")

greeting = tk.Label(text="Press the arrow keys in rhythm with the beat!")
greeting.pack()

log_label = tk.Label(text="Waiting for key press...", fg="blue")
log_label.pack(side=tk.BOTTOM, fill=tk.X)

canvas = tk.Canvas(window, width=500, height=400)
canvas.pack()

draw_target_shapes(canvas)  # Draw static target shapes at the bottom

window.bind("<Left>", on_key_press)
window.bind("<Right>", on_key_press)
window.bind("<Up>", on_key_press)
window.bind("<Down>", on_key_press)

path = './test.mp3'  # Ensure this is the correct path to your audio file
beats_info, duration = load_song_and_beats(path)

play_song(path)  # Start playing the song

schedule_arrows(beats_info, canvas, duration)  # Schedule arrows based on detected beats

window.mainloop()
