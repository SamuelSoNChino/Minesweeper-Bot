# Minesweeper Bot

The Minesweeper Bot is a Python program that automates the gameplay on the [Minesweeper Online](https://minesweeper.online/) website. By utilizing visual detection and automation, the bot analyzes the game board and simulates mouse interactions to solve the puzzle.

The app shares most of the logic with https://github.com/SamuelSoNChino/Minesweeper-Hint/

> This was one of my earlier projects, so there are parts I would refactor. I might look into it in the future.

### Features

- **Automated Gameplay**: The bot identifies safe tiles and mines and interacts with the board accordingly.

- **Visual Detection**: Uses color filters and edge recognition to detect the game board and grid tiles.

- **Adaptable Algorithm**: Handles common Minesweeper logic to solve the board, though it cannot guarantee a win due to unavoidable random guesses.

## How It Works

1. **Field Detection**: The bot identifies the game field using color-based masking and edge detection.

2. **Tile Grid Mapping**: It maps the positions of individual tiles on the grid.

3. **Tile Analysis**: Each tile is evaluated to determine whether it is safe to click, a mine, or unknown.

4. **Mouse Interaction**: Using the `pyautogui` library, the bot clicks safe tiles and flags suspected mines.

5. **Re-evaluation**: After every action, the bot updates its knowledge of the board and continues until the game is won or a random guess fails.

## Setup & Usage
Prerequisites

- Install the required Python libraries:

        pip install pyautogui opencv-python-headless numpy

- A desktop environment with Minesweeper running in a visible browser window.

### Steps to Run

1. Open Minesweeper Online and start a new game.

2. Run the script in your Python environment.

3. The bot will take control of your mouse and start playing automatically.

>**Tip**: Use a delay (`DELAY` constant) of at least 1 second for smoother performance and fewer accidental clicks.

## Warnings

1. **Random Guessing**:

    - Some Minesweeper scenarios require random guesses. The bot cannot avoid losing in these cases. To make the process amusing to watch, keep the `DELAY` constant set to at least 1 second.

2. **IP Ban Risk**:
    - Using this bot with very small delays might trigger anti-bot detection on the Minesweeper Online website. If detected, your IP address could be permanently banned from playing.

## Troubleshooting

If the bot prints "Something is wrong," try the following:

1. **Adjust Zoom and Brightness**:
    
    - Experiment with browser zoom levels or screen brightness to ensure accurate detection.

2. **Change the `MAIN_COLOR`**:
    - If detection issues persist, update the `MAIN_COLOR` constant to match the primary shade of gray in your minefield.
        - Use [Image Color Picker](https://imagecolorpicker.com/) to find the RGB code of the gray area.
        - Convert the RGB value into a single grayscale value for `MAIN_COLOR`.

## Program Explanation

The bot relies on the following steps:

1. **Visual Detection**:

    - Color filters and edge detection isolate the minefield from the screenshot.
    
    - The `task2` function identifies the field’s bounding box.
    
    - The `task1` function maps the grid positions of all tiles.

2. **Tile Classification**:
    - Each tile is analyzed using the `detect_tile` function, which identifies numbers, mines, and empty spaces based on pixel colors.

3. **Logic Processing**:
    - A simple algorithm evaluates neighbors and assigns safety or danger scores to unknown tiles.

4. **Mouse Automation**:
    - The bot interacts with tiles based on the evaluation:

        - Clicks safe tiles.
        
        - Flags suspected mines.
        
        - Ignores tiles marked as unknown.

5. **Reiteration**:
    - The process repeats until the game is solved or fails due to a random guess.

## Customization

- **Adjust `DELAY`**:

    Modify the DELAY constant to control the speed of mouse clicks.

- **Change `MAIN_COLOR`**:

    Update the primary gray shade for better field detection on custom or altered game boards.

## Disclaimer

This bot is intended for educational purposes. Use at your own risk, as automated interactions may violate the website's terms of service.
