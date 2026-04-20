import keyboard

STOP_FLAG = False


def start_listener():
    global STOP_FLAG

    def on_press(event):
        global STOP_FLAG
        if event.name == "esc":
            print("🛑 STOP SIGNAL RECEIVED")
            STOP_FLAG = True

    keyboard.on_press(on_press)
