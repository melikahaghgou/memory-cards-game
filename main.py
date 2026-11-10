import pygame
import os
import json
import random
import tempfile
import math

# ---------- تنظیمات اولیه ----------
pygame.init()

WIDTH, HEIGHT = 1024, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Memory Cards")
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 24)
SMALL_FONT = pygame.font.SysFont("arial", 19)
BIG_FONT = pygame.font.SysFont("arial", 48, bold=True)
CARD_FONT = pygame.font.SysFont("arial", 26, bold=True)

# پالت رنگی نئونی
BG = (13, 15, 29)
PANEL = (25, 29, 51)
PANEL_HOVER = (41, 48, 78)
CYAN = (47, 231, 244)
PURPLE = (171, 94, 255)
WHITE = (239, 242, 255)
MUTED = (149, 159, 185)
GOLD = (255, 210, 89)
GREEN = (75, 220, 165)
RED = (255, 116, 130)
PINK = (255, 130, 220)
BLUE = (100, 160, 255)
ORANGE = (255, 150, 70)

GRID_SIZES = (4, 6, 8, 10)

# زمان بازی (ثانیه) برای هر مپ؛ همه ۶۰ ثانیه = ۱ دقیقه
# برای مپ‌های بزرگ می‌توانی مقدار را بیشتر کنی، مثلاً 10: 180
TIME_LIMITS = {4: 60, 6: 60, 8: 60, 10: 60}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "leaderboard.json")

# مسیر پوشه عکس‌ها
CARDS_DIR = os.path.join(BASE_DIR, "assets", "cards")
if not os.path.exists(CARDS_DIR):
    CARDS_DIR = os.path.join(BASE_DIR, "cards")

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")

# ۱۴ شکل × ۸ رنگ = ۱۱۲ آیکون یکتا
ICON_COLORS = [CYAN, PURPLE, GOLD, GREEN, RED, PINK, BLUE, ORANGE]
SHAPE_COUNT = 14

RAW_IMAGES = {}
SCALED_CACHE = {}
_FILES_CACHE = None


# ---------- سیستم بارگذاری و تولید آیکون‌ها ----------
def list_card_files():
    """لیست همه عکس‌های داخل پوشه کارت‌ها (با هر اسمی)."""
    global _FILES_CACHE
    if _FILES_CACHE is None:
        files = []
        if os.path.isdir(CARDS_DIR):
            for name in sorted(os.listdir(CARDS_DIR)):
                if name.lower().endswith(IMAGE_EXTS):
                    files.append(os.path.join(CARDS_DIR, name))
        _FILES_CACHE = files
    return _FILES_CACHE


def poly(cx, cy, r, sides, rotation=-math.pi / 2):
    return [
        (cx + r * math.cos(rotation + i * 2 * math.pi / sides),
         cy + r * math.sin(rotation + i * 2 * math.pi / sides))
        for i in range(sides)
    ]


