import time
import cv2 as cv
from cv2.typing import MatLike
import numpy as np
import pyautogui

Position = tuple[int, int]
Color = tuple[int, int, int]
HintChange = tuple[tuple[int, int], str]
GridCoords = tuple[list[int], list[int]]


WAVE_DELAY = 2
CLICK_DELAY = 1
SCREEN_SCALING = 1.75
MAIN_COLOR: Color = (198, 198, 198)
VICINITY = [(-1, 1), (0, 1), (1, 1),
            (-1, 0), (1, 0),
            (-1, -1), (0, -1), (1, -1)]
TILE_PADDING = 5
GRID_BORDER_PADDING = 12
UNCLICKABLE = "0"
EMPTY = "1"
SAFE = "2"
DANGEROUS = "3"


def find_minefield_bounds(image: MatLike) -> tuple[Position, Position] | None:
    mask = cv.inRange(image, np.array(MAIN_COLOR), np.array(MAIN_COLOR))

    masked_image = cv.bitwise_and(image, image, mask=mask)
    grayscale_image = cv.cvtColor(masked_image, cv.COLOR_BGR2GRAY)

    contours, _ = cv.findContours(
        grayscale_image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return None

    field_contour = max(contours, key=cv.contourArea)
    x, y, w, h = cv.boundingRect(field_contour)
    return (x, y), (x + w, y + h)


def extract_grid_coordinates(image: MatLike,
                             minefield_position: tuple[Position, Position])\
        -> GridCoords | None:
    (x_start, y_start), (x_end, y_end) = minefield_position
    image = image[y_start:y_end, x_start:x_end]

    mask = cv.inRange(image, np.array(MAIN_COLOR), np.array(MAIN_COLOR))
    masked_image = cv.bitwise_and(image, image, mask=mask)
    grayscale_image = cv.cvtColor(masked_image, cv.COLOR_BGR2GRAY)

    contours, _ = cv.findContours(
        grayscale_image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    sorted_contours = sorted(contours, key=cv.contourArea, reverse=True)

    if len(sorted_contours) < 2:
        return None

    second_largest_contour_idx = next(
        i for i, c in enumerate(contours) if
        cv.contourArea(c) == cv.contourArea(sorted_contours[1])
    )

    second_largest_contour = contours[second_largest_contour_idx]

    child_contours = [
        i for i, c in enumerate(contours)
        if i != second_largest_contour_idx and
        cv.pointPolygonTest(second_largest_contour,
                            tuple(map(int, c[0][0])),
                            False) >= 0
    ]

    if not child_contours:
        return None

    child_index = max(
        child_contours, key=lambda i: cv.contourArea(contours[i]))

    max_size = contours[child_index][2][0][0] - \
        contours[child_index][0][0][0]

    tile_size = max_size + TILE_PADDING

    x, y, w, h = cv.boundingRect(contours[second_largest_contour_idx])

    x += GRID_BORDER_PADDING
    y += GRID_BORDER_PADDING
    w -= GRID_BORDER_PADDING
    h -= GRID_BORDER_PADDING

    x_cords = [i + x + x_start for i in range(0, w, tile_size)]
    y_cords = [i + y + y_start for i in range(0, h, tile_size)]

    return x_cords, y_cords


def classify_tile(tile: MatLike) -> str:
    unique_colors = np.unique(tile.reshape(-1, tile.shape[2]), axis=0)
    is_red = is_five = is_black = False

    for unique_color in unique_colors:
        if cv.inRange(unique_color, np.array([210, 0, 0], dtype=np.uint8),
                      np.array([255, 30, 30], dtype=np.uint8)).all():
            return "1"
        if cv.inRange(unique_color, np.array([0, 90, 0], dtype=np.uint8),
                      np.array([30, 140, 30], dtype=np.uint8)).all():
            return "2"
        if cv.inRange(unique_color, np.array([90, 0, 0], dtype=np.uint8),
                      np.array([140, 30, 30], dtype=np.uint8)).all():
            return "4"
        if cv.inRange(unique_color, np.array([50, 50, 0], dtype=np.uint8),
                      np.array([170, 170, 40], dtype=np.uint8)).all():
            return "6"
        if cv.inRange(unique_color, np.array([0, 0, 210], dtype=np.uint8),
                      np.array([30, 30, 255], dtype=np.uint8)).all():
            is_red = True
        elif cv.inRange(unique_color, np.array([0, 0, 50], dtype=np.uint8),
                        np.array([40, 40, 170], dtype=np.uint8)).all():
            is_five = True
        elif cv.inRange(unique_color, np.array([0, 0, 0], dtype=np.uint8),
                        np.array([50, 50, 50], dtype=np.uint8)).all():
            is_black = True
    if is_black and is_red:
        return "F"
    if is_black:
        return "7"
    if is_red:
        return "3"
    if is_five:
        return "5"

    total_pixels = tile.shape[0] * tile.shape[1]

    white_mask = cv.inRange(tile, np.array([230, 230, 230], dtype=np.uint8),
                            np.array([255, 255, 255], dtype=np.uint8))
    if cv.countNonZero(white_mask) / total_pixels > 0.1:
        return "?"

    gray_mask = cv.inRange(tile, np.array([70, 70, 70], dtype=np.uint8),
                           np.array([180, 180, 180], dtype=np.uint8))
    if cv.countNonZero(gray_mask) / total_pixels > 0.5:
        return "8"

    return "0"


def parse_game_state(image: MatLike,
                     field_grid: GridCoords) -> list[str]:
    game_state = []
    x_cords, y_cords = field_grid
    tile_size = y_cords[1] - y_cords[0]
    for y in y_cords[:-1]:
        line = ""
        for x in x_cords[:-1]:
            tile = image[y:y + tile_size, x:x + tile_size]
            tile_symbol = classify_tile(tile)
            line += tile_symbol
        game_state.append(line)
    return game_state


def analyze_tile_neighbors(tile_index: tuple[int, int],
                           minefield: list[str],
                           hint: list[str]) -> list[HintChange]:
    y, x = tile_index
    neighbours = [(y + i, x + j) for i, j in VICINITY if 0 <=
                  y + i < len(minefield) and 0 <= x + j < len(minefield[0])]
    changes: list[HintChange] = []
    num_mines = int(minefield[y][x])

    num_flags = sum(1 for i, j in neighbours if minefield[i][j] == "F")
    num_unknowns = sum(1 for i, j in neighbours if minefield[i][j] == "?")
    num_dangerous = sum(1 for i, j in neighbours if hint[i][j] == DANGEROUS)
    num_safe = sum(1 for i, j in neighbours if hint[i][j] == SAFE)
    num_correct_flags = sum(1 for i, j in neighbours if
                            hint[i][j] == UNCLICKABLE and
                            minefield[i][j] == "F")

    if num_correct_flags == num_mines:
        changes.extend(((i, j), SAFE) for i, j in neighbours if
                       minefield[i][j] == "?" and hint[i][j] != SAFE)
    if num_correct_flags + num_dangerous == num_mines:
        changes.extend(((i, j), SAFE) for i, j in neighbours if
                       minefield[i][j] == "?" and
                       hint[i][j] in {EMPTY, UNCLICKABLE})
    if num_unknowns - num_safe + num_flags == num_mines:
        changes.extend(((i, j), DANGEROUS) for i, j in neighbours if
                       minefield[i][j] == "?" and
                       hint[i][j] in {EMPTY, UNCLICKABLE})
    return changes


def generate_hint_map(minefield: list[str]) -> list[str]:
    hint = [len(row) * UNCLICKABLE for row in minefield]
    non_important = {"?", "0", "F"}
    change_count = 1
    while change_count > 0:
        change_count = 0
        for y, row in enumerate(minefield):
            for x, tile in enumerate(row):
                if tile not in non_important:
                    changes = analyze_tile_neighbors((y, x), minefield, hint)
                    for (i, j), new_label in changes:
                        hint[i] = hint[i][:j] + new_label + hint[i][j + 1:]
                        change_count += 1
                if minefield[y][x] == "?" and hint[y][x] == UNCLICKABLE:
                    hint[y] = hint[y][:x] + EMPTY + hint[y][x + 1:]
    return hint


def apply_clicks(hint: list[str],
                 field_grid: GridCoords,
                 random_click: bool) -> int:
    x_coords, y_coords = field_grid
    tile_size = field_grid[0][1] - field_grid[0][0]
    number_of_clicks = 0

    for y_idx, y in enumerate(y_coords[:-1]):
        for x_idx, x in enumerate(x_coords[:-1]):
            label = hint[y_idx][x_idx]
            if label == UNCLICKABLE or (label == EMPTY and not random_click):
                continue
            print(x + tile_size // 2, y + tile_size // 2)
            if label == EMPTY:
                pyautogui.click((x + tile_size // 2) / SCREEN_SCALING,
                                (y + tile_size // 2) / SCREEN_SCALING)
                random_click = False
            elif label == SAFE:
                pyautogui.click((x + tile_size // 2) / SCREEN_SCALING,
                                (y + tile_size // 2) / SCREEN_SCALING)
            elif label == DANGEROUS:
                pyautogui.click((x + tile_size // 2) / SCREEN_SCALING,
                                (y + tile_size // 2) / SCREEN_SCALING,
                                button="right")
            number_of_clicks += 1
            time.sleep(CLICK_DELAY)
    return number_of_clicks


def main() -> None:
    total_clicks = 0
    tile_count = 1
    number_of_clicks = 1
    while total_clicks != tile_count:
        screenshot = np.array(pyautogui.screenshot())
        screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)

        field = find_minefield_bounds(screenshot)
        if field is None:
            print("Coudn't find the minefield.")
            time.sleep(1)
            continue
        grid = extract_grid_coordinates(screenshot, field)
        if grid is None:
            print("Coudn't extract the grid coordinates.")
            time.sleep(1)
            continue
        game_state = parse_game_state(screenshot, grid)
        hint = generate_hint_map(game_state)
        tile_count = len(hint) * len(hint[0])
        number_of_clicks = apply_clicks(hint, grid, number_of_clicks == 0)
        total_clicks += number_of_clicks
        time.sleep(WAVE_DELAY)


if __name__ == "__main__":
    main()
