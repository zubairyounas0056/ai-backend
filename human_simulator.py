import time
import random
import pyautogui
import pygetwindow as gw


class HumanSimulator:

    def __init__(self):
        pass

    def random_sleep(self, min_s=0.5, max_s=1.5):
        time.sleep(random.uniform(min_s, max_s))

    # 🔥 REAL FIX: Window-based browser focus
    def focus_browser_by_number(self, number):

        # all chrome windows
        windows = [w for w in gw.getWindowsWithTitle("") if w.title]

        # filter browsers (chrome / edge / etc)
        browser_windows = [
            w for w in windows if "Chrome" in w.title or "Edge" in w.title
        ]

        if not browser_windows:
            print("❌ No browser windows found")
            return

        # sort for stability
        browser_windows = sorted(browser_windows, key=lambda w: w.title)

        # select by index
        index = number - 1

        if index >= len(browser_windows):
            print(f"❌ Browser {number} not found")
            return

        window = browser_windows[index]

        try:
            window.activate()
            time.sleep(1)
        except:
            print("❌ Could not focus window")

    # 🔥 REAL HUMAN URL OPEN
    def open_url_human(self, url):

        time.sleep(0.5)

        # focus address bar
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.3)

        # clear text
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)

        # type URL
        pyautogui.typewrite(url, interval=0.03)

        # enter
        pyautogui.press("enter")

        time.sleep(2)

    # clean typing
    def type_like_human(self, text):
        for char in text:
            pyautogui.write(char)
            time.sleep(random.uniform(0.02, 0.05))
