import pygame
import copy
import random
import sys
import librosa
import tkinter as tk
from tkinter import filedialog

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Rhythm Game")

# color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

frame_counter = 0
note_period = random.randint(30, 50)
note_speed = 5
hit_zone = 500  # y position where player has to hit the note
zone_lineWidth = 2
zone_color = GREEN
score = 0
hit_comment = ''
combo = 1
combo_comment = ''
all_arrow_choices = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
notes = []
prev_key = None
prev_points = 0

# distances from hit_zone
ok_margin = 80
ok_score = 1
good_margin = 60
good_score = 3
great_margin = 40
great_score = 5

# Set up font
titleFont = pygame.font.SysFont('Elephant', 48)
subFont = pygame.font.SysFont('Elephant', 18)
cornerFont = pygame.font.SysFont('Elephant', 24)
font = pygame.font.SysFont('Arial', 48)

instructions = 'Click the start button to pick a song, or input an MP3 file to have your own unique rhythm game!'
instructionText = subFont.render(instructions, True, BLACK)

game_running = True
inGame = False
song_running = True  # remove this probably
inPick = False
inMenu = True
isEnd = False
songButtons = []

# map keys to corresponding symbol
KEY_DICT = {pygame.K_LEFT: "←", pygame.K_RIGHT: "→", pygame.K_UP: "↑", pygame.K_DOWN: "↓"}

# map each arrow to the corresponding lane
NOTE_X_DICT = {pygame.K_LEFT: 300, pygame.K_RIGHT: 600, pygame.K_UP: 400, pygame.K_DOWN: 500}

clock = pygame.time.Clock()
#PATHS
twinklePath = 'Twinkle Twinkle Little Star.mp3'
MoonlightPath = 'Beethoven - Moonlight Sonata, 1st Mvmt. (Intro).mp3'
RhapsodyPath = 'Queen - Bohemian Rhapsody (Part 1).mp3'
christmasPath = 'All I Want for Christmas Is You.mp3'
uploadPath = ''
songDict = {'twinkle': twinklePath, 'moonlight': MoonlightPath, 'bohemian': RhapsodyPath, 'christmas': christmasPath, 'upload': uploadPath}
beatList = []

# get beat map  using librosa
def getOnsetList(filePath):
    x, sr = librosa.load(filePath)
    onset_frames = librosa.onset.onset_detect(y=x, sr=sr, wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
    onset_times = librosa.frames_to_time(onset_frames)
    return list(onset_times)

# Function to open a file dialog and return the selected file path
def open_file_dialog():
    # Hide root window (Tkinter window)
    root = tk.Tk()
    root.withdraw()  #prevent root window from showing up
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("All Files", "*.*")])
    return file_path

