from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class GestureHandler:
    def __init__(self, driver):
        self.driver = driver
        self.actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))

    # tap(x, y)
    def perform_tap(self, x, y):
        self.actions.pointer_action.move_to_location(x, y).pointer_down().pointer_up()
        self.actions.perform()

    # long_press(x, y, duration)
    def perform_long_press(self, x, y, duration=2):
        self.actions.pointer_action.move_to_location(x, y).pointer_down()
        self.actions.pointer_action.pause(duration)
        self.actions.pointer_action.pointer_up()
        self.actions.perform()

    # swipe(start_x, start_y, end_x, end_y, duration)
    def perform_swipe(self, start_x, start_y, end_x, end_y, duration=1):
        self.actions.pointer_action.move_to_location(start_x, start_y).pointer_down()
        self.actions.pointer_action.move_to_location(end_x, end_y)
        self.actions.pointer_action.pointer_up()
        self.actions.perform()

    # double_tap(x, y)
    def perform_double_tap(self, x, y):
        # First tap
        self.actions.pointer_action.move_to_location(x, y).pointer_down().pointer_up()
        # Second tap
        self.actions.pointer_action.move_to_location(x, y).pointer_down().pointer_up()
        self.actions.perform()

    # pinch_zoom(x, y, zoom_in)
    def perform_pinch_zoom(self, x, y, zoom_in=True):
        if zoom_in:
            # Zoom-in (손가락을 중앙에서 바깥으로 이동)
            self.actions.pointer_action.move_to_location(x, y-50).pointer_down()
            self.actions.pointer_action.move_to_location(x, y-100).pointer_up()
            self.actions.pointer_action.move_to_location(x, y+50).pointer_down()
            self.actions.pointer_action.move_to_location(x, y+100).pointer_up()
        else:
            # Zoom-out (손가락을 바깥에서 중앙으로 이동)
            self.actions.pointer_action.move_to_location(x, y-100).pointer_down()
            self.actions.pointer_action.move_to_location(x, y-50).pointer_up()
            self.actions.pointer_action.move_to_location(x, y+100).pointer_down()
            self.actions.pointer_action.move_to_location(x, y+50).pointer_up()
            
        self.actions.perform()