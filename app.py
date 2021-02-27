from typing import List
from settings import *
from helper import *
from random import choice

import random
import sys
import pygame


class PyRect:
    def __init__(self, window, colour, position, size, border=0) -> None:
        super().__init__()
        self.window = window
        self.colour = colour
        self.position = position
        self.size = size
        self.border = border

    def create_rect(self):
        self.rect = pygame.draw.rect(
            self.window, self.colour, (self.position, self.size), self.border)
        return self.rect


class Candidate(PyRect):
    def __init__(self, window, colour, position, size, border=0) -> None:
        super().__init__(window, colour, position, size, border=border)
        self.value: int = 0

    def _get_value(self):
        return self.__value

    def _set_value(self, value):
        if not isinstance(value, int):
            raise TypeError("bar must be set to an integer")
        self.__value = value
    value = property(_get_value, _set_value)


class Cell(PyRect):
    def __init__(self, window, colour, position, size, border=0) -> None:
        super().__init__(window, colour, position, size, border=border)

        self.value: int = 0
        self.is_selected = False
        self.candidates: List[Candidate] = []
        self.position_tuple = None
        self.text = None
        self.is_valid = True
        self.text_colour = BLACK
        self.block_no = None
        self.block: Block = None

    def create_candidate(self, candidate: Candidate):
        self.candidates.append(candidate)
        return candidate


class Block(PyRect):
    def __init__(self, window, colour, position, size, border=0) -> None:
        super().__init__(window, colour, position, size, border=border)

        self.cells: List[Cell] = []
        self.number = None
        self.position_tuple = None
        self.is_completed = False

    def create_cell(self, cell: Cell):
        cell.block_no = self.number
        cell.block = self
        self.cells.append(cell)
        return cell


