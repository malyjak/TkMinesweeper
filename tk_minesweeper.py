###############################################################################
#                        Copyright (c) 2022 Jakub Maly                        #
#                            All rights reserved.                             #
###############################################################################

from functools import reduce
from itertools import product, chain
from operator import add
from random import sample
from tkinter import Button, Frame, Menu, Label, StringVar, Tk, PhotoImage, Toplevel
from typing import Set, Tuple


APP_TITLE = "TkMinesweeper"


class Tile(object):
    """Tile definition object.
    """

    def __init__(self):

        self.mine = False
        self.flagged = False
        self.revealed = False


class Model(object):
    """2D model of the gaming board.

    :param width: Width of the gaming board.
    :param height: Height of the gaming board.
    :param: mines: Number of mines.
    """

    def __init__(self,
                 width: int,
                 height: int,
                 mines: int):

        self.width = width
        self.height = height
        self.mines = mines

        # Create grid.
        self.grid = self.create_grid()

        # Add mines to the grid.
        self.add_mines()

    def create_grid(self) -> list[list[Tile]]:
        """Creates a Width X Height grid of Tiles.

        :returns: 2D list of tiles.
        """

        # Width and height needs to be switched due to button placement.
        return [[Tile() for _ in range(self.height)] for _ in range(self.width)]

    def add_mines(self):
        """Adds mines to the grid.
        """

        # TODO: enhance random placement.
        for x, y in sample(list(product(range(self.width),
                                        range(self.height))),
                           self.mines):
            self.grid[x][y].mine = True


class View(Frame):
    """Main view (window / frame) of the program.

    :param master: Tk master object.
    :param width: Width of the gaming board.
    :param height: Height of the gaming board.
    :param: mines: Number of mines.
    """

    def __init__(self,
                 master: Tk,
                 width: int,
                 height: int,
                 mines: int):

        self.master = master
        self.width = width
        self.height = height
        self.mines = mines

        # Initialise a new frame.
        Frame.__init__(self,
                       self.master)
        self.master.title(APP_TITLE)
        self.master.resizable(False,
                              False)
        self.grid()

        # Add top panel.
        self.top_panel = TopPanel(self.master,
                                  self.width,
                                  self.height,
                                  self.mines)

        # Create tile buttons.
        self.default_img = PhotoImage(file='img/default.png')
        self.buttons = self.create_buttons()

    def create_buttons(self) -> list[list[Button]]:
        """Creates tile buttons.

        :returns: 2D list of tile buttons.
        """

        def create_button(x, y) -> Button:
            """Creates a single tile button.

            :returns: Configured tile button.
            """

            button = Button(self.master,
                            image=self.default_img,
                            bd=0)
            button.grid(row=x + 1,
                        column=y + 1)

            return button

        # Width and height needs to be switched due to button placement.
        return [[create_button(y, x) for y in range(self.height)] for x in range(self.width)]

    def display_lose(self):
        """Displays lose emoji.
        """

        self.top_panel.reset_button.configure(image=self.top_panel.img_dict[1])

    def display_win(self):
        """Displays win emoji.
        """

        self.top_panel.reset_button.configure(image=self.top_panel.img_dict[2])


class TopPanel(Frame):
    """Top panel view (window / frame) of the program.

    :param master: Tk master object.
    :param width: Width of the gaming board.
    :param height: Height of the gaming board.
    :param: mines: Number of mines.
    """

    def __init__(self,
                 master: Tk,
                 width: int,
                 height: int,
                 mines: int):

        # Initialise a new frame.
        Frame.__init__(self,
                       master)
        self.grid()

        # Emoji image dictionary.
        self.img_dict = {
            0: PhotoImage(file='img/happy.png'),
            1: PhotoImage(file='img/sad.png'),
            2: PhotoImage(file='img/victory.png')}

        self.reset_button = Button(master,
                                   image=self.img_dict[0],
                                   bd=0)
        self.reset_button.grid(row=0,
                               columnspan=int((width * 10) / 2))

        self.mines_cnt = StringVar()
        self.mines_cnt.set(f'0 / {mines}')
        self.mines_left = Label(textvariable=self.mines_cnt)
        self.mines_left.grid(row=0,
                             columnspan=5)