class Note:
    def __init__(self, x, key):
        self.x = x
        self.y = -50  # start above screen
        self.key = key
        self.width = 100
        self.height = 75
        self.color = RED
        self.key_text = font.render(f'{KEY_DICT[self.key]}', True, WHITE)

    def move(self):
        self.y += note_speed

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        screen.blit(self.key_text, (self.x + self.width // 2 - self.key_text.get_width() // 2,
                                    self.y + self.height // 2 - self.key_text.get_height() // 2))

# Function to create new notes
def create_note(arrows):
    key = random.choice(arrows)
    x = NOTE_X_DICT[key]  # Corresponding lane for each arrow
    note = Note(x, key)
    notes.append(note)
    global prev_key
    prev_key = key

class Button:
    def __init__(self, x, y, width, height, font, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.font = pygame.font.Font(None, 36)
        self.textSurface = self.font.render(self.text, True, BLACK)
        self.textRect = self.textSurface.get_rect(center=self.rect.center)

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)
        screen.blit(self.textSurface, self.textRect)

    def is_clicked(self, mouse_pos, mouse_button):
        if self.rect.collidepoint(mouse_pos):
            if mouse_button == 1:
                if self.action:
                    self.action()

def startGame():
    global inGame, inPick, inMenu
    inMenu = False
    inPick = True

def quitGame():
    pygame.quit()
    sys.exit()

def pickSong(songName):
    global inPick, inGame, beatList, songDict, uploadPath

    if songName == 'upload':
        uploadPath = open_file_dialog()
        if uploadPath:
            if uploadPath[-4:] == '.mp3':
                songDict[songName] = uploadPath
            else:
                print('Please make sure the file is an mp3 file!')
                return

    inPick = False
    inGame = True

    beatList = getOnsetList(songDict[songName])
    pygame.mixer.music.load(songDict[songName])
    pygame.mixer.music.play(-1)

def backToMenu():
    global inPick, inMenu
    inPick = False
    inMenu = True

backButton = Button(700, 100, 50, 50, titleFont, "X", backToMenu)
startButton = Button(400, 350, 200, 50, titleFont, "Start", startGame)
songButtons = [
    Button(350, 120, 300, 50, subFont, 'twinkle', lambda: pickSong('twinkle')),
    Button(350, 180, 300, 50, subFont, 'moonlight', lambda: pickSong('moonlight')),
    Button(350, 240, 300, 50, subFont, 'bohemian', lambda: pickSong('bohemian')),
    Button(350, 300, 300, 50, subFont, 'christmas', lambda: pickSong('christmas')),
    Button(350, 360, 300, 50, subFont, 'Upload MP3 File', lambda: pickSong('upload'))
]

while game_running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if inMenu:
                startButton.is_clicked(event.pos, event.button)
            elif inPick:
                for button in songButtons:
                    button.is_clicked(event.pos, event.button)
        elif event.type == pygame.KEYDOWN:
            # Check if pressed key matches a note
            for note in notes:
                if event.key == note.key:
                    if hit_zone - ok_margin < note.y < hit_zone + ok_margin:
                        if hit_zone - great_margin < note.y < hit_zone + great_margin:  # within 40 of hit_zone
                            hit_comment = "Great!"
                            zone_lineWidth = 15
                            zone_color = GREEN
                            if prev_points >= 5:
                                combo += 1
                                combo_comment = f"Combo x{combo}!"
                                noteScore = prev_points * 2
                            else:
                                noteScore = great_score
                        elif hit_zone - good_margin < note.y < hit_zone + good_margin:  # within 60 of hit_zone
                            noteScore = good_score
                            hit_comment = "Good!"
                            zone_lineWidth = 10
                            zone_color = GREEN
                            combo = 1
                        elif hit_zone - ok_margin < note.y < hit_zone + ok_margin:  # within 100 of hit_zone
                            noteScore = ok_score
                            hit_comment = "OK"
                            zone_lineWidth = 7
                            zone_color = GREEN
                            combo = 1
                        notes.remove(note)  # Remove the note if it's hit
                        score += noteScore
                        prev_points = noteScore
                        break
                    else:
                        prev_points = 0
                        hit_comment = "Miss!"
                        zone_color = RED
                        combo = 1

    if inMenu:
        welcomeText = titleFont.render('Welcome To Rhythm Game', True, BLACK)
        welcomeTextRect = welcomeText.get_rect()
        welcomeTextRect.center = (500, 150)
        instructionTextRect = instructionText.get_rect()
        instructionTextRect.center = (500, 250)

        screen.blit(welcomeText, welcomeTextRect)
        screen.blit(instructionText, instructionTextRect)
        startButton.draw()
    elif inPick:
        screen.fill(WHITE)
        for button in songButtons:
            button.draw()
    elif inGame:
        if beatList != [] and pygame.mixer.music.get_pos() / 1000 >= beatList[0] - 1.7:
            beatList.pop(0)
            if prev_key == None:
                arrow_choices = all_arrow_choices
            else:
                arrow_choices = copy.copy(all_arrow_choices)
                arrow_choices.remove(prev_key)
            create_note(arrow_choices)

        # Continuously move each note
        for note in notes:
            note.move()
            note.draw()
            if note.y > SCREEN_HEIGHT:  # remove notes off-screen
                notes.remove(note)
            elif note.y > hit_zone + ok_margin:
                hit_comment = "Miss!"
                zone_color = RED
                prev_points = 0
                combo = 1

        pygame.draw.line(screen, BLACK, (300, 0), (300, hit_zone), 2)
        pygame.draw.line(screen, BLACK, (400, 0), (400, hit_zone), 2)
        pygame.draw.line(screen, BLACK, (500, 0), (500, hit_zone), 2)
        pygame.draw.line(screen, BLACK, (600, 0), (600, hit_zone), 2)
        pygame.draw.line(screen, BLACK, (700, 0), (700, hit_zone), 2)

        # hit zone visual
        pygame.draw.line(screen, zone_color, (0, hit_zone), (SCREEN_WIDTH, hit_zone), zone_lineWidth)
        if zone_lineWidth > 2:  # return to regular width to create pulsing effect
            zone_lineWidth -= 1

        # Display score
        score_text = cornerFont.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Display comment based on user hit
        comment_text = cornerFont.render(f'{hit_comment}', True, BLACK)
        screen.blit(comment_text, (10, 45))
        frame_counter += 1

        if combo > 1:
            combo_text = cornerFont.render(combo_comment, True, RED)
            screen.blit(combo_text, (10, 80))

    # Update screen
    pygame.display.flip()

    # 60 fps
    clock.tick(60)

pygame.quit()