import json
import math
import os
import random
import pygame

pygame.init()

display_info = pygame.display.Info()
WIDTH = min(1040, max(520, display_info.current_w - 60))
HEIGHT = min(860, max(620, display_info.current_h - 90))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Memory Cards - Scoreboard Edition")
clock = pygame.time.Clock()

LIMIT_SECONDS = 60
FLIP_MS = 220
MISMATCH_MS = 600
SCORES_FILE = os.path.join(os.path.dirname(__file__), "scores.json")

# رنگ‌ها
WHITE = (245, 248, 255)
MUTED = (155, 170, 205)
CYAN = (65, 226, 255)
PINK = (255, 92, 160)
PANEL = (24, 34, 62)
BORDER = (60, 78, 120)
GOLD = (255, 215, 0)

PALETTE = [
    (255, 107, 107), (78, 205, 196), (255, 230, 109), (170, 111, 255),
    (255, 159, 243), (84, 160, 255), (95, 227, 161),  (254, 202, 87),
    (255, 121, 198), (139, 233, 253), (80, 250, 123), (255, 184, 108),
    (189, 147, 249), (255, 85, 85),   (241, 250, 140), (100, 215, 240)
]

TITLE_FONT = pygame.font.SysFont("arial", 36, bold=True)
HEADING_FONT = pygame.font.SysFont("arial", 26, bold=True)
TEXT_FONT = pygame.font.SysFont("arial", 18, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 14)
STAT_FONT = pygame.font.SysFont("arial", 22, bold=True)

# ----------------- سیستم ذخیره‌سازی Scoreboard -----------------
def load_scores():
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_score(player_name, grid_size, time_taken, moves, score):
    scores = load_scores()
    record = {
        "name": player_name.strip() if player_name.strip() else "Player",
        "grid": f"{grid_size}x{grid_size}",
        "time": time_taken,
        "moves": moves,
        "score": score
    }
    scores.append(record)
    scores.sort(key=lambda x: (x["time"], x["moves"]))
    scores = scores[:20]
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

