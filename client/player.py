import re
import pygame

from consts import WIDTH, HEIGHT

class Player():
  def __init__(self, data, name=''):
    r_, color_ = data.split('&&')
    self.r = int(r_)
    self.color = tuple(map(int, re.findall(r'-?\d+', color_)))
    self.name = name

  def set_radius(self, r):
    self.r = r
