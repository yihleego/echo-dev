import time
from unittest import TestCase

from echo.core.jab import JABDriver, JABLib
from echo.core.uia import UIADriver
from echo.utils import win32


class UIATestSuite(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_event(self):
        from echo.utils.event import listener, Event, Key, run_thread
        jab_lib = JABLib()
        drivers = {}
        pos = [
            (0, 0),
            (0, 0),
        ]

        @listener(Event.KEYUP)
        def on_click(x, y, key):
            if key != Key.f3:
                return
            pos[1] = (x, y)
            print('click', x, y)

        run_thread()

        while True:
            if pos[0] == pos[1]:
                time.sleep(0.3)
                continue
            pos[0] = pos[1]
            x, y = pos[0]
            handle = win32.window_from_point((x, y))
            if not handle:
                return
            if handle not in drivers:
                if jab_lib.isJavaWindow(handle):
                    drivers[handle] = JABDriver(handle)
                else:
                    drivers[handle] = UIADriver(handle)
            driver = drivers[handle]
            if driver:
                print((x, y), driver, driver.__class__)
                elems = driver.find_elements(lambda e: e.rectangle[0] <= x <= e.rectangle[2] and e.rectangle[1] <= y <= e.rectangle[3])
                for elem in elems:
                    print(elem)
                    win32.draw_outline(elem.rectangle, str(elem))
                print()
