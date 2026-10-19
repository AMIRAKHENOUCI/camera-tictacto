
import pygame
import sys
import os
import math
import random
from hand_control import HandController
from ai import best_move
pygame.init()

# ==========================================
# FENETRE
# ==========================================
WIDTH, HEIGHT = 640, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ITC | Neon Tic-Tac-Toe")

clock = pygame.time.Clock()
hand = HandController(cam_index=0, show_preview=True)
FPS = 60

# ==========================================
# COULEURS ITC
# ==========================================
BLACK = (10, 10, 13)
PANEL = (25, 25, 32)
PANEL_LIGHT = (38, 38, 47)
RED = (255, 35, 55)
RED_LIGHT = (255, 85, 100)
RED_DARK = (130, 15, 30)
WHITE = (245, 245, 250)
GRAY = (150, 150, 165)
MUTED = (80, 80, 95)
GREEN = (70, 255, 160)

# ==========================================
# POLICES
# ==========================================
font_title = pygame.font.SysFont("arial", 38, bold=True)
font_subtitle = pygame.font.SysFont("arial", 15)
font_small = pygame.font.SysFont("arial", 14, bold=True)
font_status = pygame.font.SysFont("arial", 18, bold=True)
font_score = pygame.font.SysFont("arial", 25, bold=True)
font_tiny = pygame.font.SysFont("arial", 12, bold=True)
font_button = pygame.font.SysFont("arial", 16, bold=True)

# ==========================================
# LOGO ITC
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "NoBG-LOGO1.png")

logo_image = None

try:
    original_logo = pygame.image.load(LOGO_PATH).convert_alpha()

    max_logo_width = 150
    max_logo_height = 90

    original_width, original_height = original_logo.get_size()

    scale = min(
        max_logo_width / original_width,
        max_logo_height / original_height,
        1.0
    )

    logo_image = pygame.transform.smoothscale(
        original_logo,
        (
            max(1, int(original_width * scale)),
            max(1, int(original_height * scale))
        )
    )

except (pygame.error, OSError) as error:
    print("Logo introuvable :", error)
    print("Vérifie le fichier NoBG-LOGO1.png.")

# ==========================================
# PLATEAU
# ==========================================
BOARD_SIZE = 350
CELL_SIZE = BOARD_SIZE // 3
BOARD_X = (WIDTH - BOARD_SIZE) // 2
BOARD_Y = 255

board_rect = pygame.Rect(
    BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE
)

# ==========================================
# ETAT DU JEU
# ==========================================
board = [""] * 9
current_player = "X"
winner = None
game_over = False
winning_line = None

scores = {"X": 0, "O": 0}
game_mode = "2P"     
ai_timer = None
AI_DELAY = 0.6
symbol_birth = {}

# Boutons
restart_button = pygame.Rect(30, 635, 185, 40)
reset_scores_button = pygame.Rect(225, 635, 185, 40)
mode_button = pygame.Rect(420, 635, 190, 40)

# ==========================================
# PARTICULES LUMINEUSES
# ==========================================
particles = []

for _ in range(40):
    particles.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "speed": random.uniform(0.2, 0.8),
        "radius": random.choice([1, 1, 2]),
        "phase": random.uniform(0, math.tau)
    })


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def draw_text(text, font, color, x, y, center=True):
    surface = font.render(text, True, color)
    rect = surface.get_rect()

    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))

    screen.blit(surface, rect)


def draw_glow_rect(rect, color, radius=12, intensity=2):
    for layer in range(intensity, 0, -1):
        padding = layer * 2

        glow = pygame.Surface(
            (rect.width + padding * 2,
             rect.height + padding * 2),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            glow,
            (*color, 18),
            glow.get_rect(),
            border_radius=radius + padding
        )

        screen.blit(
            glow,
            (rect.x - padding, rect.y - padding)
        )

    pygame.draw.rect(
        screen, color, rect, 1, border_radius=radius
    )


