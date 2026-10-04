import pygame
import time

# ============================================================
# SMARTMAP
# AI MAP COLORING GAME
# CSP + BACKTRACKING
# ============================================================

pygame.init()

# ============================================================
# WINDOW
# ============================================================

WIDTH = 1200
HEIGHT = 760

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SMARTMAP - AI Map Coloring Game")

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

WHITE = (255, 255, 255)
BLACK = (25, 25, 30)

BACKGROUND = (242, 245, 250)
PANEL = (255, 255, 255)

PURPLE = (108, 76, 170)
PURPLE_DARK = (78, 52, 130)

RED = (231, 76, 60)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
YELLOW = (241, 196, 15)

GRAY = (210, 214, 220)
DARK_GRAY = (80, 84, 90)

LIGHT_PURPLE = (238, 232, 250)
LIGHT_BLUE = (232, 242, 252)
LIGHT_GREEN = (231, 248, 238)
LIGHT_RED = (252, 235, 233)

ORANGE = (230, 126, 34)

# ============================================================
# FONTS
# ============================================================

title_font = pygame.font.SysFont("arial", 34, bold=True)
heading_font = pygame.font.SysFont("arial", 25, bold=True)
normal_font = pygame.font.SysFont("arial", 19)
small_font = pygame.font.SysFont("arial", 16)
tiny_font = pygame.font.SysFont("arial", 14)

# ============================================================
# MAP
# ============================================================

regions = {
    "A": (330, 180),
    "B": (190, 310),
    "C": (470, 310),
    "D": (190, 460),
    "E": (470, 460),
    "F": (330, 590)
}

# Neighbor relationships
neighbors = {
    "A": ["B", "C"],
    "B": ["A", "C", "D"],
    "C": ["A", "B", "E"],
    "D": ["B", "E", "F"],
    "E": ["C", "D", "F"],
    "F": ["D", "E"]
}

# ============================================================
# COLORS AVAILABLE
# ============================================================

color_list = [
    ("RED", RED),
    ("GREEN", GREEN),
    ("BLUE", BLUE),
    ("YELLOW", YELLOW)
]

# ============================================================
# GAME VARIABLES
# ============================================================

player_assignment = {}

selected_region = None

score = 0
mistakes = 0

game_started = False
game_over = False

start_time = 0
time_limit = 120

message = "Select a region and choose a color."

ai_solution = {}

ai_status = "AI READY"

hint_text = "Select a region to receive an AI hint."

show_ai_explanation = False

# ============================================================
# BUTTONS
# ============================================================

start_button = pygame.Rect(430, 420, 260, 65)

ai_button = pygame.Rect(925, 190, 220, 52)

hint_button = pygame.Rect(925, 255, 220, 52)

explain_button = pygame.Rect(925, 320, 220, 52)

reset_button = pygame.Rect(925, 385, 220, 52)

home_button = pygame.Rect(925, 450, 220, 52)

again_button = pygame.Rect(455, 450, 260, 65)

# Bottom color buttons
red_button = pygame.Rect(40, 675, 125, 50)
green_button = pygame.Rect(180, 675, 125, 50)
blue_button = pygame.Rect(320, 675, 125, 50)
yellow_button = pygame.Rect(460, 675, 125, 50)

color_buttons = [
    red_button,
    green_button,
    blue_button,
    yellow_button
]

# ============================================================
# RESET GAME
# ============================================================

def reset_game():

    global player_assignment
    global selected_region
    global score
    global mistakes
    global game_started
    global game_over
    global start_time
    global message
    global ai_solution
    global ai_status
    global hint_text
    global show_ai_explanation

    player_assignment = {}

    selected_region = None

    score = 0

    mistakes = 0

    game_started = True

    game_over = False

    start_time = time.time()

    message = "Select a region and choose a color."

    ai_solution = {}

    ai_status = "AI READY"

    hint_text = "Select a region to receive an AI hint."

    show_ai_explanation = False


# ============================================================
# GET REGION
# ============================================================

def get_region_at_position(pos):

    x, y = pos

    for region, (rx, ry) in regions.items():

        distance = ((x - rx) ** 2 + (y - ry) ** 2) ** 0.5

        if distance <= 52:

            return region

    return None


# ============================================================
# CSP CONSTRAINT CHECK
# ============================================================

def is_safe(region, color, assignment):

    for neighbor in neighbors[region]:

        if neighbor in assignment:

            if assignment[neighbor] == color:

                return False

    return True


# ============================================================
# AI BACKTRACKING
# ============================================================

