import functools
import os
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict
from uuid import uuid4

from adb_pywrapper.adb_device import AdbDevice
from adb_pywrapper.adb_screen_recorder import AdbScreenRecorder
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.extensions.android.nativekey import AndroidKey
from appium.webdriver.webdriver import WebDriver
from selenium.common import NoSuchElementException
from urllib3.exceptions import MaxRetryError

from puma.apps.android import logger
from puma.computer_vision import ocr
from puma.utils.video_utils import CACHE_FOLDER, log_error_and_raise_exception

__drivers: dict[str, WebDriver] = {}

def _get_appium_driver(appium_server: str, udid: str, options) -> WebDriver:
    key = f"{appium_server}${udid}"
    if key not in __drivers.keys():
        try:
            __drivers[key] = webdriver.Remote(appium_server, options=options)
        except MaxRetryError:
            logger.error("Connecting to the Appium server has failed.\n"
                  "Make sure that the appium server is running!\n"
                  "This can be done by running the `appium` command from the command line.")
            exit(1)
    else:
        logger.warning(f'WARNING: there already was an initialized driver for appium server {appium_server} and udid {udid}. '
              'This driver will be used, which might mean your appium capabilities are ignored as these cannot be'
              'altered for a driver that has already been initialized. If you need specific capabilities, please '
              'rewrite your Puma code to ensure the correct capabilities are loaded the first time you connect to '
              f'server {appium_server} and device {udid}.')
    return __drivers[key]


def _get_android_default_options():
    options = UiAutomator2Options()
    options.no_reset = True
    options.platform_name = 'Android'
    options.new_command_timeout = 1200
    return options


def supported_version(version: str):
    def decorator(class_or_function):
        class_or_function.supported_version = version
        return class_or_function

    return decorator


