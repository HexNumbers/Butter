import board
import busio
import adafruit_framebuf
import adafruit_is31fl3731
import random
import sys
import time
import keyboard

from cellular_automaton import *

ALIVE = [1.0]
DYING = [0.5]
DEAD = [0]

class BriansRule(Rule):
    def init_state(self, cell_coordinate):
        rand = random.randrange(0, 16, 1)
        init = max(.0, float(rand - 14))
        return [init]

    def evolve_cell(self, last_cell_state, neighbors_last_states):
        new_cell_state = last_cell_state
        alive_neighbours = self.__count_alive_neighbours(neighbors_last_states)
        if last_cell_state == DEAD and alive_neighbours == 2:
            new_cell_state = ALIVE
        if last_cell_state == ALIVE:
            new_cell_state = DYING
        if last_cell_state == DYING:
            new_cell_state = DEAD
        return new_cell_state

    @staticmethod
    def __count_alive_neighbours(neighbours):
        an = []
        for n in neighbours:
            if n == ALIVE:
                an.append(1)
        return len(an)

    def get_state_draw_color(self, current_state):
        if current_state == ALIVE:
            return [255, 255, 255]
        if current_state == DYING:
            return [20, 20, 20]
        return [0, 0 ,0]

i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_is31fl3731.CharlieBonnet(i2c)
buf = bytearray(32)
fb = adafruit_framebuf.FrameBuffer(
    buf, display.width, display.height, adafruit_framebuf.MVLSB
)

if (len(sys.argv) > 1):
    random_seed = random.seed(sys.argv[1])

neighborhood = MooreNeighborhood(EdgeRule.FIRST_AND_LAST_CELL_OF_DIMENSION_ARE_NEIGHBORS)
ca = CAFactory.make_single_process_cellular_automaton(dimension=[16, 8],
                                                      neighborhood=neighborhood,
                                                      rule=BriansRule)
frame = 0
while True:
    display.frame(frame, show=False)
    ca.evolve_x_times(1)
    for coordinate, cell in ca.get_cells().items():
            if cell.is_set_for_redraw():
                color = ca.get_current_rule().get_state_draw_color(cell.get_current_state(ca.get_current_evolution_step()))
                display.pixel(coordinate[0], coordinate[1], color[0])
    display.frame(frame, show=True)
    frame = (frame + 1) % 2
    time.sleep(0.5)