def solve_map(assignment):

    # If every region has a color,
    # solution is complete.
    if len(assignment) == len(regions):

        return assignment.copy()

    # Find an unassigned region
    unassigned = None

    for region in regions:

        if region not in assignment:

            unassigned = region

            break

    # Try every available color
    for color_name, color_value in color_list:

        if is_safe(
            unassigned,
            color_value,
            assignment
        ):

            # Assign
            assignment[unassigned] = color_value

            # Continue recursively
            result = solve_map(assignment)

            if result is not None:

                return result

            # BACKTRACK
            del assignment[unassigned]

    return None


# ============================================================
# AI SOLVE
# ============================================================

def run_ai_solver():

    global ai_solution
    global player_assignment
    global score
    global message
    global ai_status
    global hint_text

    ai_solution = solve_map({})

    if ai_solution is not None:

        player_assignment = ai_solution.copy()

        score += 50

        ai_status = "AI SOLUTION FOUND"

        message = "AI successfully solved the map!"

        hint_text = "All constraints satisfied."

        check_game_complete()

    else:

        ai_status = "NO SOLUTION"

        message = "AI could not find a valid solution."


# ============================================================
# AI HINT
# ============================================================

def give_hint():

    global hint_text
    global ai_status
    global score

    if selected_region is None:

        hint_text = "First select a region on the map."

        return

    solution = solve_map({})

    if solution is None:

        hint_text = "No valid solution found."

        return

    correct_color = solution[selected_region]

    color_name = "UNKNOWN"

    for name, value in color_list:

        if value == correct_color:

            color_name = name

            break

    hint_text = (
        f"Hint: Region {selected_region} "
        f"can safely use {color_name}."
    )

    ai_status = "HINT GENERATED"

    score = max(0, score - 2)


# ============================================================
# CHECK GAME COMPLETE
# ============================================================

def check_game_complete():

    global game_over
    global score
    global message
    global ai_status

    if len(player_assignment) == len(regions):

        game_over = True

        score += 100

        ai_status = "GAME COMPLETED"

        message = "Excellent! All regions are correctly colored."


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(text, font, color, x, y):

    surface = font.render(
        text,
        True,
        color
    )

    screen.blit(
        surface,
        (x, y)
    )


# ============================================================
# DRAW CENTERED TEXT
# ============================================================

def draw_centered(text, font, color, rect):

    surface = font.render(
        text,
        True,
        color
    )

    text_rect = surface.get_rect(
        center=rect.center
    )

    screen.blit(
        surface,
        text_rect
    )


# ============================================================
# BUTTON
# ============================================================

def draw_button(rect, text, color):

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=10
    )

    draw_centered(
        text,
        normal_font,
        WHITE,
        rect
    )


# ============================================================
# PANEL
# ============================================================

def draw_panel(rect):

    pygame.draw.rect(
        screen,
        PANEL,
        rect,
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        GRAY,
        rect,
        2,
        border_radius=15
    )


# ============================================================
# MAP
# ============================================================

def draw_map():

    # --------------------------------------------------------
    # Draw connections
    # --------------------------------------------------------

    for region in neighbors:

        x1, y1 = regions[region]

        for neighbor in neighbors[region]:

            x2, y2 = regions[neighbor]

            if region < neighbor:

                pygame.draw.line(
                    screen,
                    GRAY,
                    (x1, y1),
                    (x2, y2),
                    5
                )

    # --------------------------------------------------------
    # Draw regions
    # --------------------------------------------------------

    for region, (x, y) in regions.items():

        if region in player_assignment:

            region_color = player_assignment[region]

        else:

            region_color = WHITE

        pygame.draw.circle(
            screen,
            region_color,
            (x, y),
            52
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (x, y),
            52,
            3
        )

        draw_centered(
            region,
            heading_font,
            BLACK,
            pygame.Rect(
                x - 30,
                y - 30,
                60,
                60
            )
        )

    # --------------------------------------------------------
    # Selected region
    # --------------------------------------------------------

    if selected_region is not None:

        x, y = regions[selected_region]

        pygame.draw.circle(
            screen,
            PURPLE,
            (x, y),
            61,
            4
        )


# ============================================================
# HOME / START
# ============================================================

def draw_home():

    screen.fill(BACKGROUND)

    # Main card
    card = pygame.Rect(
        180,
        80,
        840,
        560
    )

    draw_panel(card)

    draw_text(
        "SMARTMAP",
        title_font,
        PURPLE,
        455,
        135
    )

    draw_text(
        "AI Map Coloring Game",
        heading_font,
        DARK_GRAY,
        405,
        190
    )

    draw_text(
        "A Constraint Satisfaction Problem",
        normal_font,
        DARK_GRAY,
        410,
        250
    )

    draw_text(
        "powered by Backtracking AI",
        normal_font,
        DARK_GRAY,
        450,
        285
    )

    # Features
    features = [
        "✓ Interactive map coloring",
        "✓ AI Solver",
        "✓ CSP constraint checking",
        "✓ Backtracking algorithm",
        "✓ AI hints",
        "✓ Score and timer"
    ]

    y = 340

    for feature in features:

        draw_text(
            feature,
            normal_font,
            DARK_GRAY,
            400,
            y
        )

        y += 30

    draw_button(
        start_button,
        "START SMARTMAP",
        PURPLE
    )

    draw_text(
        "One application • One game • AI integrated",
        small_font,
        DARK_GRAY,
        430,
        610
    )


