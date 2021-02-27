from typing import List
from settings import *
import time
import sys
import pygame


class Block:
    def __init__(self, window, colour, position, size, border=0) -> None:
        super().__init__()
        self.window = window
        self.colour = colour
        self.position = position
        self.size = size
        self.border = border
        self.cells = []

    def create_rect(self):
        self.rect = pygame.draw.rect(
            self.window, self.colour, (self.position, self.size), self.border)
        return self.rect


class Cell(Block):
    def __init__(self, window, colour, position, size, border=0) -> None:
        super().__init__(window, colour, position, size, border=border)
        self.value = 0
        self.is_selected = False
        self.candidates = [1, 2, 3, 4, 5, 6, 7, 8, 9]


class Candidate(Cell):
    def __init__(self, window, colour, position, size, border=0) -> None:
        super().__init__(window, colour, position, size, border=border)
        self.value = 0

    def create_rect(self):
        self.rect = pygame.draw.rect(
            self.window, self.colour, (self.position, self.size), self.border)
        return self.rect


class App:

    def __init__(self) -> None:
        super().__init__()
        pygame.init()
        pygame.display.set_caption("Sudoku")

        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.blocks: List[Block] = []
        self.cells: List[Cell] = []
        self.candidates: List[Candidate] = []

        self.init_fields()

        self.selected_cell = None
        self.show_candidates = False
        self.is_running = True
        self.is_finished = False
        self.mouse_position = None

    def init_fields(self):
        for x in range(3):
            for y in range(3):
                block = Block(self.window, BLACK, (GRID_POS[0]+(
                    BLOCK_WIDTH*x), GRID_POS[1]+(BLOCK_HEIGHT*y)), BLOCK_SIZE, 2)
                self.blocks.append(block)

        for x in range(9):
            for y in range(9):
                cell = Cell(
                    self.window, GRAY, (GRID_POS[0]+(CELL_WIDTH*x), GRID_POS[1]+(CELL_HEIGHT*y)), CELL_SIZE, 1)
                self.cells.append(cell)

        for x in range(9*3):
            for y in range(9*3):
                candidate = Candidate(self.window, WHITE, (GRID_POS[0]+(
                    CANDIDATE_WIDTH*x), GRID_POS[1]+(CANDIDATE_HEIGHT*y)), CANDIDATE_SIZE, 1)
                self.candidates.append(candidate)

    def events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

                if (self.is_int(event.unicode)):
                    self.selected_cell.value = event.unicode

                if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    self.selected_cell.value = 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # cell = next((cell for cell in self.cells if cell.rect.collidepoint(
                    #    self.mouse_position)), None)
                    if self.button_show_candidates.collidepoint(self.mouse_position):
                        self.show_candidates = not self.show_candidates
                    else:
                        for c in self.cells:
                            c.is_selected = False
                            if c.rect.collidepoint(self.mouse_position):
                                self.selected_cell = c
                                self.selected_cell.is_selected = True

                        if self.show_candidates:
                            candidate = next((candidate for candidate in self.candidates if candidate.rect.collidepoint(
                                self.mouse_position)), None)

                            if candidate.value:
                                self.selected_cell.value = candidate.value
                                candidate.value = 0
                            else:
                                print("pushed on cell")
                                # candidate.value = cell.value
                                # cell.value = 0
                        else:
                            pass

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
        pygame.display.flip()
        #display update einstellen dass board nur 1x geladen wird sowie bei drawbtn

    def draw_grid(self):
        self.window.fill(WHITE)
        if self.show_candidates:
            self.draw_candidates()
        self.draw_cell()
        self.draw_block()

        #pygame.display.update()

    def draw_block(self):
        [block.create_rect() for block in self.blocks]

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

                self.text_to_rect(
                    cell.rect, cell.value, CELL_HEIGHT*0.75, BLACK, 20, 2)
            else:
                if self.show_candidates:
                    candidates = [
                        can for can in self.candidates if can.rect.colliderect(c)]
                    test = [1, 4, 7,
                            2, 5, 8,
                            3, 6, 9]
                    for i, can in zip(test, candidates):
                        can.value = i
                        can.colour = WHITE

    def draw_candidates(self):
        for candidate in self.candidates:
            can = candidate.create_rect()
            if candidate.value:
                self.text_to_rect(can, candidate.value,
                                  CANDIDATE_HEIGHT*.5, GRAY, 10, 2)

                if can.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.window, LIGHTBLUE,
                                     ((can.x, can.y), CANDIDATE_SIZE), 4)

    def draw_button(self):
        border = pygame.draw.rect(self.window, BLACK, (600, 40, 150, 30), width=5)
        self.button_show_candidates = pygame.draw.rect(self.window, GRAY, (600, 40, 150, 30), border_radius=1)
        self.text_to_rect(self.button_show_candidates, "Toggle Candidates", 20, LIGHTBLUE)



    def text_to_rect(self, rect, text, font_size, colour, offsetx=0, offsety=0):
        font_size = int(font_size)
        font_style = pygame.font.SysFont("arial", font_size)
        font = font_style.render(str(text), False, colour)

        self.window.blit(font, (rect.x + offsetx, rect.y + offsety))

    def is_int(self, string):
        try:
            int(string)
            return True
        except Exception:
            return False


if __name__ == "__main__":
    app = App()
    app.run()
