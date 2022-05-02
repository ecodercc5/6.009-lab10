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


class Board:
    pass

    def to_level_description(self):
        pass


class Game:
    def __init__(self, level_description) -> None:
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
        return self.board.get(position, [])

    def is_stoppable_at(self, position):
        cell = self.get(position)

        return "wall" in cell

    def is_pushable_at(self, position):
        cell = self.get(position)

        return "rock" in cell or len(set(cell) & WORDS) > 0

    def is_pullable_at(self, position):
        cell = self.get(position)

        return "computer" in cell

    def can_move_to_position(self, position, direction):
        # check out of bounds
        if not is_in_bounds(position, self.rows, self.cols):
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

    def get_movables(self, position, direction):
        pass

    def new_move(self, obj, direction):
        # get all positions of the object
        positions = [position for position in self.board if obj in self.get(position)]

        for position in positions:
            next_position = get_next_position(position, direction)

            if not self.can_move_to_position(next_position, direction):
                continue

            self.move_object(obj, position, next_position)

    def move(self, direction):
        self.move_object_in("snek", direction)

    def move_object_in(self, obj, direction):
        # get all sneks
        positions = [position for position in self.board if obj in self.get(position)]

        # update sneks
        for position in positions:
            self.move_object_from_in(obj, position, direction)

    def move_object_from_in(self, obj, position, direction):
        print(f"moving {obj} from {position} to {direction}")
        delta = direction_vector[direction]

        # calculate next position of snek
        next_position = apply_delta(position, delta)

        # calculate previous position
        prev_position = apply_delta(position, negative(delta))

        # check if position is in bounds
        if not is_in_bounds(next_position, self.rows, self.cols):
            return

        # hard code wall is stop
        # check if wall is in next position
        if self.is_stoppable_at(next_position):
            return

        # loop over sneks at position
        cell = self.get(position)

        # count number of sneks
        num_objs = cell.count(obj)

        # if object in front is pushable, try to push it
        if self.is_pushable_at(next_position):
            # print("moving rock")
            # pprint.pprint(self.to_level_description())

            # print(next_position)
            self.move_object_from_in("rock", next_position, direction)
            # self.move_object("rock", position, next_position)

        # check if space has clear out
        if self.is_pushable_at(next_position):
            # print("something still pushable in front")
            return

        # check if object you're trying to move has already moved
        if obj not in self.get(position):
            return

        for _ in range(num_objs):
            # move current object
            self.move_object(obj, position, next_position)
            print(f"moving {obj}")

        if self.is_pullable_at(prev_position):
            # print("pulling something")
            # print(prev_position)
            # pprint.pprint(self.to_level_description())
            # move prev object
            self.move_object_from_in("computer", prev_position, direction)

    def move_object(self, obj, from_, to):
        num_removed = self.remove_from_cell(obj, from_)

        for i in range(num_removed):
            self.add_to_cell(obj, to)

    def remove_from_cell(self, obj, position):
        """
        Removes object from cell at position

        Return: How many objects removed
        """
        # print("removing")
        # print(position)
        cell = self.get(position)

        num_removed = cell.count(obj)

        for i in range(num_removed):
            cell.remove(obj)

        if not cell:
            del self.board[position]

        return num_removed

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

    return False


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
        [[], ["snek"], ["wall"]],
        [["SNEK"], ["IS"], ["YOU"]],
    ]

    game = new_game(level_description)

    game.new_move("snek", "right")

    # game.move_object("snek", (0, 1), (0, 2))

    pprint.pprint(dump_game(game))