def draw_shape(s, shape, col, cx, cy, r, w):
    """رسم یک شکل روی سطح s. w ضخامت خطوط است."""
    if shape == 0:  # حلقه با نقطه مرکزی
        pygame.draw.circle(s, col, (cx, cy), r, width=w)
        pygame.draw.circle(s, col, (cx, cy), max(2, r // 3))

    elif shape == 1:  # الماس
        pts = [(cx, cy - r), (cx + int(r * 0.75), cy), (cx, cy + r), (cx - int(r * 0.75), cy)]
        pygame.draw.polygon(s, col, pts, width=w)
        pygame.draw.polygon(s, col, [(cx, cy - r // 3), (cx + r // 4, cy),
                                     (cx, cy + r // 3), (cx - r // 4, cy)])

    elif shape == 2:  # ستاره پر
        pts = []
        for i in range(10):
            a = i * math.pi / 5 - math.pi / 2
            rr = r * 1.1 if i % 2 == 0 else r * 0.45
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        pygame.draw.polygon(s, col, pts)

    elif shape == 3:  # مربع گرد با مربع داخلی
        rect = pygame.Rect(0, 0, int(r * 1.7), int(r * 1.7))
        rect.center = (cx, cy)
        pygame.draw.rect(s, col, rect, width=w, border_radius=10)
        inner = pygame.Rect(0, 0, int(r * 0.7), int(r * 0.7))
        inner.center = (cx, cy)
        pygame.draw.rect(s, col, inner, border_radius=4)

    elif shape == 4:  # مثلث
        pts = poly(cx, cy + r // 8, r * 1.1, 3)
        pygame.draw.polygon(s, col, pts, width=w)
        pygame.draw.circle(s, col, (cx, cy + r // 5), max(2, r // 6))

    elif shape == 5:  # بعلاوه
        t = max(w + 2, r // 3)
        pygame.draw.rect(s, col, (cx - r, cy - t // 2, 2 * r, t), border_radius=t // 2)
        pygame.draw.rect(s, col, (cx - t // 2, cy - r, t, 2 * r), border_radius=t // 2)

    elif shape == 6:  # شش‌ضلعی
        pygame.draw.polygon(s, col, poly(cx, cy, r * 1.1, 6, rotation=0), width=w)
        pygame.draw.polygon(s, col, poly(cx, cy, r * 0.45, 6, rotation=0))

    elif shape == 7:  # قلب
        pts = []
        for i in range(80):
            t = i * 2 * math.pi / 80
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            pts.append((cx + x * r / 15.5, cy - y * r / 15.5 + 2))
        pygame.draw.polygon(s, col, pts)

    elif shape == 8:  # هلال
        pygame.draw.circle(s, col, (cx, cy), int(r * 1.05))
        pygame.draw.circle(s, (0, 0, 0, 0), (cx + int(r * 0.5), cy - int(r * 0.2)), int(r * 0.9))

    elif shape == 9:  # رعد و برق
        pts = [
            (cx + r * 0.25, cy - r * 1.15),
            (cx - r * 0.65, cy + r * 0.1),
            (cx - r * 0.05, cy + r * 0.1),
            (cx - r * 0.3, cy + r * 1.15),
            (cx + r * 0.7, cy - r * 0.3),
            (cx + r * 0.05, cy - r * 0.3),
        ]
        pygame.draw.polygon(s, col, pts)

    elif shape == 10:  # هدف
        pygame.draw.circle(s, col, (cx, cy), int(r * 1.05), width=w)
        pygame.draw.circle(s, col, (cx, cy), int(r * 0.6), width=w)
        pygame.draw.circle(s, col, (cx, cy), max(2, int(r * 0.2)))

    elif shape == 11:  # جرقه چهارپر
        pts = []
        for i in range(8):
            a = i * math.pi / 4 - math.pi / 2
            rr = r * 1.2 if i % 2 == 0 else r * 0.3
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        pygame.draw.polygon(s, col, pts)

    elif shape == 12:  # پنج‌ضلعی
        pygame.draw.polygon(s, col, poly(cx, cy + 2, r * 1.1, 5), width=w)
        pygame.draw.polygon(s, col, poly(cx, cy + 2, r * 0.4, 5))

    else:  # فلش دوتایی
        for dy in (-r // 3, r // 2):
            pts = [(cx - r * 0.8, cy + dy + r * 0.4), (cx, cy + dy - r * 0.4),
                   (cx + r * 0.8, cy + dy + r * 0.4)]
            pygame.draw.lines(s, col, False, pts, w + 1)


def generate_icon(shape, color_idx, size=120):
    """آیکون نئونی با درخشش؛ بدون هیچ شماره یا متنی."""
    col = ICON_COLORS[color_idx % len(ICON_COLORS)]
    cx, cy = size // 2, size // 2
    r = int(size * 0.32)

    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    draw_shape(glow, shape, (*col, 110), cx, cy, r, 12)
    small = pygame.transform.smoothscale(glow, (size // 4, size // 4))
    glow = pygame.transform.smoothscale(small, (size, size))

    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.blit(glow, (0, 0))
    surf.blit(glow, (0, 0))

    crisp = pygame.Surface((size, size), pygame.SRCALPHA)
    draw_shape(crisp, shape, col, cx, cy, r, 6)
    surf.blit(crisp, (0, 0))
    return surf


def load_card_image(card_key):
    """card_key = ('f', i) برای فایل عکس یا ('g', shape, color) برای آیکون تولیدی"""
    if card_key in RAW_IMAGES:
        return RAW_IMAGES[card_key]

    img = None
    if card_key[0] == "f":
        files = list_card_files()
        idx = card_key[1]
        if 1 <= idx <= len(files):
            try:
                img = pygame.image.load(files[idx - 1]).convert_alpha()
            except Exception:
                img = None
        if img is None:
            img = generate_icon(idx % SHAPE_COUNT, idx // SHAPE_COUNT)
    else:
        img = generate_icon(card_key[1], card_key[2])

    RAW_IMAGES[card_key] = img
    return img


def get_scaled_card_image(card_key, target_w, target_h):
    """ریسایز تصویر متناسب با اندازه خانه مپ و کش کردن آن"""
    cache_key = (card_key, target_w, target_h)
    if cache_key in SCALED_CACHE:
        return SCALED_CACHE[cache_key]

    raw = load_card_image(card_key)
    pad_w = max(4, int(target_w * 0.15))
    pad_h = max(4, int(target_h * 0.15))
    fit_w = max(10, target_w - pad_w)
    fit_h = max(10, target_h - pad_h)

    orig_w, orig_h = raw.get_size()
    scale = min(fit_w / orig_w, fit_h / orig_h)
    new_w = max(1, int(orig_w * scale))
    new_h = max(1, int(orig_h * scale))

    scaled = pygame.transform.smoothscale(raw, (new_w, new_h))
    SCALED_CACHE[cache_key] = scaled
    return scaled


def pick_generated_icons(pair_count):
    """انتخاب آیکون‌های یکتا: ابتدا همه شکل‌ها با رنگ‌های متفاوت، بعد دور بعدی با رنگ‌های جدید."""
    shapes = list(range(SHAPE_COUNT))
    offset = random.randrange(len(ICON_COLORS))
    keys = []
    round_no = 0
    while len(keys) < pair_count:
        random.shuffle(shapes)
        for s in shapes:
            keys.append(("g", s, (round_no + s + offset) % len(ICON_COLORS)))
        round_no += 1
    return keys[:pair_count]


# ---------- مدیریت فایل رکوردهای لیدربورد ----------
def load_records():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("leaderboard.json must contain a JSON list.")
    return data


def save_records(records):
    folder = os.path.dirname(DATA_FILE)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=folder,
            prefix="leaderboard_",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name
            json.dump(records, temp_file, ensure_ascii=False, indent=2)
        os.replace(temp_path, DATA_FILE)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def read_leaderboard():
    try:
        return load_records(), None
    except (OSError, json.JSONDecodeError, ValueError) as error:
        return [], str(error)


def record_grid(record):
    value = record.get("grid", record.get("grid_size"))
    if isinstance(value, int):
        return f"{value}x{value}"
    if isinstance(value, str):
        return value.lower().replace(" ", "").replace("×", "x")
    return None


def number(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def top_records(records, grid):
    """رکوردهای یک مپ مشخص: اول کمترین زمان، بعد کمترین حرکت."""
    selected = [
        record for record in records
        if isinstance(record, dict) and record_grid(record) == grid
    ]
    selected.sort(
        key=lambda r: (
            number(r.get("time"), float("inf")),
            number(r.get("moves"), float("inf")),
        )
    )
    return selected[:8]


# ---------- توابع ترسیم UI ----------
def text(message, font, color, center=None, topleft=None):
    surface = font.render(str(message), True, color)
    if center is not None:
        rect = surface.get_rect(center=center)
    else:
        rect = surface.get_rect(topleft=topleft)
    SCREEN.blit(surface, rect)


def button(label, rect, mouse_pos, active=False):
    hovered = rect.collidepoint(mouse_pos)
    if active:
        fill = CYAN
        label_color = BG
        border = CYAN
    else:
        fill = PANEL_HOVER if hovered else PANEL
        label_color = WHITE
        border = CYAN if hovered else PURPLE

    pygame.draw.rect(SCREEN, fill, rect, border_radius=12)
    pygame.draw.rect(SCREEN, border, rect, width=2, border_radius=12)
    text(label, FONT, label_color, center=rect.center)


def map_buttons():
    width = 175
    gap = 18
    start_x = (WIDTH - (4 * width + 3 * gap)) // 2
    return {
        size: pygame.Rect(start_x + idx * (width + gap), 390, width, 62)
        for idx, size in enumerate(GRID_SIZES)
    }


def tab_buttons():
    width = 175
    gap = 16
    start_x = (WIDTH - (4 * width + 3 * gap)) // 2
    return {
        size: pygame.Rect(start_x + idx * (width + gap), 178, width, 52)
        for idx, size in enumerate(GRID_SIZES)
    }


MENU_LEADERBOARD_BUTTON = pygame.Rect(387, 510, 250, 56)
BACK_BUTTON = pygame.Rect(42, 728, 185, 48)
GAME_LEADERBOARD_BUTTON = pygame.Rect(795, 728, 187, 48)

WIN_AGAIN_BUTTON = pygame.Rect(245, 515, 160, 55)
WIN_LEADERBOARD_BUTTON = pygame.Rect(432, 515, 160, 55)
WIN_MENU_BUTTON = pygame.Rect(619, 515, 160, 55)


# ---------- بازی و منطق آن ----------
def new_game(size, player_name):
    pair_count = (size * size) // 2

    files = list_card_files()
    if len(files) >= pair_count:
        chosen = random.sample(range(1, len(files) + 1), pair_count)
        keys = [("f", n) for n in chosen]
    else:
        keys = pick_generated_icons(pair_count)

    cards = keys * 2
    random.shuffle(cards)

    return {
        "size": size,
        "name": player_name.strip() or "Player",
        "cards": cards,
        "opened": [],
        "matched": set(),
        "moves": 0,
        "time_limit": TIME_LIMITS.get(size, 60),
        "started_at": pygame.time.get_ticks(),
        "hide_at": None,
        "finished_time": None,   # زمان صرف‌شده تا برد
        "lost": False,
        "score": 0,
        "save_error": None,
    }


def elapsed_seconds(game):
    """زمان سپری‌شده از شروع بازی."""
    if game["finished_time"] is not None:
        return game["finished_time"]
    if game["lost"]:
        return game["time_limit"]
    return (pygame.time.get_ticks() - game["started_at"]) / 1000


def remaining_seconds(game):
    """زمان باقی‌مانده (شمارش معکوس)."""
    return max(0.0, game["time_limit"] - elapsed_seconds(game))


def format_time(seconds):
    seconds = max(0.0, seconds)
    minutes = int(seconds // 60)
    rest = seconds - minutes * 60
    return f"{minutes}:{rest:04.1f}"


def card_rect(size, index):
    gap = 6
    cell_width = (900 - (size - 1) * gap) // size
    cell_height = (500 - (size - 1) * gap) // size

    board_width = size * cell_width + (size - 1) * gap
    x0 = (WIDTH - board_width) // 2
    y0 = 174

    row, col = divmod(index, size)
    return pygame.Rect(
        x0 + col * (cell_width + gap),
        y0 + row * (cell_height + gap),
        cell_width,
        cell_height,
    )


def finish_game(game):
    """بازی با برد تمام شد؛ زمان صرف‌شده و امتیاز ذخیره می‌شود."""
    game["finished_time"] = round(elapsed_seconds(game), 2)
    time_left = game["time_limit"] - game["finished_time"]

    game["score"] = max(
        0,
        int(time_left * 100) + 1000 - game["moves"] * 10,
    )

    record = {
        "name": game["name"],
        "grid": f"{game['size']}x{game['size']}",
        "time": game["finished_time"],   # زمانی که برنده صرف کرده
        "moves": game["moves"],
        "score": game["score"],
    }

    try:
        records = load_records()
        records.append(record)
        save_records(records)
        game["save_error"] = None
    except (OSError, json.JSONDecodeError, ValueError) as error:
        game["save_error"] = str(error)


def flip_card(game, position):
    if game["hide_at"] is not None:
        return False

    clicked = None
    for index in range(len(game["cards"])):
        if card_rect(game["size"], index).collidepoint(position):
            clicked = index
            break

    if clicked is None or clicked in game["matched"] or clicked in game["opened"]:
        return False

    game["opened"].append(clicked)

    if len(game["opened"]) == 2:
        game["moves"] += 1
        first, second = game["opened"]

        if game["cards"][first] == game["cards"][second]:
            game["matched"].update((first, second))
            game["opened"].clear()

            if len(game["matched"]) == len(game["cards"]):
                finish_game(game)
                return True
        else:
            game["hide_at"] = pygame.time.get_ticks() + 850

    return False


# ---------- صفحات رابط کاربری ----------
def draw_menu(player_name, mouse_pos):
    SCREEN.fill(BG)

    text("NEON MEMORY CARDS", BIG_FONT, CYAN, center=(WIDTH // 2, 125))
    text(
        "Match picture pairs before time runs out!",
        FONT,
        MUTED,
        center=(WIDTH // 2, 183),
    )

    text("PLAYER NAME", SMALL_FONT, PURPLE, center=(WIDTH // 2, 258))

    name_rect = pygame.Rect(300, 276, 424, 60)
    pygame.draw.rect(SCREEN, PANEL, name_rect, border_radius=12)
    pygame.draw.rect(SCREEN, CYAN, name_rect, width=2, border_radius=12)
    text(
        player_name or "Type your name...",
        FONT,
        WHITE if player_name else MUTED,
        center=name_rect.center,
    )

    text("CHOOSE YOUR MAP", FONT, WHITE, center=(WIDTH // 2, 365))

    for size, rect in map_buttons().items():
        button(f"{size} x {size}", rect, mouse_pos)

    button("LEADERBOARD", MENU_LEADERBOARD_BUTTON, mouse_pos)
    text(
        "Select map size to begin.",
        SMALL_FONT,
        MUTED,
        center=(WIDTH // 2, 633),
    )


def draw_game(game, mouse_pos):
    SCREEN.fill(BG)

    size = game["size"]
    text(f"{size} x {size}  |  {game['name']}", FONT, CYAN, topleft=(58, 35))

    left = remaining_seconds(game)
    time_color = RED if left <= 10 else WHITE
    text(
        f"Time Left: {format_time(left)}",
        FONT,
        time_color,
        topleft=(58, 92),
    )
    text(f"Moves: {game['moves']}", FONT, WHITE, topleft=(382, 92))
    text(
        f"Pairs: {len(game['matched']) // 2}/{size * size // 2}",
        FONT,
        WHITE,
        topleft=(714, 92),
    )

    # نوار زمان
    bar = pygame.Rect(58, 140, WIDTH - 116, 10)
    pygame.draw.rect(SCREEN, PANEL, bar, border_radius=5)
    ratio = left / game["time_limit"] if game["time_limit"] else 0
    fill_rect = pygame.Rect(bar.x, bar.y, int(bar.width * ratio), bar.height)
    if fill_rect.width > 0:
        pygame.draw.rect(
            SCREEN, RED if left <= 10 else CYAN, fill_rect, border_radius=5
        )

    for index, card_key in enumerate(game["cards"]):
        rect = card_rect(size, index)
        is_matched = index in game["matched"]
        is_open = index in game["opened"]

        if is_matched or is_open:
            fill = PANEL_HOVER if is_open else PANEL
            border = CYAN if is_open else GREEN
            pygame.draw.rect(SCREEN, fill, rect, border_radius=8)
            pygame.draw.rect(SCREEN, border, rect, width=2, border_radius=8)

            img = get_scaled_card_image(card_key, rect.width, rect.height)
            img_rect = img.get_rect(center=rect.center)
            SCREEN.blit(img, img_rect)
        else:
            pygame.draw.rect(SCREEN, PANEL, rect, border_radius=8)
            pygame.draw.rect(SCREEN, PURPLE, rect, width=2, border_radius=8)
            text("?", CARD_FONT, PURPLE, center=rect.center)

    button("BACK TO MENU", BACK_BUTTON, mouse_pos)
    button("LEADERBOARD", GAME_LEADERBOARD_BUTTON, mouse_pos)


def draw_leaderboard(records, error, selected_size, mouse_pos):
    SCREEN.fill(BG)

    text("HALL OF FAME", BIG_FONT, CYAN, center=(WIDTH // 2, 85))
    text(
        "Select a map tab to view its records",
        SMALL_FONT,
        MUTED,
        center=(WIDTH // 2, 135),
    )

    # تب‌ها: هر مپ جدول جدا دارد
    for size, rect in tab_buttons().items():
        button(
            f"{size} x {size}",
            rect,
            mouse_pos,
            active=(size == selected_size),
        )

    headers = [
        ("RANK", 86),
        ("PLAYER", 196),
        ("TIME", 530),
        ("MOVES", 680),
        ("SCORE", 823),
    ]

    for label, x in headers:
        text(label, SMALL_FONT, PURPLE, topleft=(x, 275))

    pygame.draw.line(SCREEN, MUTED, (75, 310), (949, 310), 1)

    grid = f"{selected_size}x{selected_size}"
    visible_records = top_records(records, grid)

    if not visible_records:
        text(
            f"No records yet for {selected_size} x {selected_size}",
            FONT,
            MUTED,
            center=(WIDTH // 2, 395),
        )

    for index, record in enumerate(visible_records):
        y = 325 + index * 42

        if index % 2 == 0:
            pygame.draw.rect(
                SCREEN,
                PANEL,
                pygame.Rect(75, y - 4, 874, 38),
                border_radius=6,
            )

        rank_color = GOLD if index == 0 else WHITE
        player = str(record.get("name", "Player"))[:18]
        seconds = number(record.get("time"))
        moves = int(number(record.get("moves")))
        score = int(number(record.get("score")))

        text(f"#{index + 1}", FONT, rank_color, topleft=(86, y))
        text(player, FONT, WHITE, topleft=(196, y))
        text(format_time(seconds), FONT, WHITE, topleft=(530, y))
        text(moves, FONT, WHITE, topleft=(680, y))
        text(score, FONT, CYAN, topleft=(823, y))

    if error:
        text(
            f"Could not read leaderboard: {error[:65]}",
            SMALL_FONT,
            RED,
            center=(WIDTH // 2, 706),
        )

    button("BACK", BACK_BUTTON, mouse_pos)


def draw_win(game, mouse_pos):
    draw_game(game, mouse_pos)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 7, 18, 190))
    SCREEN.blit(overlay, (0, 0))

    panel = pygame.Rect(180, 210, 664, 390)
    pygame.draw.rect(SCREEN, PANEL, panel, border_radius=20)
    pygame.draw.rect(SCREEN, CYAN, panel, width=3, border_radius=20)

    text("YOU WON!", BIG_FONT, GOLD, center=(WIDTH // 2, 280))
    text(
        f"Map: {game['size']} x {game['size']}     Your Time: {format_time(game['finished_time'])}",
        FONT,
        WHITE,
        center=(WIDTH // 2, 355),
    )
    text(
        f"Moves: {game['moves']}     Score: {game['score']}",
        FONT,
        CYAN,
        center=(WIDTH // 2, 402),
    )

    if game["save_error"]:
        text(
            f"Record not saved: {game['save_error'][:48]}",
            SMALL_FONT,
            RED,
            center=(WIDTH // 2, 461),
        )
    else:
        text("Record saved to leaderboard!", SMALL_FONT, GREEN, center=(WIDTH // 2, 461))

    button("PLAY AGAIN", WIN_AGAIN_BUTTON, mouse_pos)
    button("LEADERBOARD", WIN_LEADERBOARD_BUTTON, mouse_pos)
    button("MENU", WIN_MENU_BUTTON, mouse_pos)


def draw_lose(game, mouse_pos):
    draw_game(game, mouse_pos)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 7, 18, 190))
    SCREEN.blit(overlay, (0, 0))

    panel = pygame.Rect(180, 210, 664, 390)
    pygame.draw.rect(SCREEN, PANEL, panel, border_radius=20)
    pygame.draw.rect(SCREEN, RED, panel, width=3, border_radius=20)

    text("TIME'S UP!", BIG_FONT, RED, center=(WIDTH // 2, 280))
    text(
        f"Map: {game['size']} x {game['size']}",
        FONT,
        WHITE,
        center=(WIDTH // 2, 355),
    )
    text(
        f"Pairs found: {len(game['matched']) // 2}/{game['size'] * game['size'] // 2}"
        f"     Moves: {game['moves']}",
        FONT,
        CYAN,
        center=(WIDTH // 2, 402),
    )
    text("No record saved.", SMALL_FONT, MUTED, center=(WIDTH // 2, 461))

    button("TRY AGAIN", WIN_AGAIN_BUTTON, mouse_pos)
    button("LEADERBOARD", WIN_LEADERBOARD_BUTTON, mouse_pos)
    button("MENU", WIN_MENU_BUTTON, mouse_pos)


# ---------- حلقه اصلی برنامه ----------
def main():
    state = "menu"
    player_name = ""
    game = None

    records, leaderboard_error = read_leaderboard()
    selected_size = 4

    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        if state == "game":
            if game["hide_at"] is not None:
                if pygame.time.get_ticks() >= game["hide_at"]:
                    game["opened"].clear()
                    game["hide_at"] = None

            # پایان زمان => باخت
            if remaining_seconds(game) <= 0:
                game["lost"] = True
                game["opened"].clear()
                game["hide_at"] = None
                state = "lost"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.key not in (pygame.K_RETURN, pygame.K_ESCAPE):
                        if event.unicode.isprintable() and len(player_name) < 16:
                            player_name += event.unicode

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for size, rect in map_buttons().items():
                        if rect.collidepoint(event.pos):
                            game = new_game(size, player_name)
                            selected_size = size
                            state = "game"
                            break
                    else:
                        if MENU_LEADERBOARD_BUTTON.collidepoint(event.pos):
                            records, leaderboard_error = read_leaderboard()
                            state = "leaderboard"

            elif state == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "menu"

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if BACK_BUTTON.collidepoint(event.pos):
                        state = "menu"
                    elif GAME_LEADERBOARD_BUTTON.collidepoint(event.pos):
                        selected_size = game["size"]
                        records, leaderboard_error = read_leaderboard()
                        state = "leaderboard"
                    elif flip_card(game, event.pos):
                        state = "won"

            elif state in ("won", "lost"):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "menu"

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if WIN_AGAIN_BUTTON.collidepoint(event.pos):
                        game = new_game(game["size"], game["name"])
                        state = "game"
                    elif WIN_LEADERBOARD_BUTTON.collidepoint(event.pos):
                        selected_size = game["size"]
                        records, leaderboard_error = read_leaderboard()
                        state = "leaderboard"
                    elif WIN_MENU_BUTTON.collidepoint(event.pos):
                        state = "menu"

            elif state == "leaderboard":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "menu"

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if BACK_BUTTON.collidepoint(event.pos):
                        state = "menu"
                    else:
                        for size, rect in tab_buttons().items():
                            if rect.collidepoint(event.pos):
                                selected_size = size
                                break

        if not running:
            break

        if state == "menu":
            draw_menu(player_name, mouse_pos)
        elif state == "game":
            draw_game(game, mouse_pos)
        elif state == "won":
            draw_win(game, mouse_pos)
        elif state == "lost":
            draw_lose(game, mouse_pos)
        elif state == "leaderboard":
            draw_leaderboard(
                records,
                leaderboard_error,
                selected_size,
                mouse_pos,
            )

        pygame.display.flip()
        CLOCK.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()