# ============================================================
# GAME HEADER
# ============================================================

def draw_header():

    pygame.draw.rect(
        screen,
        PURPLE_DARK,
        (0, 0, WIDTH, 90)
    )

    draw_text(
        "SMARTMAP",
        title_font,
        WHITE,
        30,
        25
    )

    draw_text(
        "AI MAP COLORING GAME",
        small_font,
        WHITE,
        235,
        38
    )

    # Score
    draw_text(
        f"SCORE  {score}",
        normal_font,
        WHITE,
        640,
        32
    )

    # Mistakes
    draw_text(
        f"MISTAKES  {mistakes}",
        normal_font,
        WHITE,
        790,
        32
    )

    # Timer
    elapsed = int(
        time.time() - start_time
    )

    remaining = max(
        0,
        time_limit - elapsed
    )

    minutes = remaining // 60
    seconds = remaining % 60

    draw_text(
        f"{minutes:02d}:{seconds:02d}",
        normal_font,
        WHITE,
        1050,
        32
    )


# ============================================================
# AI PANEL
# ============================================================

def draw_ai_panel():

    panel_rect = pygame.Rect(
        760,
        115,
        405,
        525
    )

    draw_panel(panel_rect)

    draw_text(
        "AI CONTROL CENTER",
        heading_font,
        PURPLE,
        850,
        140
    )

    # Status box
    status_color = LIGHT_GREEN

    if "NO" in ai_status:

        status_color = LIGHT_RED

    status_rect = pygame.Rect(
        805,
        180,
        315,
        40
    )

    pygame.draw.rect(
        screen,
        status_color,
        status_rect,
        border_radius=8
    )

    draw_centered(
        ai_status,
        small_font,
        BLACK,
        status_rect
    )

    # AI buttons
    draw_button(
        ai_button,
        "🤖  AI SOLVE",
        PURPLE
    )

    draw_button(
        hint_button,
        "💡  AI HINT",
        BLUE
    )

    draw_button(
        explain_button,
        "🧠  AI EXPLANATION",
        ORANGE
    )

    # Hint
    draw_text(
        "AI HINT",
        small_font,
        BLUE,
        805,
        475
    )

    # Wrap hint text manually
    hint_line = hint_text

    if len(hint_line) > 42:

        first = hint_line[:42]
        second = hint_line[42:]

        draw_text(
            first,
            tiny_font,
            DARK_GRAY,
            805,
            500
        )

        draw_text(
            second,
            tiny_font,
            DARK_GRAY,
            805,
            520
        )

    else:

        draw_text(
            hint_line,
            tiny_font,
            DARK_GRAY,
            805,
            500
        )

    # AI explanation
    draw_text(
        "AI METHOD",
        small_font,
        PURPLE,
        805,
        555
    )

    draw_text(
        "CSP + Backtracking",
        normal_font,
        BLACK,
        805,
        580
    )

    draw_text(
        "Variables: A - F",
        tiny_font,
        DARK_GRAY,
        805,
        610
    )

    draw_text(
        "Domain: 4 colors",
        tiny_font,
        DARK_GRAY,
        950,
        610
    )


# ============================================================
# BOTTOM CONTROLS
# ============================================================

def draw_bottom_controls():

    draw_text(
        "CHOOSE COLOR",
        small_font,
        DARK_GRAY,
        40,
        650
    )

    draw_button(
        red_button,
        "RED",
        RED
    )

    draw_button(
        green_button,
        "GREEN",
        GREEN
    )

    draw_button(
        blue_button,
        "BLUE",
        BLUE
    )

    draw_button(
        yellow_button,
        "YELLOW",
        YELLOW
    )

    draw_button(
        reset_button,
        "RESET GAME",
        DARK_GRAY
    )

    draw_button(
        home_button,
        "HOME",
        PURPLE_DARK
    )


# ============================================================
# GAME SCREEN
# ============================================================

def draw_game():

    screen.fill(BACKGROUND)

    draw_header()

    # Left map panel
    map_panel = pygame.Rect(
        25,
        115,
        700,
        525
    )

    draw_panel(map_panel)

    draw_text(
        "MAP COLORING AREA",
        heading_font,
        PURPLE,
        250,
        130
    )

    draw_map()

    # Instruction
    draw_text(
        message,
        small_font,
        DARK_GRAY,
        160,
        615
    )

    draw_ai_panel()

    draw_bottom_controls()