class Controller(object):
    """Game logic controller.

    :param def_diff_lvl: Default difficulty level.
    """

    def __init__(self,
                 def_diff_lvl: int = 0):

        # Difficulty dictionary. (width, height, mines)
        self.diff_dict = {
            0: (9, 9, 10),
            1: (16, 16, 40),
            2: (30, 16, 99)}

        self.width = self.diff_dict[def_diff_lvl][0]
        self.height = self.diff_dict[def_diff_lvl][1]
        self.mines = self.diff_dict[def_diff_lvl][2]

        # 2D model of the gaming board.
        self.model = Model(self.width,
                           self.height,
                           self.mines)

        # Tk master object.
        self.root = Tk()

        # Main view.
        self.view = View(self.root,
                         self.width,
                         self.height,
                         self.mines)

        # Tile button image dictionary.
        self.img_dict = {
            0: PhotoImage(file='img/mine0.png'),
            1: PhotoImage(file='img/mine1.png'),
            2: PhotoImage(file='img/mine2.png'),
            3: PhotoImage(file='img/mine3.png'),
            4: PhotoImage(file='img/mine4.png'),
            5: PhotoImage(file='img/mine5.png'),
            6: PhotoImage(file='img/mine6.png'),
            7: PhotoImage(file='img/mine7.png'),
            8: PhotoImage(file='img/mine8.png'),
            9: PhotoImage(file='img/flag.png'),
            10: PhotoImage(file='img/mine.png'),
            11: PhotoImage(file='img/mine_step.png'),
            12: PhotoImage(file='img/mine_ok.png'),
            13: PhotoImage(file='img/default.png')}

        # First mine step.
        self.first_mine = True

        # Number of revealed tiles. (used for winning condition)
        self.tiles_revealed = set()
        self.tiles_flagged = set()

        self.game_state = None

        # Bindings
        self.set_bindings()

        # Menu.
        menubar = Menu(self.root)

        filemenu = Menu(menubar,
                        tearoff=0)
        filemenu.add_command(label="Undo (not implemented)",
                             command=self.donothing)
        filemenu.add_separator()
        filemenu.add_command(label="New", command=self.reset)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="Game", menu=filemenu)

        diffmenu = Menu(menubar, tearoff=0)
        diffmenu.add_command(label="Easy", command=lambda: self.change_diff(0))
        diffmenu.add_command(
            label="Medium", command=lambda: self.change_diff(1))
        diffmenu.add_command(label="Hard", command=lambda: self.change_diff(2))
        menubar.add_cascade(label="Difficulty", menu=diffmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.root.config(menu=menubar)

        # Main loop.
        self.root.mainloop()

    def donothing(self):
        # TODO
        pass

    def set_bindings(self):
        """Sets tile buttons bindings.
        """

        def set_binding(index: Tuple[int, int]):
            """Sets tile button bindings.

            :param index: Position tuple.
            """

            x, y = index

            # Right click bind to reveal.
            self.view.buttons[x][y].bind('<Button-1>',
                                         lambda event: self.reveal((x, y)))
            # fnc_helper(self.reveal,
            #            (x, y)))

            # Left click bind to flag.
            self.view.buttons[x][y].bind('<Button-3>',
                                         lambda event: self.flag((x, y)))

        list(map(set_binding,
                 product(range(self.width),
                         range(self.height))))

        # Set up reset button.
        self.view.top_panel.reset_button.bind('<Button>',
                                              lambda event: self.reset())

    def reset(self):
        """Resets the game.
        """

        self.first_mine = True
        self.game_state = None
        self.tiles_revealed = set()
        self.tiles_flagged = set()

        def reset_tile(index: Tuple[int, int]):
            """Resets a tile.

            :param index: Position tuple.
            """

            x, y = index

            self.view.buttons[x][y].configure(image=self.img_dict[13])
            self.model.grid[x][y].mine = False
            self.model.grid[x][y].flagged = False
            self.model.grid[x][y].revealed = False

        list(map(reset_tile,
                 product(range(self.width),
                         range(self.height))))

        self.model.add_mines()
        self.update_cnt()

        self.view.top_panel.reset_button.configure(
            image=self.view.top_panel.img_dict[0])

    def reveal(self,
               index: Tuple[int, int]):
        """Reveals a tile.

        :param index: Position tuple.
        """

        x, y = index

        # Not revealed or flagged.
        if not self.model.grid[x][y].revealed and not self.model.grid[x][y].flagged:
            # It is a mine
            if self.model.grid[x][y].mine and self.game_state != 'win':
                self.reveal_tile(index)
                self.game_state = 'Loss'
                self.lose()

            # Get number of adjacent mines.
            val = self.get_adjacent_mines_cnt(index)
            # It has adjacent mines.
            if val in range(1, 9):
                self.reveal_tile(index)
            # Recursive reveal.
            elif val == 0:
                self.reveal_rec(index)

    def get_adjacent_tiles(self,
                           index: Tuple[int, int],
                           width: int,
                           height: int) -> Set[Tuple[int, int]]:
        """Gets adjacent tiles.

        :param width: Width of the gaming board.
        :param height: Height of the gaming board.
        :returns: The indexes of adjacent tiles.
        """

        x, y = index

        indexes = set()

        def add_index(index_inner: Tuple[int, int]):
            """Adds a valid index to the set of indexes.

            :param index: Position tuple.
            """

            x_new, y_new = index_inner

            # Is valid.
            if 0 <= x_new <= width - 1 and 0 <= y_new <= height - 1:
                indexes.add((x_new, y_new))

        list(map(add_index,
                 product(range(x + 1, x - 2, -1),
                         range(y + 1, y - 2, -1))))

        return indexes

    def get_adjacent_mines_cnt(self,
                               index: Tuple[int, int]) -> int:
        """Gets number of adjacent mines.

        :param index: Position tuple.
        :returns: The number of adjacent mines.
        """

        def is_mine(index) -> bool:
            """Determines if the tile is a mine.

            :param index: Position tuple.
            :returns: Whether the tile is a mine.
            """

            return self.model.grid[index[0]][index[1]].mine

        return reduce(add,
                      map(is_mine,
                          self.get_adjacent_tiles(index,
                                                  self.width,
                                                  self.height)))

    def reveal_tile(self,
                    index: Tuple[int, int]):
        """Reveals a tile.

        :param index: Position tuple.
        """

        x, y = index

        # Not revealed.
        if not self.model.grid[x][y].revealed:
            cells_unrevealed = self.width * \
                self.height - len(self.tiles_revealed) - 1

            # Already flagged tile and end of the game.
            if self.model.grid[x][y].flagged and self.game_state:
                # Mine guess was ok.
                if self.model.grid[x][y].mine:
                    self.view.buttons[x][y].configure(
                        image=self.img_dict[12])
                # Mine guess was wrong.
                else:
                    self.model.grid[x][y].flagged = False
                    self.tiles_flagged.remove(index)
                    self.update_cnt()
                    self.reveal_tile(index)

            # Mine.
            elif self.model.grid[x][y].mine:
                if not self.first_mine:
                    self.view.buttons[x][y].configure(image=self.img_dict[10])
                else:
                    self.view.buttons[x][y].configure(image=self.img_dict[11])
                    self.first_mine = False

                self.model.grid[x][y].revealed = True

            # Normal tile.
            else:
                # Checks if cell is in the board limits
                value = self.get_adjacent_mines_cnt(index)

                self.view.buttons[x][y].configure(image=self.img_dict[value])
                self.tiles_revealed.add(index)
                self.model.grid[x][y].revealed = True

                # Removes cell from flagged list when the cell gets revealed
                if index in self.tiles_flagged:
                    self.tiles_flagged.remove(index)
                    self.update_cnt()

                # Check for win condition
                if cells_unrevealed == self.mines and not self.game_state:
                    self.win()

    def reveal_rec(self,
                   index: Tuple[int, int]):
        """Reveals tiles recursively.

        :param index: Position tuple.
        """

        val = self.get_adjacent_mines_cnt(index)
        for index_inner in self.get_adjacent_tiles(index,
                                                   self.width,
                                                   self.height) | {index}:
            # Not revealed.
            if not self.model.grid[index_inner[0]][index_inner[1]].revealed:
                self.reveal_tile(index_inner)
                val = self.get_adjacent_mines_cnt(index_inner)
                # Continue recursion
                if val == 0:
                    self.reveal_rec(index_inner)

    def win(self):
        """Displays win.
        """

        self.view.display_win()
        self.game_state = 'win'

    def lose(self):
        """Reveals all tiles and displays lose.
        """

        list(map(self.reveal_tile,
                 product(range(self.width),
                         range(self.height))))

        self.view.display_lose()

    def flag(self,
             index: Tuple[int, int]):
        """Flags tile as a possible mine.

        :param index: Position tuple.
        """

        x, y = index

        button = self.view.buttons[x][y]

        # Not revealed.
        if not self.model.grid[x][y].revealed:
            # Not flagged and we can still add a flag.
            if not self.model.grid[x][y].flagged and len(self.tiles_flagged) < self.mines:
                button.configure(image=self.img_dict[9])
                self.tiles_flagged.add(index)
                self.model.grid[x][y].flagged = True
            # Flagged.
            elif self.model.grid[x][y].flagged:
                button.configure(image=self.img_dict[13])
                self.tiles_flagged.remove(index)
                self.model.grid[x][y].flagged = False

            self.update_cnt()

    def update_cnt(self):
        """Updates mine counter.
        """

        self.view.top_panel.mines_cnt.set(
            f'{len(self.tiles_flagged)} / {self.mines}')

    def change_diff(self,
                    diff_lvl: int):
        """Changes game difficulty.

        :param diff_lvl: Difficulty level.
        """

        # self.reset()
        self.width = self.diff_dict[diff_lvl][0]
        self.height = self.diff_dict[diff_lvl][1]
        self.mines = self.diff_dict[diff_lvl][2]

        # Update model.
        self.model.width = self.width
        self.model.height = self.height
        self.model.mines = self.mines
        self.model.grid = self.model.create_grid()
        self.model.add_mines()

        # Update View.
        self.view.width = self.width
        self.view.height = self.height
        self.view.mines = self.mines
        for button in chain.from_iterable(self.view.buttons):
            button.destroy()
        self.view.buttons = self.view.create_buttons()

        # Reset
        self.first_mine = True
        self.game_state = None
        self.tiles_revealed = set()
        self.tiles_flagged = set()
        self.update_cnt()
        self.view.top_panel.reset_button.configure(
            image=self.view.top_panel.img_dict[0])
        self.set_bindings()

    def show_about(self):
        # about_window = Tk()
        # about_window = about_window.title("About")
        # about_text = Label(
        #     about_window, text='Here are the rules...', foreground="black")
        # about_text.grid(row=0, column=0, columnspan=3)
        # about_window.mainloop()
        about_window = Toplevel(self.root)
        about_window.geometry("420x140")
        about_window.title("About")
        about_window.resizable(False,
                               False)
        Label(about_window,
              text="Copyright (C) 2022  Jakub Maly – https://github.com/malyjak\nThis is experimental software; see the source code for copying conditions.\nThere is ABSOLUTELY NO WARRANTY; not even for\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\nSee the documentation for example usage.").place(x=10, y=20)


if __name__ == '__main__':
    Controller()