# ----------------- رسم وکتور آیکون‌ها -----------------
def render_icon(surface, icon_id, size):
    cx, cy = size // 2, size // 2
    r = int(size * 0.36)
    color = PALETTE[(icon_id - 1) % len(PALETTE)]
    var = (icon_id - 1) % 10

    if var == 0:
        points = []
        spikes = 4 + (icon_id % 4)
        for i in range(spikes * 2):
            ang = -math.pi / 2 + i * math.pi / spikes
            rad = r if i % 2 == 0 else int(r * 0.45)
            points.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
        pygame.draw.polygon(surface, color, points)
    elif var == 1:
        pygame.draw.ellipse(surface, color, (cx - r, cy - r // 2, r * 2, r), max(2, size // 20))
        pygame.draw.circle(surface, WHITE, (cx, cy), max(3, r // 3))
        pygame.draw.circle(surface, color, (cx + int(r * 0.8), cy), max(2, r // 5))
    elif var == 2:
        pts = [(cx, cy - r), (cx + int(r * 0.8), cy), (cx, cy + r), (cx - int(r * 0.8), cy)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.line(surface, (20, 28, 50), (cx - int(r * 0.8), cy), (cx + int(r * 0.8), cy), max(2, size // 22))
    elif var == 3:
        pygame.draw.circle(surface, color, (cx, cy), r)
        pygame.draw.circle(surface, (22, 30, 52), (cx + int(r * 0.4), cy - int(r * 0.3)), int(r * 0.9))
    elif var == 4:
        w_half = max(3, r // 3)
        pts = [(cx + w_half, cy - r), (cx - r, cy + 2), (cx, cy + 2),
               (cx - w_half, cy + r), (cx + r, cy - 2), (cx, cy - 2)]
        pygame.draw.polygon(surface, color, pts)
    elif var == 5:
        petals = 5 + (icon_id % 3)
        for i in range(petals):
            ang = i * (2 * math.pi / petals)
            px = cx + math.cos(ang) * (r * 0.55)
            py = cy + math.sin(ang) * (r * 0.55)
            pygame.draw.circle(surface, color, (int(px), int(py)), max(3, r // 3))
        pygame.draw.circle(surface, WHITE, (cx, cy), max(2, r // 4))
    elif var == 6:
        for i in range(8):
            ang = i * math.pi / 4
            p1 = (cx + math.cos(ang) * (r * 0.6), cy + math.sin(ang) * (r * 0.6))
            p2 = (cx + math.cos(ang) * r, cy + math.sin(ang) * r)
            pygame.draw.line(surface, color, p1, p2, max(2, size // 18))
        pygame.draw.circle(surface, color, (cx, cy), max(3, int(r * 0.45)))
    elif var == 7:
        hr = int(r * 0.48)
        pygame.draw.circle(surface, color, (cx - hr // 2, cy - hr // 2), hr)
        pygame.draw.circle(surface, color, (cx + hr // 2, cy - hr // 2), hr)
        pts = [(cx - hr - 2, cy - hr // 4), (cx + hr + 2, cy - hr // 4), (cx, cy + r)]
        pygame.draw.polygon(surface, color, pts)
    elif var == 8:
        pts = [(cx, cy - r), (cx + r, cy - int(r * 0.4)), (cx + int(r * 0.7), cy + int(r * 0.6)),
               (cx, cy + r), (cx - int(r * 0.7), cy + int(r * 0.6)), (cx - r, cy - int(r * 0.4))]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.circle(surface, WHITE, (cx, cy), max(2, r // 4))
    else:
        pygame.draw.circle(surface, color, (cx, cy), r, max(2, size // 16))
        pygame.draw.circle(surface, WHITE, (cx, cy), int(r * 0.6), max(2, size // 18))
        pygame.draw.circle(surface, color, (cx, cy), int(r * 0.25))

ICON_CACHE = {}
def get_card_icon(icon_id, size):
    key = (icon_id, size)
    if key in ICON_CACHE:
        return ICON_CACHE[key]
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    render_icon(surf, icon_id, size)
    ICON_CACHE[key] = surf
    return surf

# ----------------- پس‌زمینه و ظاهر -----------------
def make_background():
    surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = (int(9 + t * 10), int(14 + t * 14), int(30 + t * 24))
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))

    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for x, y, col in [(110, 110, (110, 60, 220)), (WIDTH - 100, HEIGHT - 100, (20, 160, 210))]:
        for r in range(250, 40, -30):
            pygame.draw.circle(glow, (*col, 8), (x, y), r)
    surface.blit(glow, (0, 0))

    rng = random.Random(42)
    for _ in range(60):
        pygame.draw.circle(surface, (80, 100, 140), (rng.randrange(WIDTH), rng.randrange(HEIGHT)), 1)
    return surface

BACKGROUND = make_background()

def text(msg, font, color, center=None, topleft=None):
    img = font.render(str(msg), True, color)
    rect = img.get_rect()
    if center: rect.center = center
    elif topleft: rect.topleft = topleft
    screen.blit(img, rect)

def button(rect, label, mouse, subtitle=None, accent=CYAN):
    hovered = rect.collidepoint(mouse)
    fill = (38, 56, 92) if hovered else PANEL
    outline = accent if hovered else BORDER

    pygame.draw.rect(screen, (5, 9, 22), rect.move(0, 4), border_radius=14)
    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, outline, rect, 2, border_radius=14)

    if subtitle:
        text(label, HEADING_FONT, WHITE, center=(rect.centerx, rect.centery - 12))
        text(subtitle, SMALL_FONT, MUTED, center=(rect.centerx, rect.centery + 18))
    else:
        text(label, TEXT_FONT, WHITE, center=rect.center)

def size_buttons():
    gap = 14
    total_w = min(WIDTH - 50, 680)
    btn_w = (total_w - 2 * gap) // 3
    left = (WIDTH - total_w) // 2
    top = HEIGHT // 2 + 10
    return [(s, pygame.Rect(left + i * (btn_w + gap), top, btn_w, 85)) for i, s in enumerate((6, 8, 10))]

def board_layout(size):
    panel = pygame.Rect(20, 185, WIDTH - 40, HEIGHT - 245)
    gap = {6: 10, 8: 6, 10: 4}[size]
    card_size = min((panel.width - 32 - (size - 1) * gap) // size,
                    (panel.height - 32 - (size - 1) * gap) // size)

    grid_w = size * card_size + (size - 1) * gap
    grid_h = grid_w
    start_x = panel.centerx - grid_w // 2
    start_y = panel.centery - grid_h // 2

    rects = []
    for r in range(size):
        for c in range(size):
            rects.append(pygame.Rect(start_x + c * (card_size + gap),
                                     start_y + r * (card_size + gap),
                                     card_size, card_size))
    return panel, rects, card_size

# ----------------- منطق بازی -----------------
def new_game(size, player_name):
    pairs_needed = (size * size) // 2
    values = list(range(1, pairs_needed + 1)) * 2
    random.shuffle(values)

    cards = [{
        "val": val, "face": False, "matched": False,
        "flip_start": -1, "before": False, "after": False
    } for val in values]

    now = pygame.time.get_ticks()
    clean_name = player_name.strip() if player_name.strip() else "Player"
    return {
        "size": size,
        "cards": cards,
        "selected": [],
        "phase": "idle",
        "show_until": 0,
        "start_time": now,
        "deadline": now + LIMIT_SECONDS * 1000,
        "score": 0,
        "moves": 0,
        "pairs": 0,
        "mode": "playing",
        "win_time_taken": 0,
        "player_name": clean_name,
        "score_saved": False
    }

def start_flip(card, face_up, now):
    card["before"] = card["face"]
    card["after"] = face_up
    card["flip_start"] = now

def choose_card(game, idx, now):
    if game["mode"] != "playing" or game["phase"] != "idle":
        return
    if now >= game["deadline"]:
        game["mode"] = "lost"
        return

    cards = game["cards"]
    if any(c["flip_start"] >= 0 for c in cards):
        return

    c = cards[idx]
    if c["face"] or c["matched"]:
        return

    start_flip(c, True, now)
    game["selected"].append(idx)

    if len(game["selected"]) == 2:
        game["moves"] += 1
        game["phase"] = "checking"

def update_game(game, now):
    if game["mode"] != "playing":
        return

    if now >= game["deadline"]:
        game["mode"] = "lost"
        return

    cards = game["cards"]
    for c in cards:
        if c["flip_start"] >= 0 and now - c["flip_start"] >= FLIP_MS:
            c["face"] = c["after"]
            c["flip_start"] = -1

    sel = game["selected"]
    if game["phase"] == "checking":
        if all(cards[i]["flip_start"] < 0 for i in sel):
            c1, c2 = cards[sel[0]], cards[sel[1]]
            if c1["val"] == c2["val"]:
                c1["matched"] = True
                c2["matched"] = True
                game["pairs"] += 1
                game["score"] += 100
                sel.clear()
                game["phase"] = "idle"
                if game["pairs"] == (game["size"] ** 2) // 2:
                    game["mode"] = "won"
                    game["win_time_taken"] = round((now - game["start_time"]) / 1000, 1)
            else:
                game["show_until"] = now + MISMATCH_MS
                game["phase"] = "waiting"

    elif game["phase"] == "waiting":
        if now >= game["show_until"]:
            for i in sel:
                start_flip(cards[i], False, now)
            game["phase"] = "closing"

    elif game["phase"] == "closing":
        if all(cards[i]["flip_start"] < 0 for i in sel):
            sel.clear()
            game["phase"] = "idle"

# ----------------- رسم کارت‌ها -----------------
def draw_card(card, rect, now, mouse):
    size = rect.width
    if card["flip_start"] >= 0:
        progress = min(1.0, (now - card["flip_start"]) / FLIP_MS)
        visible_face = card["before"] if progress < 0.5 else card["after"]
        vis_w = max(1, round(size * abs(1.0 - 2.0 * progress)))
    else:
        visible_face = card["face"]
        vis_w = size

    card_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    radius = max(6, size // 8)

    if visible_face:
        fill = (22, 30, 52)
        border_col = CYAN if card["matched"] else WHITE
        pygame.draw.rect(card_surf, fill, (0, 0, size, size), border_radius=radius)
        icon = get_card_icon(card["val"], size)
        card_surf.blit(icon, (0, 0))
        pygame.draw.rect(card_surf, border_col, (0, 0, size, size), 2, border_radius=radius)
    else:
        hovered = rect.collidepoint(mouse)
        fill = (34, 48, 82) if hovered else (28, 40, 70)
        border_col = CYAN if hovered else BORDER
        pygame.draw.rect(card_surf, fill, (0, 0, size, size), border_radius=radius)
        pygame.draw.rect(card_surf, border_col, (0, 0, size, size), 2, border_radius=radius)

        q_size = max(14, size // 2)
        q_font = pygame.font.SysFont("arial", q_size, bold=True)
        q_txt = q_font.render("?", True, CYAN if hovered else MUTED)
        card_surf.blit(q_txt, q_txt.get_rect(center=(size // 2, size // 2)))

    pygame.draw.rect(screen, (4, 8, 20), rect.move(0, 3), border_radius=radius)
    if vis_w != size:
        card_surf = pygame.transform.smoothscale(card_surf, (vis_w, size))
    screen.blit(card_surf, (rect.centerx - vis_w // 2, rect.y))

# ----------------- صفحه اسکوربورد (Scoreboard Screen) -----------------
def draw_leaderboard(mouse):
    screen.blit(BACKGROUND, (0, 0))
    text("HALL OF FAME / SCOREBOARD", TITLE_FONT, GOLD, center=(WIDTH // 2, 70))
    text("Fastest victories across all grid maps", SMALL_FONT, MUTED, center=(WIDTH // 2, 110))

    panel = pygame.Rect((WIDTH - 760) // 2, 140, 760, HEIGHT - 230)
    pygame.draw.rect(screen, PANEL, panel, border_radius=18)
    pygame.draw.rect(screen, BORDER, panel, 2, border_radius=18)

    headers = [("RANK", panel.x + 40), ("PLAYER", panel.x + 150), ("MAP", panel.x + 330),
               ("TIME (s)", panel.x + 460), ("MOVES", panel.x + 590), ("SCORE", panel.x + 690)]
    for h, x in headers:
        text(h, TEXT_FONT, CYAN, center=(x, panel.y + 35))

    pygame.draw.line(screen, BORDER, (panel.x + 20, panel.y + 60), (panel.right - 20, panel.y + 60), 1)

    scores = load_scores()
    if not scores:
        text("No winners yet! Win a match to get your name here.", HEADING_FONT, MUTED, center=panel.center)
    else:
        y_offset = panel.y + 90
        for i, s in enumerate(scores[:10]):
            rank_col = GOLD if i == 0 else (CYAN if i < 3 else WHITE)
            text(f"#{i+1}", TEXT_FONT, rank_col, center=(panel.x + 40, y_offset))
            text(str(s["name"])[:14], TEXT_FONT, WHITE, center=(panel.x + 150, y_offset))
            text(str(s["grid"]), SMALL_FONT, MUTED, center=(panel.x + 330, y_offset))
            text(f"{s['time']}s", STAT_FONT, CYAN, center=(panel.x + 460, y_offset))
            text(str(s["moves"]), SMALL_FONT, WHITE, center=(panel.x + 590, y_offset))
            text(str(s["score"]), SMALL_FONT, PINK, center=(panel.x + 690, y_offset))
            y_offset += 40

    back_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 70, 200, 44)
    button(back_btn, "BACK TO MENU", mouse)

# ----------------- صفحه اصلی با فیلد ورودی نام -----------------
def draw_menu(player_name, input_active, now):
    screen.blit(BACKGROUND, (0, 0))
    mouse = pygame.mouse.get_pos()

    text("NEON MEMORY CARDS", TITLE_FONT, WHITE, center=(WIDTH // 2, HEIGHT // 2 - 200))
    text("Enter your name, pick a map size, and beat the 60s timer!", SMALL_FONT, MUTED, center=(WIDTH // 2, HEIGHT // 2 - 160))

    # جعبه ورودی نام بازیکن (Input Box)
    input_w = 340
    input_box = pygame.Rect((WIDTH - input_w) // 2, HEIGHT // 2 - 110, input_w, 48)
    box_border = CYAN if input_active else BORDER
    pygame.draw.rect(screen, PANEL, input_box, border_radius=12)
    pygame.draw.rect(screen, box_border, input_box, 2, border_radius=12)

    # نمایش نام یا متن پیش‌فرض
    if player_name:
        display_str = player_name
        # کرسر چشمک‌زن
        if input_active and (now // 500) % 2 == 0:
            display_str += "|"
        text(display_str, TEXT_FONT, WHITE, center=input_box.center)
    else:
        placeholder = "Click & type name..." if not input_active else "|"
        text(placeholder, TEXT_FONT, CYAN if input_active else MUTED, center=input_box.center)

    text("PLAYER NAME", SMALL_FONT, CYAN, center=(WIDTH // 2, input_box.y - 14))

    text("SELECT GRID MAP", TEXT_FONT, WHITE, center=(WIDTH // 2, HEIGHT // 2 - 20))
    for s, r in size_buttons():
        button(r, f"{s} x {s}", mouse, subtitle=f"{s * s // 2} pairs", accent=PINK if s == 10 else CYAN)

    sb_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 120, 240, 46)
    button(sb_btn, "LEADERBOARD", mouse, accent=GOLD)

    return input_box, sb_btn

def draw_game(game, now):
    screen.blit(BACKGROUND, (0, 0))
    mouse = pygame.mouse.get_pos()

    text("HIDDEN CARDS", HEADING_FONT, WHITE, topleft=(24, 18))
    text(f"Player: {game['player_name']}  |  Map: {game['size']}x{game['size']}", SMALL_FONT, CYAN, topleft=(26, 54))

    menu_btn = pygame.Rect(WIDTH - 150, 20, 126, 44)
    button(menu_btn, "MENU", mouse)

    rem = max(0, math.ceil((game["deadline"] - now) / 1000))
    stats = [
        ("SCORE", str(game["score"])),
        ("PAIRS", f"{game['pairs']} / {game['size'] ** 2 // 2}"),
        ("MOVES", str(game["moves"])),
        ("TIME", f"0:{rem:02d}" if rem < 60 else "1:00"),
    ]

    gap = 10
    w = (WIDTH - 40 - gap * 3) // 4
    for i, (lbl, val) in enumerate(stats):
        box = pygame.Rect(20 + i * (w + gap), 90, w, 68)
        pygame.draw.rect(screen, PANEL, box, border_radius=12)
        pygame.draw.rect(screen, BORDER, box, 1, border_radius=12)
        text(lbl, SMALL_FONT, MUTED, topleft=(box.x + 12, box.y + 8))
        v_col = PINK if lbl == "TIME" and rem <= 10 else CYAN
        text(val, STAT_FONT, v_col, topleft=(box.x + 12, box.y + 28))

    panel, rects, _ = board_layout(game["size"])
    pygame.draw.rect(screen, (16, 24, 44), panel, border_radius=20)
    pygame.draw.rect(screen, (45, 60, 95), panel, 1, border_radius=20)

    for c, r in zip(game["cards"], rects):
        draw_card(c, r, now, mouse)

    text("Press R to restart  |  ESC for menu", SMALL_FONT, MUTED, center=(WIDTH // 2, HEIGHT - 24))

    # پنجره پایان بازی
    if game["mode"] in ("won", "lost"):
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((4, 8, 22, 220))
        screen.blit(shade, (0, 0))

        popup = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 160, 400, 320)
        pygame.draw.rect(screen, PANEL, popup, border_radius=20)
        border_col = GOLD if game["mode"] == "won" else PINK
        pygame.draw.rect(screen, border_col, popup, 2, border_radius=20)

        if game["mode"] == "won":
            text("VICTORY!", HEADING_FONT, GOLD, center=(WIDTH // 2, popup.y + 35))
            text(f"Player: {game['player_name']}", TEXT_FONT, WHITE, center=(WIDTH // 2, popup.y + 68))
            text(f"Solved in {game['win_time_taken']}s on {game['size']}x{game['size']}!", SMALL_FONT, CYAN, center=(WIDTH // 2, popup.y + 96))
            
            if not game["score_saved"]:
                save_score(game["player_name"], game["size"], game["win_time_taken"], game["moves"], game["score"])
                game["score_saved"] = True
                
            text("Saved to Leaderboard!", SMALL_FONT, (120, 240, 150), center=(WIDTH // 2, popup.y + 122))
        else:
            text("TIME'S UP!", HEADING_FONT, PINK, center=(WIDTH // 2, popup.y + 45))
            text(f"Pairs matched: {game['pairs']} / {game['size']**2 // 2}", TEXT_FONT, MUTED, center=(WIDTH // 2, popup.y + 90))
            text("Better luck next time!", SMALL_FONT, MUTED, center=(WIDTH // 2, popup.y + 120))

        again_btn = pygame.Rect(WIDTH // 2 - 130, popup.y + 155, 260, 40)
        lb_btn = pygame.Rect(WIDTH // 2 - 130, popup.y + 203, 260, 40)
        back_btn = pygame.Rect(WIDTH // 2 - 130, popup.y + 251, 260, 40)

        button(again_btn, "PLAY AGAIN", mouse)
        button(lb_btn, "VIEW LEADERBOARD", mouse, accent=GOLD)
        button(back_btn, "CHANGE MAP / PLAYER", mouse)

# ----------------- حلقه اصلی -----------------
def main():
    game = None
    state = "menu"
    player_name = "Melika"
    input_active = False
    running = True

    while running:
        clock.tick(60)
        now = pygame.time.get_ticks()

        if state == "playing" and game:
            update_game(game, now)

        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if state == "menu":
                    if input_active:
                        if event.key == pygame.K_RETURN:
                            input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            player_name = player_name[:-1]
                        elif len(player_name) < 14 and event.unicode.isprintable():
                            player_name += event.unicode
                    else:
                        if event.key == pygame.K_RETURN:
                            # با زدن اینتر روی منو بازی 6x6 شروع می‌شود
                            game = new_game(6, player_name)
                            state = "playing"
                elif event.key == pygame.K_ESCAPE:
                    state = "menu"
                    game = None
                elif event.key == pygame.K_r and state == "playing" and game:
                    game = new_game(game["size"], player_name)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "menu":
                    input_box = pygame.Rect((WIDTH - 340) // 2, HEIGHT // 2 - 110, 340, 48)
                    if input_box.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False

                    for s, r in size_buttons():
                        if r.collidepoint(event.pos):
                            game = new_game(s, player_name)
                            state = "playing"
                            break

                    sb_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 120, 240, 46)
                    if sb_rect.collidepoint(event.pos):
                        state = "leaderboard"

                elif state == "leaderboard":
                    back_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 70, 200, 44)
                    if back_rect.collidepoint(event.pos):
                        state = "menu"

                elif state == "playing" and game:
                    menu_btn = pygame.Rect(WIDTH - 150, 20, 126, 44)
                    if game["mode"] in ("won", "lost"):
                        popup_y = HEIGHT // 2 - 160
                        again_btn = pygame.Rect(WIDTH // 2 - 130, popup_y + 155, 260, 40)
                        lb_btn = pygame.Rect(WIDTH // 2 - 130, popup_y + 203, 260, 40)
                        back_btn = pygame.Rect(WIDTH // 2 - 130, popup_y + 251, 260, 40)

                        if again_btn.collidepoint(event.pos):
                            game = new_game(game["size"], player_name)
                        elif lb_btn.collidepoint(event.pos):
                            state = "leaderboard"
                        elif back_btn.collidepoint(event.pos):
                            state = "menu"
                            game = None
                    elif menu_btn.collidepoint(event.pos):
                        state = "menu"
                        game = None
                    else:
                        _, rects, _ = board_layout(game["size"])
                        for idx, r in enumerate(rects):
                            if r.collidepoint(event.pos):
                                choose_card(game, idx, now)
                                break

        if state == "menu":
            draw_menu(player_name, input_active, now)
            pygame.display.flip()
        elif state == "leaderboard":
            draw_leaderboard(mouse)
            pygame.display.flip()
        elif state == "playing" and game:
            draw_game(game, now)
            pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
