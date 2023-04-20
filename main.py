# *** Игра "Морской бой" ***
from random import randint


class Color:
    white = '\033[0m'
    gray = '\033[0;37m'
    blue = '\033[0;34m'
    yellow = '\033[0;33m'
    red = '\033[0;31m'
    green = '\033[0;32m'

    @staticmethod
    def set_color(text, color):
        return color + text + Color.white


class Cell(object):
    empty_cell = Color.set_color('□', Color.white)
    ship_cell = Color.set_color('■', Color.blue)
    miss_cell = Color.set_color('•', Color.gray)
    hit_cell = Color.set_color('●', Color.yellow)
    destroy_cell = Color.set_color('X', Color.red)


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return Color.set_color("Некорректный диапазон ввода!", Color.red)


class BoardUsedException(BoardException):
    def __str__(self):
        return Color.set_color("Вы уже стреляли в эту клетку!", Color.red)


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [[Cell.empty_cell] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = Cell.ship_cell
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = Cell.miss_cell
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", Cell.empty_cell)
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = Cell.hit_cell
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    for i in ship.dots:
                        self.field[i.x][i.y] = Cell.destroy_cell
                    print(Color.red + "Корабль уничтожен!" + Color.white)
                    print("-" * 64)
                    return True
                else:
                    print(Color.yellow + "Корабль подбит!" + Color.white)
                    print("-" * 64)
                    return True
        self.field[d.x][d.y] = Cell.miss_cell
        print("Мимо!")
        print("-" * 64)
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        while d in self.enemy.busy:
            d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    @staticmethod
    def greet():
        print(Color.yellow + "-" * 60)
        print(" Формат ввода: x y, где x - номер строки, y - номер столбца")
        print("-" * 60 + Color.white)

    def board_print(self):
        board_us = str(self.us.board).split('\n')
        board_ai = str(self.ai.board).split('\n')
        print(' ' * 6 + "Флот пользователя:" + ' ' * 19 + "Флот компьютера:")
        for i, elm in enumerate(board_us):
            print(elm + ' ' * 10 + board_ai[i])

    def loop(self):
        num = 0
        while True:
            self.board_print()
            if num % 2 == 0:
                print("-" * 64)
                repeat = self.us.move()
            else:
                print("-" * 64)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print(Color.green + "-" * 64)
                print(" " * 22 + "Пользователь выиграл!")
                print("-" * 64 + Color.white)
                self.board_print()
                break

            if self.us.board.count == 7:
                print(Color.red + "-" * 64)
                print(" " * 22 + "Компьютер выиграл!")
                print("-" * 64 + Color.white)
                self.board_print()
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
