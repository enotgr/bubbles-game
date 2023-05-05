import socket
import pygame
import random
import re

from consts import ROOM_WIDTH, ROOM_HEIGHT, SERVER_WINDOW_WIDTH, SERVER_WINDOW_HEIGHT, SERVER_IP, PORT, FPS, START_PLAYER_SIZE, MOBS_QUANTITY, MICROBE_SIZE, MICROBES_QUANTITY
from player import Player
from microbe import Microbe

def init_pygame():
  pygame.init()
  screen = None
  if not is_remote_server:
    screen = pygame.display.set_mode((SERVER_WINDOW_WIDTH, SERVER_WINDOW_HEIGHT))
  clock = pygame.time.Clock()
  return screen, clock

def is_closed():
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      return True
  return False

def draw_players():
  for player in players:
    x = round(player.x * SERVER_WINDOW_WIDTH / ROOM_WIDTH)
    y = round(player.y * SERVER_WINDOW_HEIGHT / ROOM_HEIGHT)
    r = round(player.r * SERVER_WINDOW_WIDTH / ROOM_WIDTH)
    pygame.draw.circle(screen, player.color, (x, y), r)
  pygame.display.update()

def extract_last_vector(s):
  pattern = r'<(-?\d+),(-?\d+)>'
  matches = re.findall(pattern, s)
  if matches:
    return tuple(map(int, matches[-1]))
  return (0, 0)

def create_main_socket():
  main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

  try:
    main_socket.bind((SERVER_IP, PORT))
  except socket.error as e:
    print(e)

  main_socket.setblocking(0)
  main_socket.listen(8)
  return main_socket

def send_all():
  for i in range(len(players)):
    if not players[i].conn or not players[i].ready:
      continue

    try:
      players[i].conn.send(messages[i].encode())
      players[i].errors_count = 0
    except:
      if i >= len(players):
        print('ERR: List out of range')
        return
      players[i].errors_count += 1

def remove_dead():
  for player in players:
    if not player.r:
      if player.conn:
        player.dead += 1
      else:
        player.dead += 300
    if (player.errors_count == 500) or (player.dead >= 300):
      disconnect_player(player)

  for microbe in microbes:
    if microbe.r == 0:
      microbes.remove(microbe)

def check_new_connections():
  try:
    conn, addr = main_socket.accept()
    print('Connected to:', addr)
    conn.setblocking(0)
    add_player(conn, addr)
    # start_new_thread(threaded_client, (conn, current_player))
  except:
    # print('No one wants enter the game')
    pass

def disconnect_player(player):
  if player.conn:
    player.conn.close()
  players.remove(player)
  # print('Player disconnected')

def read_players_data(global_tick):
  for player in players:
    if not player.conn and global_tick == 0:
      v = (random.randint(-100, 100), random.randint(-100, 100))
      player.change_speed(v)
      player.update()
      continue

    try:
      data = player.conn.recv(2048).decode()
      if data[0] == '!':
        player.ready = True
      elif data[0] == '.' and data[-1] == '.':
        player.set_options(data)
        data_to_send = f'{START_PLAYER_SIZE}&&{player.color}'
        player.conn.send(data_to_send.encode())
      else: 
        v = extract_last_vector(data)
        player.change_speed(v)
    except:
      pass
    player.update()

def get_players_visions():
  players_visions = [[] for i in range(len(players))]

  for i in range(len(players)):
    for k in range(len(microbes)):
      dist_x = microbes[k].x - players[i].x
      dist_y = microbes[k].y - players[i].y
      microbe_opponent = find_opponent(players[i], microbes[k], dist_x, dist_y)
      if microbe_opponent:
        players_visions[i].append(microbe_opponent)

    for j in range(i + 1, len(players)):
      dist_x = players[j].x - players[i].x
      dist_y = players[j].y - players[i].y

      opponent = find_opponent(players[i], players[j], dist_x, dist_y)
      if opponent:
        players_visions[i].append(opponent)

      opponent = find_opponent(players[j], players[i], dist_x, dist_y, True)
      if opponent:
        players_visions[j].append(opponent)

  return players_visions

def find_opponent(player1, player2, dist_x, dist_y, is_inverted=False):
  if (
      (abs(dist_x) <= (player1.w_vision // 2) + player2.r)
      and
      (abs(dist_y) <= (player1.h_vision // 2) + player2.r)
    ):
      check_absorption(player1, player2, dist_x, dist_y)

      if (not player1.conn) or (player2.r == 0):
        return ''
      
      dist_x_ = dist_x / player1.S
      dist_y_ = dist_y / player1.S

      x_ = str(round(-dist_x_ if is_inverted else dist_x_))
      y_ = str(round(-dist_y_ if is_inverted else dist_y_))
      r_ = str(round(player2.r / player1.S))
      color_ = str(player2.color)

      name_ = ''

      try:
        name_ = player2.name
      except:
        pass

      result = f'{x_} {y_} {r_}::{color_}'

      if (player2.r >= 30 * player1.S) and name_:
        result += f'::{name_}'

      return result
  return ''

def check_absorption(player1, player2, dist_x, dist_y):
  if (dist_x**2 + dist_y**2)**0.5 <= player1.r and player1.r > 1.1 * player2.r:
    player1.set_radius((player1.r**2 + player2.r**2)**0.5)
    player2.set_radius(0)

def add_player(conn, addr):
  x = random.randint(1, ROOM_WIDTH - 1)
  y = random.randint(1, ROOM_HEIGHT - 1)

  spawn = random.choice(microbes)

  if spawn:
    x = spawn.x
    y = spawn.y
    microbes.remove(spawn)

  new_player = Player(conn, addr,
                      x, y,
                      START_PLAYER_SIZE,
                      (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

  players.append(new_player)

def add_mobs(is_initial=True):
  count = MOBS_QUANTITY - len(players)

  for i in range(count):
    x = random.randint(1, ROOM_WIDTH - 1)
    y = random.randint(1, ROOM_HEIGHT - 1)

    if not is_initial:
      spawn = random.choice(microbes)

      if spawn:
        x = spawn.x
        y = spawn.y
        microbes.remove(spawn)

    new_player = Player(None, None,
                        x, y,
                        random.randint(10, 100),
                        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    players.append(new_player)

def add_microbes():
  count = MICROBES_QUANTITY - len(microbes)
  for i in range(count):
    new_microbe = Microbe(random.randint(1, ROOM_WIDTH - 1),
                          random.randint(1, ROOM_HEIGHT - 1),
                          MICROBE_SIZE,
                          (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    microbes.append(new_microbe)

is_remote_server = True

screen, clock = init_pygame()
main_socket = create_main_socket()

players = []
microbes = []

is_server_works = True
global_tick = 0

add_mobs(True)
add_microbes()

while is_server_works:
  clock.tick(FPS)

  if global_tick == 200:
    check_new_connections()
    add_mobs()
    add_microbes()

  # Считываем данные игроков
  read_players_data(global_tick)

  # Определяем область видимости каждого игрока
  players_visions = get_players_visions()
  messages = ['' for i in range(len(players))]
  for i in range(len(players)):
    player_r_ = str(round(players[i].r / players[i].S))
    messages[i] = f'<{player_r_}**{"&&".join(players_visions[i])}>'

  # Отправляем всем новое состояние игры
  send_all()

  # Чистим поле от отвалившихся игроков
  remove_dead()

  # Отрисовываем комнату
  if is_closed():
    is_server_works = False
  if not is_remote_server:
    draw_players()
    screen.fill((0, 0, 0))

  if global_tick == 200:
    global_tick = 0
  else:
    global_tick += 1

pygame.quit()
main_socket.close()