def draw_particles(time_value):
    for p in particles:
        p["y"] -= p["speed"]

        if p["y"] < -3:
            p["y"] = HEIGHT + 3
            p["x"] = random.randint(0, WIDTH)

        pulse = (
            math.sin(time_value * 3 + p["phase"]) + 1
        ) / 2

        brightness = int(65 + pulse * 110)

        pygame.draw.circle(
            screen,
            (brightness, 20, 35),
            (int(p["x"]), int(p["y"])),
            p["radius"]
        )


# ==========================================
# RESET ROUND
# ==========================================
def reset_round():
    global board, current_player, winner
    global game_over, winning_line, symbol_birth, ai_timer

    board = [""] * 9
    current_player = "X"
    winner = None
    game_over = False
    winning_line = None
    symbol_birth = {}
    ai_timer = None


# ==========================================
# VERIFIER LE GAGNANT
# ==========================================
def check_winner():
    global winning_line

    combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]

    for a, b, c in combinations:
        if (
            board[a] != ""
            and board[a] == board[b]
            and board[b] == board[c]
        ):
            winning_line = (a, b, c)
            return board[a]

    return None


# ==========================================
# POSITION SOURIS
# ==========================================
def get_cell_from_mouse(pos):
    if not board_rect.collidepoint(pos):
        return None

    col = min((pos[0] - BOARD_X) // CELL_SIZE, 2)
    row = min((pos[1] - BOARD_Y) // CELL_SIZE, 2)

    return int(row * 3 + col)


def cell_center(index):
    row = index // 3
    col = index % 3

    return (
        BOARD_X + col * CELL_SIZE + CELL_SIZE // 2,
        BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2
    )


# ==========================================
# FOND ET HEADER
# ==========================================
def draw_background(time_value):
    screen.fill(BLACK)
    draw_particles(time_value)

    pulse = (math.sin(time_value * 3) + 1) / 2
    red_value = int(160 + pulse * 95)

    pygame.draw.rect(
        screen, (red_value, 15, 30), (0, 0, WIDTH, 4)
    )

    # Logo
    if logo_image:
        logo_rect = logo_image.get_rect()
        logo_rect.midleft = (22, 55)
        screen.blit(logo_image, logo_rect)
    else:
        draw_text("ITC", font_score, WHITE, 55, 55)

    # Titre
    draw_text(
        "TIC - TAC - TOE",
        font_title, WHITE, WIDTH // 2, 35
    )

    draw_text(
        "IT COMMUNITY / WELCOME DAY",
        font_subtitle, GRAY, WIDTH // 2, 65
    )

    draw_text(
        "NEON GAMING EDITION",
        font_tiny, RED_LIGHT, WIDTH // 2, 87
    )

    line_width = int(140 + pulse * 100)

    pygame.draw.line(
        screen, RED,
        (WIDTH // 2 - line_width, 110),
        (WIDTH // 2 + line_width, 110), 2
    )


# ==========================================
# CARTES JOUEURS
# ==========================================
def draw_player_cards(time_value):
    card_width = 225
    card_height = 75
    y = 125

    cards = [
        (pygame.Rect(55, y, card_width, card_height), "X", RED),
        (pygame.Rect(360, y, card_width, card_height), "O", WHITE)
    ]

    for rect, symbol, symbol_color in cards:
        active = current_player == symbol and not game_over

        pygame.draw.rect(
            screen, PANEL, rect, border_radius=12
        )

        edge = RED_LIGHT if active else MUTED

        if active:
            draw_glow_rect(rect, edge, 12, 2)
        else:
            pygame.draw.rect(
                screen, edge, rect, 1, border_radius=12
            )

        # Nom du joueur
        draw_text(
            f"PLAYER {symbol}", font_small, GRAY,
            rect.centerx, rect.y + 17
        )

        # Symbole du joueur
        draw_text(
            symbol, font_score, symbol_color,
            rect.x + 55, rect.y + 49
        )

        # Score
        draw_text(
            str(scores[symbol]), font_score, WHITE,
            rect.right - 40, rect.y + 49
        )

        # Tour du joueur
        if active:
            draw_text(
                "YOUR TURN", font_tiny, RED_LIGHT,
                rect.centerx, rect.bottom - 10
            )


# ==========================================
# STATUT DU JEU
# ==========================================
def draw_status(time_value):
    if winner:
        message = f"PLAYER {winner} WINS!"
        color = GREEN
    elif game_over:
        message = "IT'S A DRAW!"
        color = RED_LIGHT
    else:
        message = f"PLAYER {current_player}'S TURN"
        color = WHITE

    pulse = 0.9 + 0.1 * math.sin(time_value * 4)

    draw_text(
        message,
        font_status,
        tuple(int(c * pulse) for c in color),
        WIDTH // 2,
        230
    )


# ==========================================
# PLATEAU DE JEU
# ==========================================
def draw_board(time_value):
    pulse = (math.sin(time_value * 3) + 1) / 2

    edge_color = (
        190 + int(pulse * 65),
        15,
        35
    )

    draw_glow_rect(board_rect, edge_color, 12, 3)

    pygame.draw.rect(
        screen, PANEL, board_rect, border_radius=12
    )

    # Cases
    for index in range(9):
        row = index // 3
        col = index % 3

        x = BOARD_X + col * CELL_SIZE
        y = BOARD_Y + row * CELL_SIZE

        cell_rect = pygame.Rect(
            x + 5, y + 5,
            CELL_SIZE - 10, CELL_SIZE - 10
        )

        pygame.draw.rect(
            screen, (22, 22, 29),
            cell_rect, border_radius=8
        )

        # Effet au survol
        if (
            cell_rect.collidepoint(pointer_pos())
            and not game_over
            and board[index] == ""
        ):
            hover = pygame.Surface(
                cell_rect.size, pygame.SRCALPHA
            )

            pygame.draw.rect(
                hover, (255, 30, 50, 30),
                hover.get_rect(), border_radius=8
            )

            screen.blit(hover, cell_rect.topleft)

        symbol = board[index]

        if symbol:
            born = symbol_birth.get(index, time_value)
            progress = clamp(
                (time_value - born) / 0.20, 0, 1
            )

            scale = 0.4 + 0.6 * progress
            center = cell_rect.center

            # X plus grand et plus epais
            half = int(34 * scale)
            thickness = max(3, int(10 * scale))

            if symbol == "X":
                pygame.draw.line(
                    screen, RED_LIGHT,
                    (center[0] - half, center[1] - half),
                    (center[0] + half, center[1] + half),
                    thickness
                )

                pygame.draw.line(
                    screen, RED_LIGHT,
                    (center[0] + half, center[1] - half),
                    (center[0] - half, center[1] + half),
                    thickness
                )

            # O plus grand et plus epais
            else:
                pygame.draw.circle(
                    screen, WHITE, center,
                    max(2, int(34 * scale)),
                    max(3, int(9 * scale))
                )

    # Lignes du plateau
    for i in (1, 2):
        x = BOARD_X + i * CELL_SIZE
        y = BOARD_Y + i * CELL_SIZE

        pygame.draw.line(
            screen, edge_color,
            (x, BOARD_Y + 8),
            (x, BOARD_Y + BOARD_SIZE - 8), 3
        )

        pygame.draw.line(
            screen, edge_color,
            (BOARD_X + 8, y),
            (BOARD_X + BOARD_SIZE - 8, y), 3
        )

    # Ligne gagnante
    if winning_line:
        pygame.draw.line(
            screen, GREEN,
            cell_center(winning_line[0]),
            cell_center(winning_line[2]), 7
        )


# ==========================================
# BOUTONS
# ==========================================
def draw_button(rect, label, primary=True):
    hovered = rect.collidepoint(pointer_pos())

    if primary:
        color = RED if hovered else RED_DARK
        edge = RED_LIGHT
    else:
        color = PANEL_LIGHT if hovered else PANEL
        edge = RED_LIGHT if hovered else MUTED

    pygame.draw.rect(
        screen, color, rect, border_radius=12
    )

    if hovered:
        draw_glow_rect(rect, edge, 12, 2)
    else:
        pygame.draw.rect(
            screen, edge, rect, 1, border_radius=12
        )

    draw_text(
        label, font_button, WHITE,
        rect.centerx, rect.centery
    )


# ==========================================
# FOOTER
# ==========================================
def draw_footer():
    pygame.draw.line(
        screen, MUTED, (35, 685), (WIDTH - 35, 685), 1
    )

    draw_text(
        "IT COMMUNITY - BLIDA 1",
        font_tiny, GRAY, WIDTH // 2, 702
    )


# ==========================================
# INTERFACE
# ==========================================
def draw_interface(time_value):
    draw_background(time_value)
    draw_player_cards(time_value)
    draw_status(time_value)
    draw_board(time_value)

    draw_button(restart_button, "RESTART", True)
    draw_button(reset_scores_button, "RESET SCORES", False)

    mode_label = {
        "2P": "2 PLAYERS",
        "EASY": "VS AI: EASY",
        "HARD": "VS AI: HARD",
    }[game_mode]
    draw_button(mode_button, mode_label, False)

    draw_footer()
    if hand.cursor:
        pos = (int(hand.cursor[0]), int(hand.cursor[1]))
        color = GREEN if hand.pinching else RED_LIGHT
        pygame.draw.circle(screen, color, pos, 14, 3)
        pygame.draw.circle(screen, color, pos, 3)

    pygame.display.flip()


# ==========================================
# BOUCLE PRINCIPALE
# ==========================================
running = True
start_ticks = pygame.time.get_ticks()


def pointer_pos():
    return hand.cursor if hand.cursor else pygame.mouse.get_pos()


def place_move(index, time_value):
    global winner, game_over, current_player

    board[index] = current_player
    symbol_birth[index] = time_value

    winner = check_winner()

    if winner:
        game_over = True
        scores[winner] += 1
    elif "" not in board:
        game_over = True
    else:
        current_player = "O" if current_player == "X" else "X"


def is_ai_turn():
    return game_mode != "2P" and current_player == "O" and not game_over


def handle_click(pos, time_value):
    global game_mode

    if restart_button.collidepoint(pos):
        reset_round()

    elif reset_scores_button.collidepoint(pos):
        scores["X"] = 0
        scores["O"] = 0
        reset_round()

    elif mode_button.collidepoint(pos):
        modes = ["2P", "EASY", "HARD"]
        game_mode = modes[(modes.index(game_mode) + 1) % 3]
        scores["X"] = 0
        scores["O"] = 0
        reset_round()

    elif not game_over and not is_ai_turn():
        index = get_cell_from_mouse(pos)

        if index is not None and board[index] == "":
            place_move(index, time_value)


def update_ai(time_value):
    global ai_timer

    if not is_ai_turn():
        ai_timer = None
        return

    if ai_timer is None:
        ai_timer = time_value + AI_DELAY
        return

    if time_value >= ai_timer:
        level = "easy" if game_mode == "EASY" else "hard"
        move = best_move(board, "O", "X", level)
        ai_timer = None
        place_move(move, time_value)

while running:
    time_value = (
        pygame.time.get_ticks() - start_ticks
    ) / 1000

    hand.update(WIDTH, HEIGHT)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_click(event.pos, time_value)

    if hand.clicked and hand.cursor:
        handle_click((int(hand.cursor[0]), int(hand.cursor[1])), time_value)


    update_ai(time_value)
    draw_interface(time_value)  
    clock.tick(FPS)

hand.close()
pygame.quit()
sys.exit()
