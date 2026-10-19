import random

LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]


def winner_of(board):
    for a, b, c in LINES:
        if board[a] != "" and board[a] == board[b] == board[c]:
            return board[a]
    return None


def _minimax(board, turn, ai, human, depth):
    """Retourne le score du plateau : + si l'IA gagne, - si l'humain gagne."""
    win = winner_of(board)

    if win == ai:
        return 10 - depth      # gagner vite = meilleur score
    if win == human:
        return depth - 10      # perdre tard = moins mauvais
    if "" not in board:
        return 0

    scores = []

    for i in range(9):
        if board[i] == "":
            board[i] = turn
            next_turn = human if turn == ai else ai
            scores.append(_minimax(board, next_turn, ai, human, depth + 1))
            board[i] = ""

    return max(scores) if turn == ai else min(scores)


def best_move(board, ai="O", human="X", difficulty="hard"):
    """
    difficulty = "easy" : coup au hasard
    difficulty = "hard" : minimax (imbattable)
    """
    empty = [i for i in range(9) if board[i] == ""]

    if not empty:
        return None

    if difficulty == "easy":
        return random.choice(empty)

    best_score = -100
    best_moves = []

    for i in empty:
        board[i] = ai
        score = _minimax(board, human, ai, human, 1)
        board[i] = ""

        if score > best_score:
            best_score = score
            best_moves = [i]
        elif score == best_score:
            best_moves.append(i)

    # Si plusieurs coups sont equivalents, on en choisit un au hasard
    return random.choice(best_moves)