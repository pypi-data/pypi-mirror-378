import pytest
from kivy.tests.common import UnitTestTouch

from lisien.engine import Engine
from lisien.examples import polygons

from .util import advance_frames, idle_until


def test_character_switcher(polygons_sim, elide_app):
	app = elide_app
	idle_until(
		lambda: app.manager.current == "mainscreen",
		100,
		"Never switched to mainscreen",
	)
	idle_until(lambda: app.mainscreen.boardview, 100, "never got boardview")
	idle_until(
		lambda: app.mainscreen.boardview.board.spot, 100, "never got spots"
	)
	physspots = len(app.mainscreen.boardview.board.spot)
	app.mainscreen.charmenu.charmenu.toggle_chars_screen()
	idle_until(
		lambda: app.manager.current == "chars",
		100,
		"Never switched to chars",
	)
	boxl = app.chars.ids.charsview.ids.boxl
	idle_until(
		lambda: len(boxl.children) == 3,
		100,
		"Didn't get all three characters",
	)
	for charb in boxl.children:
		if charb.text == "triangle":
			touch = UnitTestTouch(*charb.center)
			touch.pos = charb.center
			assert charb.dispatch("on_touch_down", touch)
			advance_frames(5)
			charb.dispatch("on_touch_up", touch)
			idle_until(
				lambda: charb.state == "down",
				10,
				"Button press did not work",
			)
			break
	else:
		assert False, 'No button for "triangle" character'
	idle_until(
		lambda: app.chars.ids.charsview.character_name == "triangle",
		100,
		"Never propagated character_name",
	)
	app.chars.toggle()
	idle_until(
		lambda: app.manager.current == "mainscreen",
		100,
		"Didn't switch back to mainscreen",
	)
	idle_until(
		lambda: not app.mainscreen.boardview.board.spot,
		100,
		"Didn't clear out spots, {} left".format(
			len(app.mainscreen.boardview.board.spot)
		),
	)
	app.mainscreen.charmenu.charmenu.toggle_chars_screen()
	idle_until(
		lambda: app.manager.current == "chars",
		100,
		"Never switched to chars",
	)

	for charb in boxl.children:
		if charb.text == "physical":
			touch = UnitTestTouch(*charb.center)
			touch.pos = charb.center
			assert charb.dispatch("on_touch_down", touch)
			advance_frames(5)
			charb.dispatch("on_touch_up", touch)
			idle_until(
				lambda: charb.state == "down",
				10,
				"Button press did not work",
			)
			break
	else:
		assert False, 'No button for "physical" character'
	idle_until(
		lambda: app.chars.ids.charsview.character_name == "physical",
		100,
		"Never propagated character_name",
	)
	app.chars.toggle()
	idle_until(
		lambda: len(app.mainscreen.boardview.board.spot) == physspots,
		100,
		"Never got physical back",
	)
