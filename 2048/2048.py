import curses
from random import randrange, choice
from collections import defaultdict
# Actions of user
actions = ["UP", "DOWN", "RIGHT", "LEFT", "RESTART", "EXIT"]
# letter for move
letter_action = [ord(c) for c in "WSDARXwsdarx"]
action_dict = dict(zip(letter_action, actions * 2))

def get_user_action(keyboard):
    char = "N"
    while char not in action_dict:
        char = keyboard.getch()
    return action_dict[char]

#转置矩阵
def transpose(field):
    return [list(row) for row in zip(*field)]
#矩阵逆转
def invert(field):
    return [row[::-1] for row in field]

#创建棋盘
class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height # height
        self.width = width   # width
        self.win_value = win # win value
        self.score = 0       # current value
        self.highscore = 0   # highest score
        self.reset()         # reset the game

    #棋盘操作
    def spawn(self):
        new_element = 4 if randrange(100) > 89 else 2
        (i, j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element

    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()

    #能否移动
    def move_is_possible(self, direction):
        def row_is_left_movable(row):
            def change(i):
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                if row[i] != 0 and row[i + 1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))

        check = {}
        check['LEFT']  = lambda field:                              \
                any(row_is_left_movable(row) for row in field)

        check['RIGHT'] = lambda field:                              \
                 check['LEFT'](invert(field))

        check['UP']    = lambda field:                              \
                check['LEFT'](transpose(field))

        check['DOWN']  = lambda field:                              \
                check['RIGHT'](transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False

    def move(self, direction):
        def move_row_left(row):
            def tighten(row): #把零散的单元挤到一起
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row
            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row
            return tighten(merge(tighten(row)))

        moves = {}
        moves['LEFT'] = lambda field: [move_row_left(row) for row in field]
        moves['RIGHT'] = lambda field: invert(moves['LEFT'](invert(field)))
        moves['UP'] = lambda field: transpose(moves['LEFT'](transpose(field)))
        moves['DOWN'] = lambda field: transpose(moves['RIGHT'](transpose(field)))

        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False
    def is_win(self):
        return any(any(i >= self.win_value for i in row) for row in self.field)
    
    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)

    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'
        def cast(string):
            screen.addstr(string + '\n')
        
        def draw_hor_separator():
            line = '+' + ('+------' * self.width + '+')[1:]
            separator = defaultdict(lambda: line)
            if not hasattr(draw_hor_separator, "counter"):
                draw_hor_separator.counter = 0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter += 1
        
        def draw_row(row):
            cast(''.join('|{:^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')

        screen.clear()

        cast('SCORE: ' + str(self.score))
        if 0 != self.highscore:
            cast('HIGHSCORE: ' + str(self.highscore))
        
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()

        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)


def main(stdscr):

    # Restart game
    def init():
        game_field.reset()
        return 'Game'

    def not_game(state):
        #画出 GameOver 或者 Win 的界面
        game_field.draw(stdscr)
        #读取用户输入得到action，判断是重启游戏还是结束游戏
        action = get_user_action(stdscr)
        responses = defaultdict(lambda: state) # 默认是当前状态， 如果没有变化就一直保持当前
        responses["RESTART"], responses["EXIT"] = "Init", "EXIT"
        return responses[action]

    def game():

        game_field.draw(stdscr)
        action = get_user_action(stdscr)

        if action == "RESTART":
            return "Init"
        if action == "EXIT":
            return "EXIT"
        if game_field.move(action):
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'GameOver'
        return "Game"

    state_actions = {
        'Init': init,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover'),
        'Game': game
    }

    curses.use_default_colors()

    game_field = GameField(win = 32)

    state = 'Init'
    #状态机开始循环
    while state != 'EXIT':
        state = state_actions[state]()
curses.wrapper(main)


