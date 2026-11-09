import math
import random

import pygame


pygame.init()

WIDTH, HEIGHT = 960, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hidden Cards | Memory Game")
clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont("arial", 42, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 34, bold=True)
NUMBER_FONT = pygame.font.SysFont("arial", 25, bold=True)
TEXT_FONT = pygame.font.SysFont("arial", 18, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 15)
CARD_FONT = pygame.font.SysFont("arial", 14, bold=True)

WHITE = (241, 245, 255)
MUTED = (152, 164, 195)
PANEL = (24, 33, 62)
BORDER = (65, 79, 119)
CYAN = (65, 226, 255)
PINK = (255, 92, 159)

CARD_SIZE = 112
GAP = 14
GRID_X = (WIDTH - (4 * CARD_SIZE + 3 * GAP)) // 2
GRID_Y = 210

RESET_BUTTON = pygame.Rect(772, 34, 150, 46)
AGAIN_BUTTON = pygame.Rect(360, 463, 240, 54)

SYMBOLS = [
    ("STAR", (255, 205, 91)),
    ("MOON", (184, 158, 255)),
    ("GEM", (65, 226, 255)),
    ("ORBIT", (255, 130, 172)),
    ("BOLT", (255, 229, 108)),
    ("SUN", (255, 163, 89)),
    ("HEART", (255, 99, 138)),
    ("BLOOM", (125, 237, 184)),
]


def make_background():
    background = pygame.Surface((WIDTH, HEIGHT))

    for y in range(HEIGHT):
        t = y / HEIGHT
        color = (
            int(9 + 10 * t),
            int(13 + 12 * t),
            int(30 + 23 * t),
        )
        pygame.draw.line(background, color, (0, y), (WIDTH, y))

    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for x, y, color in [
        (110, 130, (85, 62, 195)),
        (850, 610, (20, 153, 198)),
    ]:
        for radius in range(270, 30, -25):
            pygame.draw.circle(glow, (*color, 7), (x, y), radius)

    background.blit(glow, (0, 0))

    rng = random.Random(12)
    for _ in range(65):
        x = rng.randrange(WIDTH)
        y = rng.randrange(HEIGHT)
        pygame.draw.circle(background, (82, 100, 145), (x, y), 1)

    return background


BACKGROUND = make_background()


def draw_text(surface, message, font, color, *, center=None, topleft=None):
    image = font.render(message, True, color)
    rect = image.get_rect()

    if center is not None:
        rect.center = center
    elif topleft is not None:
        rect.topleft = topleft

    surface.blit(image, rect)


def draw_symbol(surface, symbol_id, color):
    cx, cy = 56, 48

    if symbol_id == 0:  # Star
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            radius = 29 if i % 2 == 0 else 13
            points.append((
                int(cx + math.cos(angle) * radius),
                int(cy + math.sin(angle) * radius),
            ))
        pygame.draw.polygon(surface, color, points)

    elif symbol_id == 1:  # Moon
        pygame.draw.circle(surface, color, (cx, cy), 28)
        pygame.draw.circle(surface, (28, 37, 68), (cx + 12, cy - 10), 27)

    elif symbol_id == 2:  # Gem
        pygame.draw.polygon(
            surface, color,
            [(cx, cy - 31), (cx + 29, cy - 4),
             (cx, cy + 29), (cx - 29, cy - 4)]
        )
        pygame.draw.line(surface, (28, 37, 68),
                         (cx - 27, cy - 4), (cx + 27, cy - 4), 3)
        pygame.draw.line(surface, (28, 37, 68),
                         (cx, cy - 29), (cx - 10, cy - 4), 3)

    elif symbol_id == 3:  # Orbit
        pygame.draw.ellipse(
            surface, color, (cx - 34, cy - 14, 68, 28), 5
        )
        pygame.draw.circle(surface, color, (cx, cy), 16)
        pygame.draw.circle(surface, WHITE, (cx + 31, cy - 7), 5)

    elif symbol_id == 4:  # Bolt
        pygame.draw.polygon(
            surface, color,
            [(cx + 4, cy - 32), (cx - 19, cy + 4),
             (cx - 2, cy + 4), (cx - 9, cy + 32),
             (cx + 21, cy - 7), (cx + 5, cy - 7)]
        )

    elif symbol_id == 5:  # Sun
        for i in range(8):
            angle = i * math.pi / 4
            start = (
                int(cx + math.cos(angle) * 23),
                int(cy + math.sin(angle) * 23),
            )
            end = (
                int(cx + math.cos(angle) * 33),
                int(cy + math.sin(angle) * 33),
            )
            pygame.draw.line(surface, color, start, end, 4)
        pygame.draw.circle(surface, color, (cx, cy), 17)

    elif symbol_id == 6:  # Heart
        pygame.draw.circle(surface, color, (cx - 13, cy - 11), 17)
        pygame.draw.circle(surface, color, (cx + 13, cy - 11), 17)
        pygame.draw.polygon(
            surface, color,
            [(cx - 29, cy - 5), (cx + 29, cy - 5), (cx, cy + 32)]
        )

    elif symbol_id == 7:  # Bloom
        for i in range(8):
            angle = i * math.pi / 4
            px = int(cx + math.cos(angle) * 20)
            py = int(cy + math.sin(angle) * 20)
            pygame.draw.circle(surface, color, (px, py), 11)
        pygame.draw.circle(surface, (255, 246, 187), (cx, cy), 12)


