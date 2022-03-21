# Chess

* Tiled
* Pygame
* Aseprite
* vim & neovim

![screenshot.png]

## To-do list

* Add an AI for 0 and 1 player mode

* Add an openings book to the AI

* Add game music

## Bugs

* [FIXED] 2021-02-30: timer doesn't stop in checkmate (black lose), message of you're in check doesn't show (at least when white is in check)

* 2021-02-13: game crashes in 0-player mode, this printed out after I believe white was checkmated by black...
'''
Traceback (most recent call last):
  File "game.pyw", line 784, in <module>
    main()
  File "game.pyw", line 775, in main
    game.update()
  File "game.pyw", line 605, in update
    self.update_game_wait()
  File "game.pyw", line 431, in update_game_wait
    self.update_game_wait_ai()
  File "game.pyw", line 395, in update_game_wait_ai
    row, col, to_row, to_col = self.ai_thread.result
TypeError: cannot unpack non-iterable NoneType object
'''

## Useful AI links

* https://github.com/lhartikk/simple-chess-ai
* https://www.chessprogramming.org/Simplified_Evaluation_Function