import board
import busio
import adafruit_framebuf
import adafruit_is31fl3731
import random

from cellular_automaton import *

class StarfallRule(Rule):
    def init_state(self, cell_coordinate):
        rand = random.randrange(0, 16, 1)
        init = max(.0, float(rand - 14))
        return [init]

    def evolve_cell(self, last_cell_state, neighbors_last_states):
        return self._get_neighbor_by_relative_coordinate(neighbors_last_states, (-1, -1))

    def get_state_draw_color(self, current_state):
        return [255 if current_state[0] else 0, 0, 0]


i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_is31fl3731.CharlieBonnet(i2c)
buf = bytearray(32)
fb = adafruit_framebuf.FrameBuffer(
    buf, display.width, display.height, adafruit_framebuf.MVLSB
)

if (len(sys.argv) > 1):
    random_seed = random.seed(sys.argv[1])
else 
    random_seed = random.seed(1000)

neighborhood = MooreNeighborhood(EdgeRule.FIRST_AND_LAST_CELL_OF_DIMENSION_ARE_NEIGHBORS)
ca = CAFactory.make_single_process_cellular_automaton(dimension=[16, 8],
                                                      neighborhood=neighborhood,
                                                      rule=StarfallRule)
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