class AndroidAppiumActions:

    def __init__(self,
                 udid: str,
                 app_package: str,
                 desired_capabilities: Dict[str, str] = None,
                 implicit_wait: int = 1,
                 appium_server: str = 'http://localhost:4723'):
        """
        Class with a generic API for Appium scripting on an Android device.
        Can be used with an emulator or real device attached to the computer.
        :param desired_capabilities: desired capabilities as passed to the Appium webdriver
        :param implicit_wait: how long Appium will look for an element (you can look for an element before it is
                              rendered). Default 1 second
        :param appium_server: url of the appium server
        """
        # prepare options
        self.options = _get_android_default_options()
        self.options.udid = udid
        self.app_package = app_package
        if desired_capabilities:
            self.options.load_capabilities(desired_capabilities)

        logger.info("Connecting to Appium driver...")
        self.driver = _get_appium_driver(appium_server, udid, self.options)

        # the implicit wait time is how long appium looks for an element (you can try to find an element before it is rendered)
        self.implicit_wait = implicit_wait
        self.driver.implicitly_wait(implicit_wait)
        self.udid = self.driver.capabilities.get("udid")
        self.adb = AdbDevice(self.udid)

        # screen recorder
        self._screen_recorder = None

        logger.info(f"Activating package {self.app_package}...")
        self.activate_app()
        logger.info(f"App package {self.app_package} activated!")

    def activate_app(self):
        self.driver.activate_app(self.app_package)

    def terminate_app(self):
        self.driver.terminate_app(self.app_package)

    def restart_app(self):
        self.terminate_app()
        self.activate_app()

    def app_open(self) -> bool:
        return str(self.driver.current_package) == self.app_package

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._screen_recorder is not None:
            self.stop_recording_and_save_video()
        self.driver.__exit__(exc_type, exc_val, exc_tb)

    def back(self):
        self.driver.press_keycode(AndroidKey.BACK)

    def home(self):
        self.driver.press_keycode(AndroidKey.HOME)

    def open_notifications(self):
        self.driver.open_notifications()

    def scroll_to_find_element(self, resource_id: str = None, text_equals: str = None,
                               text_contains: str = None) -> WebElement:
        """
        This code will scroll in the current view until a certain element is found, and then return that element.
        The element can be searched for by resource-id and/or the text in that element.
        When defining the text of the element either an exact match or a textContains match can be used. These two can
        of course not be used at the same time.
        The method will keep scrolling until the element is found. If you look for something that doesn't exist you
        will have a bad time.
        The first matching element is returned when found.
        :param resource_id: the resource id of the element to look for.
        :param text_equals: the exact text of the element to look for. Cannot be used in combination with text_contains.
        :param text_contains: part of the text of the element to look for. Cannot be used in combination with
        text_equals.
        :return: The element when found.
        """
        if text_equals is not None and text_contains is not None:
            raise ValueError('text_equals and text_contains can not be used at the same time')
        if resource_id is None and text_contains is None and text_equals is None:
            raise ValueError('resource_id, text_equals and text_contains cannot all be None')

        resource_id_part = '' if resource_id is None else f'.resourceIdMatches("{resource_id}")'
        text_part = '' if text_equals is None else f'.text("{text_equals}")'
        text_contains_part = '' if text_contains is None else f'.textContains("{text_contains}")'

        java_code = f'new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollIntoView(new UiSelector(){resource_id_part}{text_part}{text_contains_part}.instance(0))'
        return self.driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value=java_code)

    def swipe_to_find_element(self, xpath: str, max_swipes: int = 10) -> WebElement:
        for attempt in range(max_swipes):
            if self.is_present(xpath):
                return self.driver.find_element(AppiumBy.XPATH, xpath)
            else:
                # Element not found, perform swipe down
                print(f"Attempt {attempt + 1}: Element not found, swiping down")
                # Get the window size to determine the swipe dimensions
                window_size = self.driver.get_window_size()
                start_x = window_size['width'] / 2
                start_y = window_size['height'] * 0.8
                end_y = window_size['height'] * 0.2

                # Perform the swipe down
                self.driver.swipe(start_x, start_y, start_x, end_y, 500)

                # Wait a bit before the next attempt
                time.sleep(0.5)

        # If the loop completes, the element was not found
        raise NoSuchElementException(msg=f'After {max_swipes} swipes, cannot find element with xpath {xpath}')

    def is_present(self, xpath: str, implicit_wait: int = 0) -> bool:
        self.driver.implicitly_wait(implicit_wait)
        found = self.driver.find_elements(by=AppiumBy.XPATH, value=xpath)
        self.driver.implicitly_wait(self.implicit_wait)
        return len(found) > 0

    def start_recording(self, output_directory: str):
        if self._screen_recorder is None:
            self._screen_recorder_output_directory = output_directory
            self._screen_recorder = AdbScreenRecorder(self.adb)
            self._screen_recorder.start_recording()

    def stop_recording_and_save_video(self) -> [str]:
        if self._screen_recorder is None:
            return None
        video_files = self._screen_recorder.stop_recording(self._screen_recorder_output_directory)
        self._screen_recorder.__exit__(None, None, None)
        self._screen_recorder = None
        return video_files

    def new_screenshot_name(self):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        device_name = self.options.device_name
        return Path(CACHE_FOLDER) / f'{now}-{device_name}-{uuid4()}.png'

    def find_text_ocr(self, text_to_find: str) -> [ocr.RecognizedText]:
        path = self.new_screenshot_name()
        screenshot_taken = False
        try:
            screenshot_taken = self.driver.get_screenshot_as_file(path)
            if not screenshot_taken:
                raise Exception(f'Screenshot could not be stored to {path}')
            found_text = ocr.find_text(str(path), text_to_find)
            return found_text
        finally:
            if screenshot_taken:
                os.remove(path)

    def click_text_ocr(self, text_to_click: str, click_first_when_multiple: bool = False):
        found_text = self.find_text_ocr(text_to_click)
        if len(found_text) == 0:
            msg = f'Could not find text {text_to_click} on screen so could not click it'
            log_error_and_raise_exception(logger, msg)
        if len(found_text) > 1:
            msg = f'Found multiple occurrences of text {text_to_click} on screen so could not determine what to click'
            if not click_first_when_multiple:
                log_error_and_raise_exception(logger, msg)
            else:
                logger.warning(f'Found multiple occurrences of text {text_to_click} on screen, clicking first one')
        x = found_text[0].bounding_box.middle[0]
        y = found_text[0].bounding_box.middle[1]
        self.driver.execute_script('mobile: clickGesture', {'x': x, 'y': y})

    def set_idle_timeout(self, timeout: int):
        # https://github.com/appium/appium-uiautomator2-driver#poor-elements-interaction-performance
        # https://github.com/appium/appium-uiautomator2-driver#settings-api
        settings = self.driver.get_settings()
        settings.update({"waitForIdleTimeout": timeout})
        self.driver.update_settings(settings)