class App:

    def __init__(self, board_counter=0) -> None:
        super().__init__()

        pygame.init()
        pygame.display.set_caption("Sudoku")

        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.board_counter=board_counter

        self.blocks: List[Block] = []
        self.cells: List[Cell] = []
        self.candidates: List[Candidate] = []

        self.init_fields()
        self.init_board(BOARDS[self.board_counter])

        self.selected_cell = None
        self.show_validation = True
        self.is_running = True
        self.is_finished = False
        self.mouse_position = None

        self.can_color = LIGHTBLUE
        self.val_color = LIGHTBLUE
        self.hint_color = LIGHTBLUE
        self.naksing_color = LIGHTBLUE
        self.hidsing_color = LIGHTBLUE
        self.hidpair_color = LIGHTBLUE
        self.xwing_color = LIGHTBLUE
        self.board_color = LIGHTBLUE

        self.hint_text = None
        self.hint_text2 = None

        self.show_candidates = True
        self.draw()
        self.show_candidates = False


    def init_board(self, board):
        limit = len(board)
        for x in range(limit):
            for y in range(limit):
                cell = self.cells[x*limit+y]
                cell.value = board[y][x]
                cell.is_valid = True
        self.set_candidate_values()

    def set_candidate_values(self):
        can_values = [1, 4, 7,
                      2, 5, 8,
                      3, 6, 9]
        for cell in self.cells:
            for candidate, value in zip(cell.candidates, can_values):
                candidate.value = value if check_candidates(
                    cell.block, self.cells, cell, value) else 0

    def init_fields(self):
        limit = 3
        for idx, x in enumerate(range(limit)):
            for idy, y in enumerate(range(limit)):
                block = Block(self.window, BLACK, (GRID_POS[0]+(
                    BLOCK_WIDTH*x), GRID_POS[1]+(BLOCK_HEIGHT*y)), BLOCK_SIZE, 2)

                block.number = 1+idx + limit*idy
                block.position_tuple = (x, y)
                self.blocks.append(block)

        x_counter = 0

        for idx, x in enumerate(range(9)):
            y_counter = -1
            if idx % 3 == 0:
                x_counter += 1
            for idy, y in enumerate(range(9)):
                if idy % 3 == 0:
                    y_counter += 1
                block_no = x_counter + (y_counter*3)

                cell = next(b.create_cell(Cell(
                    self.window, GRAY, (GRID_POS[0]+(CELL_WIDTH*x), GRID_POS[1]+(CELL_HEIGHT*y)), CELL_SIZE, 1))
                    for b in self.blocks if b.number == block_no)

                cell.position_tuple = (x, y)
                self.cells.append(cell)

                for i in range(3):
                    for k in range(3):
                        candidate = cell.create_candidate(Candidate(self.window, WHITE, (GRID_POS[0]+(
                            CANDIDATE_WIDTH*i + CELL_WIDTH*x), GRID_POS[1]+(CANDIDATE_HEIGHT*k + CELL_HEIGHT*y)), CANDIDATE_SIZE, 1))
                        self.candidates.append(candidate)

    def events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

                if (is_int(event.unicode) and self.selected_cell):
                    is_valid = check_is_valid(self.selected_cell.block,
                                              self.cells, self.selected_cell, int(event.unicode))

                    self.selected_cell.is_valid = True if is_valid else False
                    self.selected_cell.text_colour = BLACK if self.selected_cell.is_valid else RED
                    self.selected_cell.value = int(event.unicode)

                    self.set_candidate_values()
                    if self.selected_cell.is_valid:
                        self.selected_cell.block.is_completed = True

                        for c in self.selected_cell.block.cells:
                            if not c.value:
                                self.selected_cell.block.is_completed = False
                                break
                        if check_is_finished(self.blocks):
                            print("You finished the game!")

                if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    if self.selected_cell:
                        self.selected_cell.value = 0
                        self.set_candidate_values()

            if event.type == pygame.MOUSEBUTTONUP:
                self.selected_cell = None

                if event.button == 1:
                    if self.button_show_validation.collidepoint(self.mouse_position):
                        self.show_validation = not self.show_validation
                        self.val_color=self.toggle_color(self.val_color)
                    elif self.button_show_candidates.collidepoint(self.mouse_position):
                        self.show_candidates = not self.show_candidates
                        self.can_color=self.toggle_color(self.can_color)

                    elif self.button_show_hint.collidepoint(self.mouse_position):
                        self.show_hint(self.blocks, self.cells)
                        self.hint_color=self.toggle_color(self.hint_color)

                    elif self.button_naked_single.collidepoint(self.mouse_position):
                        self.show_single_hint(show_hint_naked_single(self.cells), "Naked Single")
                        self.naksing_color=self.toggle_color(self.naksing_color)

                    elif self.button_hidden_single.collidepoint(self.mouse_position):
                        self.show_single_hint(show_hint_hidden_single(self.blocks, self.cells), "Hidden Single")
                        self.hidsing_color=self.toggle_color(self.hidsing_color)


                    elif self.button_hidden_pair.collidepoint(self.mouse_position):
                        self.show_single_hint(show_hint_hidden_pair(self.blocks, self.cells), "Hidden Pair")
                        self.hidpair_color=self.toggle_color(self.hidpair_color)

                    elif self.button_show_xwing.collidepoint(self.mouse_position):
                        self.show_single_hint(show_hint_x_wing(self.cells), "X-Wing")
                        self.xwing_color=self.toggle_color(self.xwing_color)

                    elif self.button_change_board.collidepoint(self.mouse_position):
                        self.board_color=self.toggle_color(self.board_color)

                        if (self.board_counter+1) >= len(BOARDS):
                            self.board_counter = -1
                        self.__init__(self.board_counter+1)

                    else:
                        for c in self.cells:
                            c.is_selected = False
                            if c.rect.collidepoint(self.mouse_position):
                                self.selected_cell = c
                                self.selected_cell.is_selected = True

                        if self.show_candidates:
                            candidate = next((candidate for candidate in self.candidates if candidate.rect.collidepoint(
                                self.mouse_position)), None)

                            if candidate and candidate.value:
                                is_valid = check_is_valid(self.selected_cell.block,
                                                          self.cells, self.selected_cell, int(candidate.value))

                                self.selected_cell.is_valid = True if is_valid else False
                                self.selected_cell.text_colour = BLACK if self.selected_cell.is_valid else RED
                                self.selected_cell.value = candidate.value
                                candidate.value = 0
                                self.set_candidate_values()
                                if self.selected_cell.is_valid:
                                    self.selected_cell.block.is_completed = True

                                    for c in self.selected_cell.block.cells:
                                        if not c.value:
                                            self.selected_cell.block.is_completed = False
                                            break
                                    if check_is_finished(self.blocks):
                                        print("You finished the game!")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.button_show_hint.collidepoint(self.mouse_position):
                        self.hint_color=self.toggle_color(self.hint_color)

                    elif self.button_naked_single.collidepoint(self.mouse_position):
                        self.naksing_color=self.toggle_color(self.naksing_color)

                    elif self.button_hidden_single.collidepoint(self.mouse_position):
                        self.hidsing_color=self.toggle_color(self.hidsing_color)

                    elif self.button_hidden_pair.collidepoint(self.mouse_position):
                        self.hidpair_color=self.toggle_color(self.hidpair_color)

                    elif self.button_show_xwing.collidepoint(self.mouse_position):
                        self.xwing_color=self.toggle_color(self.xwing_color)

                    elif self.button_change_board.collidepoint(self.mouse_position):
                        self.board_color=self.toggle_color(self.board_color)
            
    def run(self):
        while self.is_running:
            self.events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

    def update(self):
        self.mouse_position = pygame.mouse.get_pos()

    def draw(self):
        self.draw_grid()
        self.draw_button()
        self.draw_numbers()
        self.draw_hint()
        pygame.display.flip()
        # display update einstellen dass board nur 1x geladen wird sowie bei drawbtn

    def draw_grid(self):
        self.window.fill(WHITE)
        if self.show_candidates:
            self.draw_candidates()
        self.draw_cell()
        self.draw_block()

    def draw_block(self):
        [block.create_rect() for block in self.blocks]

    def draw_numbers(self):
        for cell in self.cells:
            if cell.value:
                cell.text = self.text_to_rect(
                    cell.rect, cell.value, CELL_HEIGHT*0.75, cell.text_colour, 20, 2)

    def draw_cell(self):
        for cell in self.cells:
            c = cell.create_rect()
            if c.collidepoint(pygame.mouse.get_pos()) or cell.is_selected:
                pygame.draw.rect(self.window, LIGHTBLUE,
                                 ((c.x, c.y), CELL_SIZE), 4)
            if cell.value:
                if self.show_candidates:
                    candidates = [
                        can for can in self.candidates if can.rect.colliderect(c)]
                    for can in candidates:
                        can.value = 0
                        can.colour = WHITE
            """else:
                if self.show_candidates:
                     candidates = [
                        can for can in self.candidates if can.rect.colliderect(c)]
                    test = [1, 4, 7,
                            2, 5, 8,
                            3, 6, 9]
                    for i, can in zip(test, candidates):
                        can.value = i
                        can.colour = WHITE """

    def draw_candidates(self):
        for candidate in self.candidates:
            can = candidate.create_rect()
            if candidate.value:
                self.text_to_rect(can, candidate.value,
                                  CANDIDATE_HEIGHT*.70, GRAY, 10, 2)

                if can.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.window, LIGHTBLUE,
                                     ((can.x+4, can.y), CANDIDATE_SIZE), 1)

    def draw_button(self):
        # button for candidate
        pygame.draw.rect(
            self.window, BLACK, (600, 40, 180, 38), width=5)
        self.button_show_candidates = pygame.draw.rect(
            self.window, self.can_color, (600, 40, 180, 38), border_radius=1)
        self.cent_text_to_rect(self.button_show_candidates,
                          "Toggle Candidates", 20, WHITE)

        # button for validation
        pygame.draw.rect(
            self.window, BLACK, (600, 110, 180, 38), width=5)
        self.button_show_validation = pygame.draw.rect(
            self.window, self.val_color, (600, 110, 180, 38), border_radius=1)
        self.cent_text_to_rect(self.button_show_validation,
                          "Toggle Mistakes", 20, WHITE)

        # button for hint
        pygame.draw.rect(
            self.window, BLACK, (600, 180, 180, 35), width=5)
        self.button_show_hint = pygame.draw.rect(
            self.window, self.hint_color, (600, 180, 180, 35), border_radius=1)
        self.cent_text_to_rect(self.button_show_hint,
                          "Show Hint", 20, WHITE)

        # button for hint
        pygame.draw.rect(
            self.window, BLACK, (600, 250, 180, 35), width=5)
        self.button_naked_single = pygame.draw.rect(
            self.window, self.naksing_color, (600, 250, 180, 35), border_radius=1)
        self.cent_text_to_rect(self.button_naked_single,
                          "Show Naked Single", 20, WHITE)

                                  # button for hint
        pygame.draw.rect(
            self.window, BLACK, (600, 320, 180, 35), width=5)
        self.button_hidden_single = pygame.draw.rect(
            self.window, self.hidsing_color, (600, 320, 180, 35), border_radius=1)
        self.cent_text_to_rect(self.button_hidden_single,
                          "Show Hidden Single", 20, WHITE)

                                  # button for hint
        pygame.draw.rect(
            self.window, BLACK, (600, 390, 180, 35), width=5)
        self.button_hidden_pair = pygame.draw.rect(
            self.window, self.hidpair_color, (600, 390, 180, 35), border_radius=1)
        self.cent_text_to_rect(self.button_hidden_pair,
                          "Show Hidden Pair", 20, WHITE)

                                  # button for hint
        pygame.draw.rect(
            self.window, BLACK, (600, 460, 180, 35), width=5)
        self.button_show_xwing = pygame.draw.rect(
            self.window, self.xwing_color, (600, 460, 180, 35), border_radius=1)
        self.cent_text_to_rect(self.button_show_xwing,
                          "Show X-Wing", 20, WHITE)

        pygame.draw.rect(
            self.window, BLACK, (600, 530, 180, 35), width=5)
        self.button_change_board = pygame.draw.rect(
            self.window, self.board_color, (600, 530, 180, 35), border_radius=1)
        self.cent_text_to_rect(self.button_change_board,
                          "Change Board", 20, WHITE)

    def text_to_rect(self, rect, text, font_size, colour, offsetx=0, offsety=0):
        font_size = int(font_size)
        font_style = pygame.font.SysFont("arial", font_size)
        font = font_style.render(str(text), True, colour)

        self.window.blit(font, (rect.x + offsetx, rect.y + offsety))
    
    def cent_text_to_rect(self, rect, text, font_size, colour, offsetx=0, offsety=0):
        font_size = int(font_size)
        font_style = pygame.font.SysFont("calibri", font_size, True)
        font = font_style.render(str(text), True, colour)
        
        font_rect = font.get_rect(center=(rect.width /2, rect.height/2))
       
        self.window.blit(font, (rect.x + font_rect.x, rect.y + font_rect.y))
        
    def toggle_color(self, color):
        return DARKBLUE if color == LIGHTBLUE else LIGHTBLUE

    """ def show_hint(self, blocks, cells, ex_choice=[]):

        hints = None
        try:
            rand=choice([i for i in range(1,5) if i not in ex_choice])
        except IndexError:
            ex_choice = []
            print("No hints left")

            return

        if rand == 1:
            hints = show_hint_naked_single(cells)
        elif rand == 2:
            hints = show_hint_hidden_single(blocks, cells)
        elif rand == 3:
            hints = show_hint_hidden_pair(blocks, cells)
        elif rand == 4:
            hints = show_hint_x_wing(cells)
        
        if hints:
            rand = random.randint(0, len(hints)-1)
            print(hints[rand])
        else:    
            if len(ex_choice) < 4:
                ex_choice.append(rand)
                print(f"Appeneded {rand}: {ex_choice}")
                self.show_hint(self.blocks, self.cells, ex_choice=ex_choice) """

    def show_single_hint(self, hints, technique=False):
        if hints:
            rand = random.randint(0, len(hints)-1)
            self.hint_text = hints[rand]
            lines = self.hint_text.split('\n')
            if len(lines) == 2:
                self.hint_text = lines[0]
                self.hint_text2 = lines[1]
            else:
                self.hint_text2 = None
            pygame.display.flip()
        else:
            if technique:
                self.hint_text = f"No hint for {technique}"
            else:
                self.hint_text = "-"

    def draw_hint(self):
        font_size = 50
        font_style = pygame.font.SysFont("calibri", font_size, True)
        font = font_style.render("Hint:", True, BLACK)
        
        self.window.blit(font, (50, 500))
        hint_text = font_style.render(self.hint_text, True, BLACK)
        self.window.blit(hint_text, (50, 600))

        hint_text2 = font_style.render(self.hint_text2, True, BLACK)
        self.window.blit(hint_text2, (50, 600 + hint_text.get_height()))

    def show_hint(self, blocks, cells, tries=0):
        print(f"Try: {tries}")

        if tries == 10:
            self.hint_text = "No hints"
            return

        rand=random.randint(1,4)
        hints = None

        def is_hints_empty(hints):
            return len(hints) == 0

        if rand == 1:
            hints = show_hint_naked_single(cells)
        elif rand == 2:
            hints = show_hint_hidden_single(blocks, cells)
        elif rand == 3:
            hints = show_hint_hidden_pair(blocks, cells)
        elif rand == 4:
            hints = show_hint_x_wing(cells)
        
        if hints:
            self.show_single_hint(hints)
        else:    
            self.show_hint(blocks=blocks, cells=cells, tries=tries+1)
