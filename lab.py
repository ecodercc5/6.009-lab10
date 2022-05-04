"""6.009 Lab 10: Snek Is You Video Game"""

import doctest
import pprint

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}


# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def apply_delta(position, delta):
    return tuple([c + d for c, d in zip(position, delta)])


def negative(vector):
    return tuple([-1 * i for i in vector])


def is_in_bounds(position, rows, cols):
    r, c = position

    return 0 <= r < rows and 0 <= c < cols


def get_next_position(position, direction):
    delta = direction_vector[direction]
    next_position = apply_delta(position, delta)

    return next_position


def get_prev_position(position, direction):
    delta = negative(direction_vector[direction])
    prev_position = apply_delta(position, delta)

    return prev_position


class GameRules:
    def __init__(self, board):
        self.board = board

    pass


class Board:
    def __init__(self, level_description):
        self.rows = len(level_description)
        self.cols = len(level_description[0])
        self.board = self.to_board(level_description)

    def to_board(self, level_description):
        board = {}

        for i in range(len(level_description)):
            for j, cell in enumerate(level_description[i]):
                position = (i, j)

                if cell:
                    board[position] = cell

        return board

    def get(self, position):
        """
        Gets the cell at position
        """
        return self.board.get(position, [])

    def move_object(self, obj, from_, to):
        self.remove_from_cell(obj, from_)
        self.add_to_cell(obj, to)

    def remove_from_cell(self, obj, position):
        cell = self.get(position)

        cell.remove(obj)

        if not cell:
            del self.board[position]

    def add_to_cell(self, obj, position):
        cell = self.get(position)

        if not cell:
            self.board[position] = cell

        # add object to cell
        cell.append(obj)

    def to_level_description(self):
        level_description = [
            [self.get((i, j)) for j in range(self.cols)] for i in range(self.rows)
        ]

        return level_description


class Game:
    def __init__(self, level_description) -> None:
        self.game_board = Board(level_description)
        self.num_moves = 0

    def is_stoppable_at(self, position):
        cell = self.game_board.get(position)

        return "wall" in cell

    def is_pushable_at(self, position):
        cell = self.game_board.get(position)

        return "rock" in cell or len(set(cell) & WORDS) > 0

    def is_pullable_at(self, position):
        cell = self.game_board.get(position)

        return "computer" in cell

    def get_pushables_from_cell(self, cell):
        pushables = {}

        for obj in cell:
            if obj == "rock" or obj in WORDS:
                if obj in pushables:
                    pushables[obj] += 1
                else:
                    pushables[obj] = 1

        return pushables

    def get_pullables_from_cell(self, cell):
        pushables = {}

        for obj in cell:
            if obj == "computer":
                if obj in pushables:
                    pushables[obj] += 1
                else:
                    pushables[obj] = 1

        return pushables

    def can_move_to_position(self, position, direction):
        # check out of bounds
        if not is_in_bounds(position, self.game_board.rows, self.game_board.cols):
            return False

        is_stoppable = self.is_stoppable_at(position)
        is_pushable = self.is_pushable_at(position)

        # you can't move into here
        if is_stoppable:
            return False

        # object that does nothing
        if not is_pushable:
            return True

        # object in this cell is pushable, check if it can move into the next position in direction
        next_position = get_next_position(position, direction)

        return self.can_move_to_position(next_position, direction)

    def get_positions(self, obj):
        return [
            position
            for position in self.game_board.board
            if obj in self.game_board.get(position)
        ]

    def __get_objects_to_move(self, obj, direction):
        positions = self.get_positions(obj)

        to_move = set()

        for position in positions:
            next_position = get_next_position(position, direction)
            if self.can_move_to_position(next_position, direction):

                to_move |= self._get_objects_to_move(obj, position, direction)

        return to_move

    def _get_objects_to_move(self, obj, position, direction):
        to_move = set()
        visited = set()

        next_position = get_next_position(position, direction)
        prev_position = get_prev_position(position, direction)

        agenda = [(next_position, "push"), (prev_position, "pull")]

        while agenda:
            movement = agenda.pop(0)

            current_position, action = movement

            cell = self.game_board.get(current_position)
            next_position_ = get_next_position(current_position, direction)
            prev_position_ = get_prev_position(current_position, direction)

            if self.is_stoppable_at(next_position_):
                continue

            objects = (
                self.get_pushables_from_cell(cell)
                if action == "push"
                else self.get_pullables_from_cell(cell)
            )

            movable = {
                (k, v, current_position, next_position_) for k, v in objects.items()
            }

            visited.add(movement)

            if len(objects) != 0:
                next_ = (next_position_, "push")
                prev = (prev_position_, "pull")

                if next_ not in visited:
                    agenda.append(next_)
                    visited.add(next_)

                if prev not in visited:
                    agenda.append(prev)
                    visited.add(prev)

            to_move |= movable

        num_obj = self.game_board.get(position).count(obj)
        current_obj = {(obj, num_obj, position, next_position)}

        return to_move | current_obj

    def new_move(self, obj, direction):
        to_move = self.__get_objects_to_move(obj, direction)

        for el in to_move:
            o, count, curr, next_ = el

            for i in range(count):
                self.game_board.move_object(o, curr, next_)

        # check for defeat
        self.check_defeat()

        # update num moves
        self.num_moves += 1

    def check_defeat(self):
        defeat_locations = self.get_positions("bug")

        for defeat_location in defeat_locations:
            cell = self.game_board.get(defeat_location)
            num_yous = cell.count("snek")

            for i in range(num_yous):
                self.game_board.remove_from_cell("snek", defeat_location)

    @property
    def is_win(self):
        if self.num_moves == 0:
            return False

        # check for win
        flag_locations = self.get_positions("flag")

        for location in flag_locations:
            cell = self.game_board.get(location)

            if "snek" in cell:
                return True

        return False

    def to_level_description(self):
        return self.game_board.to_level_description()

    def __str__(self):
        return pprint.pformat(self.board)

        # return f"rows: {self.rows} cols: {self.cols} board: {self.board}"


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """

    return Game(level_description)


def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """

    game.new_move("snek", direction)

    return game.is_win


def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    return game.to_level_description()


if __name__ == "__main__":
    level_description = [
        [[], [], [], []],
        [[], [], ["snek"], []],
        [[], [], [], []],
        [["SNEK"], ["IS"], ["YOU"], []],
    ]

    game = new_game(level_description)

    game.new_move("snek", "right")
    pprint.pprint(dump_game(game))

    print("------")

    # game.new_move("snek", "right")
    # pprint.pprint(dump_game(game))
    # game.move_object("snek", (0, 1), (0, 2))
