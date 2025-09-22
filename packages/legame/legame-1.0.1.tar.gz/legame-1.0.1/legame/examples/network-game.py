#  legame/examples/network-game.py
#
#  Copyright 2020 - 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Demonstrates sending moves over a network.
"""
import argparse, logging
import random
try:
	from pygame.locals import K_q, K_ESCAPE
except ImportError:
	from pygame import K_q, K_ESCAPE
from pygame.sprite import Sprite
from legame.game import Game, GameState, GameStateFinal
from legame.board_game import BoardGame, GameBoard, GamePiece, Cell
from legame.flipper import Flipper, FlipBetween, FlipThrough, FlipNone
from legame.network_game import NetworkGame
from legame.exit_states import ExitAnimation


class TestGame(BoardGame, NetworkGame):

	xfer_interval	= 0.1		# Number of seconds between calls to service the messenger

	def __init__(self, options = None):
		self.set_resource_dir_from_file(__file__)
		BoardGame.__init__(self, options)
		NetworkGame.__init__(self, options)

	def get_board(self):
		return GameBoard(5, 5)

	def initial_state(self):
		global board, statusbar, send, me, my_opponent
		board = Game.current.board
		statusbar = Game.current.statusbar
		send = Game.current.messenger.send
		return GSWhoGoesFirst()

# ----------------------------------------
# Game states:

class GSBase(GameState):
	"""
	Used as the base class of all game states defined in this module.
	"""

	def key_down(self, event):
		"""
		Exit game immediately if K_ESCAPE or "q" key pressed
		"""
		if event.key in (K_ESCAPE, K_q):
			GSQuit(who = "me")


class GSWhoGoesFirst(GSBase):

	may_click	= False

	def enter_state(self):
		logging.debug("Enter state GSWhoGoesFirst")
		self.pick_a_color()

	def pick_a_color(self):
		logging.debug("pick_a_color()")
		self.my_roll = MsgPickAColor()
		self.my_roll.color = random.choice(["r", "g", "b"])
		self.my_roll.number = random.randrange(1, 255)
		send(self.my_roll)
		statusbar.write("Rolling for %s (my number is %d)" % (self.my_roll.color, self.my_roll.number))

	def handle_message(self, message):
		if isinstance(message, MsgPickAColor):
			if message.number == 0:
				if message.color == self.my_roll.color:
					raise Exception("Other machine conceded same color")
				Game.current.opponent_color = message.color
				logging.debug("Received concession: %s" % message.color)
				GSMyMove()
			elif message.number == self.my_roll.number:
				logging.debug("Picked the same number - trying again")
				self.pick_a_color()
			elif message.color == self.my_roll.color:
				# Both picked the same color. The one with the higher number gets their pick:
				if self.my_roll.number > message.number:
					logging.debug("Got dibs: %s; waiting for concession" % self.my_roll.color)
					Game.current.my_color = self.my_roll.color
					# Wait for concession MsgPickAColor with number = 0
				else:
					# Send concession MsgPickAColor with number = 0
					Game.current.opponent_color = message.color
					colors = ["r", "g", "b"]
					colors.remove(message.color)
					Game.current.my_color = random.choice(colors)
					self.my_roll = MsgPickAColor()
					self.my_roll.color = Game.current.my_color
					self.my_roll.number = 0
					logging.debug("Senging concession: %s" % self.my_roll.color)
					send(self.my_roll)
					GSWaitYourTurn()
			else:
				# Picked different colors. The one with the higher number moves first:
				Game.current.my_color = self.my_roll.color
				Game.current.opponent_color = message.color
				if message.number > self.my_roll.number:
					logging.debug("Picked different colors - I move first")
					GSMyMove()
				else:
					logging.debug("Picked different colors - they move first")
					GSWaitYourTurn()
		elif isinstance(message, MsgQuit):
			GSQuit(who = "them")
		else:
			logging.error("Unexpected message during GSWhoGoesFirst: %s" % message)
			GSQuit(who = "me")


class GSMyMove(GSBase):

	def enter_state(self):
		statusbar.write("GSMyMove")
		for y in range(board.rows):
			for x in range(board.columns):
				cell = Cell(x, y)
				if board.piece_at(cell) is None:
					Block(cell, Game.current.my_color)
					send(MsgAdd(cell = cell))
					GSWaitYourTurn()
					return
		GSQuit(who = "me")


class GSWaitYourTurn(GSBase):

	def enter_state(self):
		statusbar.write("GSWaitYourTurn")

	def handle_message(self, message):
		if isinstance(message, MsgAdd):
			message.rotate()
			board.set_cell(message.cell, Block(message.cell, Game.current.opponent_color))
		elif isinstance(message, MsgQuit):
			GSQuit(who = "them")
		else:
			logging.error("Unexpected message during GSWaitYourTurn: %s" % message)
			GSQuit(who = "me")
		GSMyMove()


class GSQuit(GameStateFinal):

	def enter_state(self):
		if self.who == "me": send(MsgQuit())
		ExitAnimation("bye-bye.png")

# ----------------------------------------
# Game pieces and other sprites:

class Block(GamePiece, Flipper):

	def __init__(self, cell, color):
		self.image_folder = "Block/" + color
		GamePiece.__init__(self, cell, color)
		Flipper.__init__(self, FlipThrough("enter", fps = 25), FlipNone())
		self.__glow = None

	def update(self):
		GamePiece.update(self)
		Flipper.update(self)

	def jiggle(self):
		self.flip(FlipBetween("jiggle", loops = 11, fps = 30), FlipNone())
		return self

	def glow(self):
		self.__glow = Glow(self.cell)
		return self

	def unglow(self):
		if self.__glow:
			self.__glow.kill()
			self.__glow = None
		return self


class Glow(Flipper, Sprite):

	def __init__(self, cell, frame = 0):
		self.cell = cell
		Sprite.__init__(self, Game.current.sprites)
		Game.current.sprites.change_layer(self, Game.LAYER_BELOW_PLAYER)
		Flipper.__init__(self, FlipBetween(loop_forever = True, frame = frame, fps = 30))
		self.rect = self.cell.get_rect()


if __name__ == '__main__':
	p = argparse.ArgumentParser()
	p.add_argument("--transport", type = str, default = "json")
	p.add_argument("--quiet", "-q", action = "store_true", help = "Don't make sound")
	p.add_argument("--verbose", "-v", action = "store_true", help = "Show more detailed debug information")
	p.add_argument("--direct", "-d", action = "store_true", help = "Connect by ip address instead of using udp broadcast discovery.")
	p.epilog = __doc__
	options = p.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)

	if options.transport == "json":
		from cable_car.json_messages import Message, MsgQuit

		class MsgAdd(Message):

			def encoded_attributes(self):
				return { "cell" : (self.cell.column, self.cell.row) }

			def decode_attributes(self, attributes):
				self.cell = Cell(*attributes["cell"])

			def rotate(self):
				self.cell = board.rotate(self.cell)
				return self

		class MsgPickAColor(Message):
			pass

	else:
		from cable_car.byte_messages import Message, MsgQuit

		class MsgAdd(Message):
			code = 0x8

			def encode(self):
				"""
				Encode column, row:
				"""
				return bytearray([self.cell.column, self.cell.row])

			def decode(self, msg_data):
				"""
				Read column, row from message data.
				"""
				self.cell = Cell(msg_data[0], msg_data[1])

			def rotate(self):
				self.cell = board.rotate(self.cell)
				return self

		class MsgPickAColor(Message):
			code = 0x9

			def encode(self):
				"""
				Encode color, number
				"""
				return bytearray([self.number]) + self.color.encode("ASCII")

			def decode(self, msg_data):
				"""
				Read color and number from message data.
				"""
				self.number, self.color = msg_data[0], msg_data[1:].decode()

	p.exit(TestGame(options).run())


#  end legame/examples/network-game.py
