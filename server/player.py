from consts import ROOM_WIDTH, ROOM_HEIGHT

class Player():
  def __init__(self, conn, addr, x, y, r, color):
    self.conn = conn
    self.addr = addr
    self.x = x
    self.y = y
    self.r = r
    self.color = color

    self.w_vision = 800
    self.h_vision = 600

    self.errors_count = 0

    self.abs_speed = 30 / (self.r**0.5)
    self.speed_x = 0
    self.speed_y = 0

  def change_speed(self, v):
    if v == (0, 0):
      self.speed_x = 0
      self.speed_y = 0
    else:
      len_v = (v[0]**2 + v[1]**2)**0.5
      new_v =  ((v[0] / len_v) * self.abs_speed, (v[1] / len_v) * self.abs_speed)
      self.speed_x, self.speed_y = new_v[0], new_v[1]

  def update_position(self):
    new_x = self.x + self.speed_x
    new_y = self.y + self.speed_y

    if 0 < new_x < ROOM_WIDTH:
      self.x = new_x

    if 0 < new_y < ROOM_HEIGHT:
      self.y = new_y

  def set_radius(self, r):
    self.r = r
    self.abs_speed = 30 / (self.r**0.5)
