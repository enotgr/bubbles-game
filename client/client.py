import socket
import pygame
import re

from consts import WIDTH, HEIGHT
from player import Player

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(' Bubbles')
clock = pygame.time.Clock()

my_name = 'Me'

def is_closed():
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      return True
  return False

def get_vector(player_r):
  pos = pygame.mouse.get_pos()
  v = (pos[0] - WIDTH // 2, pos[1] - HEIGHT // 2)

  if v[0]**2 + v[1]**2 <= player_r**2:
    return (0, 0)

  return v

def get_last_complete_package(data):
  pattern = r'<([^>]+)>'
  matches = re.findall(pattern, data)
  if matches:
    last_match = matches[0]
    return last_match
  else:
    return ''

def parse_data(data):
  package = get_last_complete_package(data)
  if package:
    my_r, rest_pack = package.split('**')
    opponents_data = rest_pack.split('&&')
    draw_opponents(opponents_data)
    return my_r

def draw_opponents(opponents_data):
  if opponents_data == ['']:
    return

  for player_package in opponents_data:
    decomposed_data = player_package.split('::')
    geometry_text = decomposed_data[0]
    color_text = decomposed_data[1]
    geometry = geometry_text.split(' ')
    x_ = WIDTH // 2 + int(geometry[0])
    y_ = HEIGHT // 2 + int(geometry[1])
    r_ = int(geometry[2])
    color_ = tuple(map(int, re.findall(r'-?\d+', color_text)))

    # if (0 <= x_ < WIDTH) and (0 <= y_ < HEIGHT):
    #   pygame.draw.circle(screen, color_, (x_, y_), r_)

    pygame.draw.circle(screen, color_, (x_, y_), r_)

    if len(decomposed_data) == 3:
      write_name(x_, y_, r_, decomposed_data[2])

def write_name(x, y, r, name):
  font = pygame.font.Font(None, r)
  text = font.render(name, True, (0, 0, 0))
  rect = text.get_rect(center=(x, y))
  screen.blit(text, rect)

def main():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
  sock.connect(('localhost', 5555))

  # Отправляем первые данные (имяб размеры окна) серверу
  data_to_send = f'.{my_name}&&{WIDTH}&&{HEIGHT}.'.encode()
  sock.send(data_to_send)

  # Получаем от сервера первые данные (радиус и цвет) для инициализации игрока
  player_data = sock.recv(64).decode()

  # Подтверждаем серверу, что готовы к игре
  sock.send('!'.encode())

  player = Player(player_data)

  prev_v = (0, 0)
  curr_v = prev_v
  while True:
    screen.fill((0, 0, 0))

    # Проверяем не было ли закрыто клиентское приложение
    if is_closed():
      return

    # Определяем данные для отправки на сервер
    if pygame.mouse.get_focused():
      curr_v = get_vector(player.r)

    # Отправляем наши данные (вектор) на сервер
    if prev_v != curr_v:
      prev_v = curr_v
      message = f'<{curr_v[0]},{curr_v[1]}>'
      sock.send(message.encode())

    # Получаем данные от сервера
    try:
      data = sock.recv(2**20).decode()
      if not data:
        break
    except:
      return

    # Обрабатываем данные от сервера
    my_r = parse_data(data)
    if my_r:
      player.set_radius(int(my_r))

    # Рисуем новое состояние игрового поля
    if player.r:
      pygame.draw.circle(screen, player.color, (WIDTH // 2, HEIGHT // 2), player.r)
      write_name(WIDTH // 2, HEIGHT // 2, player.r, my_name)
    pygame.display.update()
 
if __name__ == '__main__':
  main()
