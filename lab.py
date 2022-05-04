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


def is_overlap(a, b):
    return len(set(a) & set(b)) > 0


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

    def get_positions(self, filter_func):
        return [position for position in self.board if filter_func(position)]

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


class GameRules:
    def __init__(self, board: Board):
        self.board = board
        self.properties = self.get_default_properties()
        self.nouns = {}

        self.update()

    def get_default_properties(self):
        return {
            "YOU": set(),
            "STOP": set(),
            "PUSH": set(WORDS),
            "PULL": set(),
            "DEFEAT": set(),
            "WIN": set(),
        }

    def get_property_rule(self, property):
        return self.properties[property]

    def get_nouns(self, position):
        cell = self.board.get(position)

        return [obj for obj in cell if obj in NOUNS]

    def get_properties(self, position):
        cell = self.board.get(position)

        return [obj for obj in cell if obj in PROPERTIES]

    def update(self):
        # get all the
        self.properties = self.get_default_properties()

        def is_IS(position):
            cell = self.board.get(position)

            return "IS" in cell

        is_positions = self.board.get_positions(is_IS)

        # look left right, top down

        for is_position in is_positions:

            left = get_next_position(is_position, "left")
            right = get_next_position(is_position, "right")

            self.add_properties(left, right)

            up = get_next_position(is_position, "up")
            down = get_next_position(is_position, "down")

            self.add_properties(up, down)

    def add_properties(self, noun_position, property_position):
        nouns = self.get_nouns(noun_position)
        properties = self.get_properties(property_position)

        rule_exists = len(nouns) > 0 and len(properties) > 0

        if rule_exists:
            for property in properties:
                for noun in nouns:
                    self.properties[property].add(noun.lower())


class Game:
    def __init__(self, level_description) -> None:
        self.game_board = Board(level_description)
        self.rules = GameRules(self.game_board)
        self.num_moves = 0

    def is_stoppable_at(self, position):
        cell = self.game_board.get(position)
        stop_rules = self.rules.get_property_rule("STOP")
        push_rules = self.rules.get_property_rule("PUSH")

        stoppable = False

        for obj in cell:
            if obj in stop_rules and obj not in push_rules:
                return True

        return stoppable

        # return is_overlap(cell, stop_rules)

    def is_pushable_at(self, position):
        cell = self.game_board.get(position)

        push_rules = self.rules.get_property_rule("PUSH")

        return is_overlap(cell, push_rules)

    def is_pullable_at(self, position):
        cell = self.game_board.get(position)
        pull_rules = self.rules.get_property_rule("PULL")

        return is_overlap(cell, pull_rules)

    def filter_cell(self, cell, filter_func):
        filter_cell = {}

        for obj in cell:
            if filter_func(obj):
                if obj in filter_cell:
                    filter_cell[obj] += 1
                else:
                    filter_cell[obj] = 1

        return filter_cell

    def is_pushable(self, obj):
        return obj in self.rules.get_property_rule("PUSH")

    def is_pullable(self, obj):
        return obj in self.rules.get_property_rule("PULL")

    def get_pushables_from_cell(self, cell):
        pushables = {}

        for obj in cell:
            if self.is_pushable(obj):
                if obj in pushables:
                    pushables[obj] += 1
                else:
                    pushables[obj] = 1

        return pushables

    def get_pullables_from_cell(self, cell):
        pushables = {}

        for obj in cell:
            if self.is_pullable(obj):
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

    def new_get_positions(self, filter_func):
        return [position for position in self.game_board.board if filter_func(position)]

    def you_in_position(self, position):
        cell = self.game_board.get(position)
        yous = self.rules.get_property_rule("YOU")

        return is_overlap(cell, yous)

    def get_movements(self, direction):
        # get the position of the object you want to move
        positions = self.new_get_positions(self.you_in_position)

        to_move = set()

        for position in positions:
            next_position = get_next_position(position, direction)
            # check if you can move into that position
            if self.can_move_to_position(next_position, direction):
                # get all of the objects moved as a result of moving your main object
                to_move |= self.get_movements_at_position(position, direction)

        return to_move

    def get_movements_at_position(self, position, direction):
        # agenda approach
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

            # check if stoppable at next position

            # check if object is both stop and push -> object should be pushable

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

        # get the cell
        cell = self.game_board.get(position)

        # get all of the YOU objects
        you_rule = self.rules.get_property_rule("YOU")

        # get all of the YOU objects in the cell
        yous = self.filter_cell(cell, lambda object: object in you_rule)

        # get their movements
        yous_movement = {(k, v, position, next_position) for k, v in yous.items()}

        return to_move | yous_movement

    def move(self, direction):
        to_move = self.get_movements(direction)

        for el in to_move:
            o, count, curr, next_ = el

            for i in range(count):
                self.game_board.move_object(o, curr, next_)

        # check for defeat
        self.check_defeat()

        # update num moves
        self.num_moves += 1

        # update game rules
        self.rules.update()

    def create_filter(self, property):
        def filter_func(position):
            cell = self.game_board.get(position)
            rules = self.rules.get_property_rule(property)

            return is_overlap(cell, rules)

        return filter_func

    def check_defeat(self):
        defeat_locations = self.game_board.get_positions(self.create_filter("DEFEAT"))

        for defeat_location in defeat_locations:
            cell = self.game_board.get(defeat_location)
            you_rules = self.rules.get_property_rule("YOU")

            yous = self.filter_cell(cell, lambda obj: obj in you_rules)

            for obj, count in yous.items():
                for i in range(count):
                    self.game_board.remove_from_cell(obj, defeat_location)

    @property
    def is_win(self):
        if self.num_moves == 0:
            return False

        # check for win
        flag_locations = self.game_board.get_positions(self.create_filter("WIN"))

        for location in flag_locations:
            cell = self.game_board.get(location)
            you_rules = self.rules.get_property_rule("YOU")

            yous = self.filter_cell(cell, lambda obj: obj in you_rules)

            if len(yous) > 0:
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

    game.move(direction)

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

    game.move("right")
    pprint.pprint(dump_game(game))

    print("------")

    # game.new_move("snek", "right")
    # pprint.pprint(dump_game(game))
    # game.move_object("snek", (0, 1), (0, 2))
