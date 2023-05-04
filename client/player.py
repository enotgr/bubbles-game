import re

class Player():
  def __init__(self, data):
    r_, color_ = data.split('&&')
    self.r = int(r_)
    self.color = tuple(map(int, re.findall(r'-?\d+', color_)))

  def set_radius(self, r):
    self.r = r