def card_image(card, hovered):
    image = pygame.Surface((CARD_SIZE, CARD_SIZE), pygame.SRCALPHA)
    face_up = card["face"] or card["matched"]

    fill = (28, 37, 68) if face_up else (30, 43, 79)
    outline = CYAN if hovered and not face_up else BORDER

    if card["matched"]:
        outline = SYMBOLS[card["id"]][1]

    pygame.draw.rect(
        image, fill, (0, 0, CARD_SIZE, CARD_SIZE),
        border_radius=19
    )
    pygame.draw.rect(
        image, outline, (1, 1, CARD_SIZE - 2, CARD_SIZE - 2),
        2, border_radius=19
    )

    if face_up:
        name, color = SYMBOLS[card["id"]]
        draw_symbol(image, card["id"], color)
        draw_text(
            image, name, CARD_FONT, MUTED,
            center=(CARD_SIZE // 2, 91)
        )
    else:
        pygame.draw.circle(image, (49, 67, 109), (56, 56), 34, 2)
        pygame.draw.circle(image, (62, 88, 139), (56, 56), 25, 2)
        draw_text(
            image, "?", BIG_FONT, CYAN,
            center=(56, 54)
        )

    return image


def draw_button(rect, label, mouse_pos, *, bright=False):
    hovered = rect.collidepoint(mouse_pos)
    fill = (41, 70, 111) if hovered else PANEL
    border = CYAN if hovered or bright else BORDER

    pygame.draw.rect(screen, (4, 9, 23), rect.move(0, 5),
                     border_radius=14)
    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, border, rect, 2, border_radius=14)
    draw_text(screen, label, TEXT_FONT, WHITE, center=rect.center)


def new_game():
    values = list(range(8)) * 2
    random.shuffle(values)

    cards = []
    for index, value in enumerate(values):
        row, col = divmod(index, 4)
        rect = pygame.Rect(
            GRID_X + col * (CARD_SIZE + GAP),
            GRID_Y + row * (CARD_SIZE + GAP),
            CARD_SIZE,
            CARD_SIZE,
        )
        cards.append({
            "id": value,
            "rect": rect,
            "face": False,
            "target": False,
            "flip": 0.0,
            "matched": False,
        })

    return {
        "cards": cards,
        "chosen": [],
        "phase": "idle",
        "wait": 0.0,
        "score": 0,
        "moves": 0,
        "pairs": 0,
        "started_at": None,
        "finish_time": None,
        "won": False,
    }


def flip(card, face_up):
    card["target"] = face_up
    card["flip"] = 0.0001


def choose_card(game, index, now):
    if game["won"] or game["phase"] != "idle":
        return

    if any(card["flip"] > 0 for card in game["cards"]):
        return

    card = game["cards"][index]
    if card["face"] or card["matched"]:
        return

    if game["started_at"] is None:
        game["started_at"] = now

    flip(card, True)
    game["chosen"].append(index)

    if len(game["chosen"]) == 2:
        game["moves"] += 1
        game["phase"] = "checking"


def update_game(game, dt, now):
    for card in game["cards"]:
        if card["flip"] <= 0:
            continue

        previous = card["flip"]
        card["flip"] = min(1.0, previous + dt / 0.26)

        if previous < 0.5 <= card["flip"]:
            card["face"] = card["target"]

        if card["flip"] >= 1.0:
            card["flip"] = 0.0
            card["face"] = card["target"]

    chosen = game["chosen"]

    if game["phase"] == "checking":
        if all(game["cards"][i]["flip"] == 0 for i in chosen):
            first, second = (game["cards"][i] for i in chosen)

            if first["id"] == second["id"]:
                first["matched"] = True
                second["matched"] = True
                game["pairs"] += 1
                game["score"] += 100
                chosen.clear()
                game["phase"] = "idle"

                if game["pairs"] == 8:
                    game["won"] = True
                    game["finish_time"] = now
            else:
                game["wait"] = 0.85
                game["phase"] = "waiting"

    elif game["phase"] == "waiting":
        game["wait"] -= dt

        if game["wait"] <= 0:
            for i in chosen:
                flip(game["cards"][i], False)
            game["phase"] = "closing"

    elif game["phase"] == "closing":
        if all(game["cards"][i]["flip"] == 0 for i in chosen):
            chosen.clear()
            game["phase"] = "idle"


