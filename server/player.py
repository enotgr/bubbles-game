from consts import ROOM_WIDTH, ROOM_HEIGHT

class Player():
  def __init__(self, conn, addr, x, y, r, color):
    self.conn = conn
    self.addr = addr
    self.x = x
    self.y = y
    self.r = r
    self.color = color
    self.name = 'Mob'

    self.window_width = 800
    self.window_height = 600

    self.S = 1
    self.diff_S = 1
    self.w_vision = 800
    self.h_vision = 600

    self.errors_count = 0
    self.dead = 0
    self.ready = False

    self.abs_speed = 30 / (self.r**0.5)
    self.speed_x = 0
    self.speed_y = 0

  def set_options(self, data):
    name, window_width, window_height = data[1:-1].split('&&')
    self.name = name
    self.window_width = int(window_width)
    self.window_height = int(window_height)
    self.w_vision = int(window_width)
    self.h_vision = int(window_height)

  def change_speed(self, v):
    if v == (0, 0):
      self.speed_x = 0
      self.speed_y = 0
    else:
      len_v = (v[0]**2 + v[1]**2)**0.5
      new_v =  ((v[0] / len_v) * self.abs_speed, (v[1] / len_v) * self.abs_speed)
      self.speed_x, self.speed_y = new_v[0], new_v[1]

  def update(self):
    new_x = self.x + self.speed_x
    new_y = self.y + self.speed_y

    if 0 < new_x < ROOM_WIDTH:
      self.x = new_x

    if 0 < new_y < ROOM_HEIGHT:
      self.y = new_y

    if self.r >= 100:
      self.r -= self.r / 18000

    if not self.conn:
      return

    if (self.r >= self.w_vision / 4) or (self.r >= self.h_vision / 4):
      if (self.w_vision < ROOM_WIDTH) or (self.h_vision < ROOM_HEIGHT):
        self.S *= 2
        self.w_vision = self.window_width * self.S
        self.h_vision = self.window_height * self.S

    if (self.r < self.w_vision / 8) and (self.r < self.h_vision) and self.S > 1:
      self.S = self.S // 2
      self.w_vision = self.window_width * self.S
      self.h_vision = self.window_height * self.S

  def set_radius(self, r):
    self.r = r
    if self.r:
      self.abs_speed = 30 / (self.r**0.5)
    else:
      self.abs_speed = 0
