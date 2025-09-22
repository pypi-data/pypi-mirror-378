#  legame/tests/sprite_enhancement_test.py
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
from pygame import Rect
from legame.sprite_enhancement import MovingSprite, BoxedInSprite
from pygame.math import Vector2 as Vector
from legame import	normal_degrees, \
					DEGREES_EAST, DEGREES_NORTH, DEGREES_NORTHWEST, \
					DEGREES_WEST, DEGREES_SOUTHWEST, DEGREES_SOUTH, \
					COMPASS_WEST, COMPASS_NORTH, COMPASS_EAST, COMPASS_SOUTH


class Boxed(BoxedInSprite, MovingSprite):
	def __init__(self, box):
		MovingSprite.__init__(self)
		BoxedInSprite.__init__(self, box)


def test_constructor():
	thing = MovingSprite(9, 5)
	assert thing.x == 9
	assert thing.y == 5
	thing = MovingSprite(x = 9, y = 5, direction = 45, speed = 1000)
	assert thing.x == 9
	assert thing.y == 5
	assert thing.direction == 45
	assert thing.speed == 1000
	mag, deg = thing.motion.as_polar()
	assert deg == 45
	assert mag == 1000
	thing = MovingSprite(9, 5, 1000, 45)
	assert thing.x == 9
	assert thing.y == 5
	assert thing.direction == 45
	assert thing.speed == 1000

def test_motion():
	thing = MovingSprite(0, 0)
	thing.set_motion_polar(100, 90)
	assert thing.direction == 90
	assert thing.speed == 100

def test_basic_move():
	thing1 = MovingSprite(x = 100, y = 100)
	thing1.speed = 10
	thing1.direction = DEGREES_EAST
	thing1.cartesian_motion()
	assert thing1.x == 110
	assert thing1.y == 100
	thing1.x = 100
	assert thing1.x == 100
	assert thing1.direction == 0.0

def test_vector_copy():
	thing1 = MovingSprite(100, 100)
	thing2 = MovingSprite(0, 0)
	thing2.position = thing1.position
	assert thing2.x == thing1.x
	assert thing2.y == thing1.y

	thing1 = MovingSprite(80, 80)
	thing2 = MovingSprite()
	thing2.position = thing1.position
	assert thing2.x == thing1.x
	assert thing2.y == thing1.y

def test_boundary():

	thing = Boxed(Rect(0, 0, 40, 40))

	# Near the west wall

	thing.position = Vector(-5, 20)
	near = thing.nearest_boundary()
	assert near[0] == -5
	assert near[1] == COMPASS_WEST

	# Near the east wall
	thing.position = Vector(45, 20)
	near = thing.nearest_boundary()
	assert near[0] == -5
	assert near[1] == COMPASS_EAST

	# Near the north wall
	thing.position = Vector(20, -5)
	near = thing.nearest_boundary()
	assert near[0] == -5
	assert near[1] == COMPASS_NORTH

	# Near the south wall
	thing.position = Vector(20, 45)
	near = thing.nearest_boundary()
	assert near[0] == -5
	assert near[1] == COMPASS_SOUTH

def test_direction_to():
	tolerance = 0.0001
	thing = MovingSprite(0.0, 0.0)
	for degree in range(0, 720):
		target = MovingSprite(0, 0, degree, 10)
		target.cartesian_motion()
		dirc = normal_degrees(thing.direction_to_thing(target))
		ndeg = normal_degrees(degree)
		assert dirc - ndeg < tolerance \
			or dirc - 360 - ndeg < tolerance \
			or dirc + 360 - ndeg < tolerance

def test_turn_towards():

	tolerance = 0.0001

	# Setup subject in the middle of imaginary space
	subject = MovingSprite(x = 0.0, y = 0.0, direction = DEGREES_EAST, speed = 1.0)
	subject.max_turning_speed = 22.5

	# Setup target:
	target = MovingSprite(x = 0.0, y = 0.0)

	# Move target due south from center
	target.position = Vector(0.0, 0.0)
	target.direction = DEGREES_SOUTH
	target.cartesian_motion()

	# Check that subject turned south
	for stop in [22.5, 45.0, 67.5, 90.0]:
		subject.turn_towards(target.position)
		assert abs(subject.turning_speed - subject.max_turning_speed) < tolerance
		assert abs(subject.direction - stop) < tolerance

	# Reset the subject
	subject.direction = DEGREES_EAST
	subject.turning_speed = 0.0

	# Move target due north from center
	target.position = Vector(0.0, 0.0)
	target.direction = DEGREES_NORTH
	target.cartesian_motion()

	# Check that subject turned north
	for stop in [-22.5, -45.0, -67.5, -90.0]:
		subject.turn_towards(target.position)
		assert abs(subject.turning_speed + subject.max_turning_speed) < tolerance
		assert abs(subject.direction - stop) < tolerance

	# Reset the subject
	subject.direction = DEGREES_EAST
	subject.turning_speed = 0.0

	# Move target southwest from center
	target.position = Vector(0.0, 0.0)
	target.direction = DEGREES_SOUTHWEST
	target.cartesian_motion()

	# Check that subject turned south
	for stop in [22.5, 45.0, 67.5, 90.0]:
		subject.turn_towards(target.position)
		assert abs(subject.turning_speed - subject.max_turning_speed) < tolerance
		assert abs(subject.direction - stop) < tolerance

	# Reset the subject
	subject.direction = DEGREES_EAST
	subject.turning_speed = 0.0

	# Move target northwest from center
	target.position = Vector(0.0, 0.0)
	target.direction = DEGREES_NORTHWEST
	target.cartesian_motion()

	# Check that subject turned north
	for stop in [-22.5, -45.0, -67.5, -90.0]:
		subject.turn_towards(target.position)
		assert abs(subject.turning_speed + subject.max_turning_speed) < tolerance
		assert abs(subject.direction - stop) < tolerance

	# Reset the subject
	subject.direction = DEGREES_EAST
	subject.turning_speed = 0.0

	# Move target due west from center
	target.position = Vector(0.0, 0.0)
	target.direction = DEGREES_WEST
	target.cartesian_motion()

	# Check that subject turned north
	subject.turn_towards(target.position)
	subject.update()
	assert abs(subject.turning_speed) == subject.max_turning_speed
	assert abs(subject.direction) == abs(subject.direction)


#  end legame/tests/sprite_enhancement_test.py