def elapsed_text(game, now):
    if game["started_at"] is None:
        seconds = 0
    else:
        end = game["finish_time"]
        seconds = int((now if end is None else end) - game["started_at"])

    return f"{seconds // 60}:{seconds % 60:02d}"


def draw_game(game, now):
    screen.blit(BACKGROUND, (0, 0))
    mouse = pygame.mouse.get_pos()

    draw_text(
        screen, "HIDDEN CARDS", TITLE_FONT, WHITE,
        topleft=(GRID_X, 27)
    )
    draw_text(
        screen, "Flip two. Find the pair. Keep the glow.",
        SMALL_FONT, MUTED, topleft=(GRID_X + 2, 82)
    )

    draw_button(RESET_BUTTON, "NEW GAME", mouse)

    stats = [
        ("SCORE", str(game["score"])),
        ("PAIRS", f"{game['pairs']} / 8"),
        ("MOVES", str(game["moves"])),
        ("TIME", elapsed_text(game, now)),
    ]

    for i, (label, value) in enumerate(stats):
        box = pygame.Rect(GRID_X + i * 126, 120, 112, 64)
        pygame.draw.rect(screen, PANEL, box, border_radius=14)
        pygame.draw.rect(screen, BORDER, box, 1, border_radius=14)
        draw_text(
            screen, label, SMALL_FONT, MUTED,
            topleft=(box.x + 13, box.y + 8)
        )
        draw_text(
            screen, value, NUMBER_FONT, CYAN if i == 0 else WHITE,
            topleft=(box.x + 13, box.y + 27)
        )

    board_panel = pygame.Rect(GRID_X - 20, GRID_Y - 18, 530, 526)
    pygame.draw.rect(
        screen, (17, 25, 48), board_panel, border_radius=25
    )
    pygame.draw.rect(
        screen, (45, 61, 99), board_panel, 1, border_radius=25
    )

    for card in game["cards"]:
        rect = card["rect"]
        pygame.draw.rect(
            screen, (5, 10, 26), rect.move(0, 7),
            border_radius=19
        )

        hovered = (
            rect.collidepoint(mouse)
            and not card["face"]
            and not game["won"]
        )
        image = card_image(card, hovered)

        if card["flip"] > 0:
            width = max(
                1,
                round(CARD_SIZE * abs(math.cos(math.pi * card["flip"])))
            )
            image = pygame.transform.smoothscale(
                image, (width, CARD_SIZE)
            )
            screen.blit(
                image, (rect.centerx - width // 2, rect.y)
            )
        else:
            screen.blit(image, rect.topleft)

    draw_text(
        screen, "Click a card to flip it  •  Press R to restart",
        SMALL_FONT, MUTED, center=(WIDTH // 2, 753)
    )

    if game["won"]:
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((5, 9, 25, 195))
        screen.blit(shade, (0, 0))

        popup = pygame.Rect(270, 260, 420, 280)
        pygame.draw.rect(
            screen, (26, 37, 68), popup, border_radius=24
        )
        pygame.draw.rect(
            screen, CYAN, popup, 2, border_radius=24
        )

        draw_text(
            screen, "YOU FOUND THEM ALL!", BIG_FONT, WHITE,
            center=(WIDTH // 2, 321)
        )
        draw_text(
            screen, f"Score: {game['score']}   •   Moves: {game['moves']}",
            TEXT_FONT, CYAN, center=(WIDTH // 2, 381)
        )
        draw_text(
            screen, f"Time: {elapsed_text(game, now)}",
            TEXT_FONT, MUTED, center=(WIDTH // 2, 412)
        )
        draw_button(AGAIN_BUTTON, "PLAY AGAIN", mouse, bright=True)

    pygame.display.flip()


def main():
    game = new_game()
    running = True

    while running:
        dt = min(clock.tick(60) / 1000, 0.05)
        now = pygame.time.get_ticks() / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game = new_game()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    continue

                if RESET_BUTTON.collidepoint(event.pos):
                    game = new_game()
                elif game["won"]:
                    if AGAIN_BUTTON.collidepoint(event.pos):
                        game = new_game()
                else:
                    for index, card in enumerate(game["cards"]):
                        if card["rect"].collidepoint(event.pos):
                            choose_card(game, index, now)
                            break

        update_game(game, dt, now)
        draw_game(game, now)

    pygame.quit()


if __name__ == "__main__":
    main()
