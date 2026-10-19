
import pygame
import sys

pygame.init()

# Fenetre du jeu
WIDTH = 600
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Camera-Based Tic-Tac-Toe")

# Couleurs
BACKGROUND = (245, 247, 250)
BLACK = (35, 40, 50)
BLUE = (65, 105, 225)
RED = (230, 75, 75)
WHITE = (255, 255, 255)

# Police
font = pygame.font.SysFont("arial", 42)
title_font = pygame.font.SysFont("arial", 34)

# Grille du jeu
board = [""] * 9
cell_size = 150
start_x = 75
start_y = 190

current_player = "X"
winner = None
draw = False


def draw_board():
    screen.fill(BACKGROUND)

    title = title_font.render(
        "TIC-TAC-TOE", True, BLACK
    )
    screen.blit(title, (185, 55))

    subtitle = pygame.font.SysFont("arial", 22).render(
        "Camera-Based Hand Gesture Game", True, BLACK
    )
    screen.blit(subtitle, (105, 110))

    for row in range(3):
        for col in range(3):
            index = row * 3 + col

            x = start_x + col * cell_size
            y = start_y + row * cell_size

            pygame.draw.rect(
                screen, WHITE,
                (x, y, cell_size, cell_size)
            )

            pygame.draw.rect(
                screen, BLUE,
                (x, y, cell_size, cell_size), 3
            )

            if board[index] != "":
                color = BLUE if board[index] == "X" else RED
                text = font.render(board[index], True, color)
                text_rect = text.get_rect(
                    center=(x + cell_size // 2,
                            y + cell_size // 2)
                )
                screen.blit(text, text_rect)

    if winner:
        message = f"Player {winner} wins!"
    elif draw:
        message = "It's a draw!"
    else:
        message = f"Player {current_player}'s turn"

    status = pygame.font.SysFont("arial", 28).render(
        message, True, BLACK
    )
    screen.blit(status, (160, 660))

    pygame.display.flip()


def check_winner():
    winning_lines = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]

    for a, b, c in winning_lines:
        if board[a] == board[b] == board[c] != "":
            return board[a]

    return None


def reset_game():
    global board, current_player, winner, draw
    board = [""] * 9
    current_player = "X"
    winner = None
    draw = False


running = True

while running:
    draw_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if winner or draw:
                reset_game()
                continue

            mouse_x, mouse_y = event.pos

            if (start_x <= mouse_x < start_x + 3 * cell_size
                    and start_y <= mouse_y < start_y + 3 * cell_size):

                col = (mouse_x - start_x) // cell_size
                row = (mouse_y - start_y) // cell_size
                index = row * 3 + col

                if board[index] == "":
                    board[index] = current_player

                    winner = check_winner()

                    if not winner and "" not in board:
                        draw = True

                    if not winner and not draw:
                        current_player = (
                            "O" if current_player == "X" else "X"
                        )

pygame.quit()
sys.exit()