# ============================================================
# GAME OVER
# ============================================================

def draw_game_over():

    screen.fill(BACKGROUND)

    card = pygame.Rect(
        300,
        130,
        600,
        500
    )

    draw_panel(card)

    draw_text(
        "GAME COMPLETE!",
        title_font,
        PURPLE,
        455,
        190
    )

    draw_text(
        f"Final Score: {score}",
        heading_font,
        BLACK,
        485,
        270
    )

    draw_text(
        f"Mistakes: {mistakes}",
        normal_font,
        DARK_GRAY,
        510,
        325
    )

    if ai_solution:

        draw_text(
            "AI Solver was used successfully.",
            normal_font,
            GREEN,
            425,
            370
        )

    draw_text(
        "Your map was successfully colored!",
        normal_font,
        DARK_GRAY,
        440,
        410
    )

    draw_button(
        again_button,
        "PLAY AGAIN",
        PURPLE
    )


# ============================================================
# MAIN LOOP
# ============================================================

running = True

current_screen = "home"

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # ====================================================
        # HOME
        # ====================================================

        if current_screen == "home":

            if event.type == pygame.MOUSEBUTTONDOWN:

                if start_button.collidepoint(event.pos):

                    reset_game()

                    current_screen = "game"

        # ====================================================
        # GAME
        # ====================================================

        elif current_screen == "game":

            if not game_over:

                if event.type == pygame.MOUSEBUTTONDOWN:

                    mouse_pos = event.pos

                    # ----------------------------------------
                    # Region selection
                    # ----------------------------------------

                    clicked_region = get_region_at_position(
                        mouse_pos
                    )

                    if clicked_region is not None:

                        selected_region = clicked_region

                        message = (
                            f"Region {selected_region} selected. "
                            "Choose a color."
                        )

                    # ----------------------------------------
                    # Color buttons
                    # ----------------------------------------

                    if selected_region is not None:

                        for i, button in enumerate(
                            color_buttons
                        ):

                            if button.collidepoint(mouse_pos):

                                color_name, color_value = (
                                    color_list[i]
                                )

                                if is_safe(
                                    selected_region,
                                    color_value,
                                    player_assignment
                                ):

                                    player_assignment[
                                        selected_region
                                    ] = color_value

                                    score += 10

                                    message = (
                                        f"Region "
                                        f"{selected_region} "
                                        f"colored "
                                        f"{color_name}."
                                    )

                                    selected_region = None

                                    check_game_complete()

                                else:

                                    mistakes += 1

                                    score = max(
                                        0,
                                        score - 5
                                    )

                                    message = (
                                        "Invalid move! "
                                        "Neighboring regions "
                                        "cannot have the same color."
                                    )

                    # ----------------------------------------
                    # AI SOLVE
                    # ----------------------------------------

                    if ai_button.collidepoint(
                        mouse_pos
                    ):

                        run_ai_solver()

                    # ----------------------------------------
                    # AI HINT
                    # ----------------------------------------

                    if hint_button.collidepoint(
                        mouse_pos
                    ):

                        give_hint()

                    # ----------------------------------------
                    # AI EXPLANATION
                    # ----------------------------------------

                    if explain_button.collidepoint(
                        mouse_pos
                    ):

                        show_ai_explanation = (
                            not show_ai_explanation
                        )

                        if show_ai_explanation:

                            message = (
                                "AI uses CSP: variables, "
                                "domains and constraints."
                            )

                        else:

                            message = (
                                "AI explanation closed."
                            )

                    # ----------------------------------------
                    # RESET
                    # ----------------------------------------

                    if reset_button.collidepoint(
                        mouse_pos
                    ):

                        reset_game()

                    # ----------------------------------------
                    # HOME
                    # ----------------------------------------

                    if home_button.collidepoint(
                        mouse_pos
                    ):

                        game_started = False

                        current_screen = "home"

            else:

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if again_button.collidepoint(
                        event.pos
                    ):

                        reset_game()

        # ====================================================
        # GAME OVER
        # ====================================================

        if current_screen == "game" and game_over:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if again_button.collidepoint(
                    event.pos
                ):

                    reset_game()

    # ========================================================
    # TIMER
    # ========================================================

    if current_screen == "game" and not game_over:

        elapsed = time.time() - start_time

        if elapsed >= time_limit:

            game_over = True

            message = "Time's up!"

    # ========================================================
    # DRAW
    # ========================================================

    if current_screen == "home":

        draw_home()

    elif current_screen == "game":

        if game_over:

            draw_game_over()

        else:

            draw_game()

    pygame.display.flip()

    clock.tick(60)


pygame.quit()