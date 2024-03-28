# Minesweeper-Bot
The bit is based on visual detection of the minesweeper field at https://minesweeper.online/. To use it, start the program and start a new game. The
program will take control over your mouse and click the tiles until the game is won. 

## WARNING 1: 

Since in minesweeper you can enounter scenarios where random choice is necessary, the bot doesn't always win the game. The program can acually behave quite funnily in this scenarios, so I recommend keeping the DELAY constant at least 1 sec long, to avoid accidental residual clicks when changing
widnows.

## WARNING 2: 

Use this bot at your own risk. The website can actually detect when you are using it with very small delays. When this happens, your IP address will get
permanently banned from playing.

## TROUUBLESHOOTING:

If the program prints that something is wrong, try to play with different zoom and birghtness settings. If even this doesn't help, you can try to replace the MAIN_COLOR constant with the main shade of grey your minefield has (the biggest uniform areas of the frame are of this color). You can find it out by pasting screenshot into https://imagecolorpicker.com/, and you will get the RGB code of that color, then try to play with different zoom values.


## PROGRAM EXPLAINED:

The program is based on visual recoginition of the field, its grid, tiles using color filters and edge recognition. Then a simple algorithm assigns values
to each tile that determine whether to click or put a flag.