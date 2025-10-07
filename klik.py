import time
import sys, os, signal
from threading import Event
from pynput.mouse import Button, Controller as MouseController, Listener as mouseListener
from pynput.keyboard import Key, Controller as KeyboardController, Listener as keyboardListener

if sys.platform.startswith("win"):
    import msvcrt
    platform = "win"
else: 
    import termios
    platform = "unix"

mouse = MouseController()
keyboard = KeyboardController()

STOP_ALL = Event()
STOP_LOOP = Event()
MODE = "get_input"



def loop_click(interval, pos):
    if pos == None:
        return

    global MODE
    MODE = "loop"
    STOP_LOOP.clear()
    
    while True:
        for i in range(interval):
            time.sleep(1)
            if STOP_ALL.is_set():
                exit()
            if STOP_LOOP.is_set():
                STOP_LOOP.clear()
                return
            
        print("klik")
        mouse.position = pos
        mouse.click(Button.left)
        time.sleep(0.1)
        print("Čekám")


def do_repeat():
    global MODE
    MODE = "get_input"
    while True:
        clear_input()
        repeat = input("\nSpustit znova? Y/N: ")
        if repeat.lower().strip() in ["y", "yes", "ano", "yy", "kk", "k", "yup", "j", "jj"]:
            break
        elif repeat.lower().strip() in ["n", "nn", "no", "nope", "ne"]:
            exit()
        else: pass


def exit():
    print("\nUkončuji")
    os._exit(0)


def get_interval():
    global MODE
    while True:
        clear_input()
        MODE = "get_input"
        interval = input("Zadej interval kliků (v sekundách, rozmezí 1-99): ")
        try:
            interval = round(float(interval))
            if 0 < interval < 100:
                return interval
            else:
                print("..erm, celé číslo v rozmezí od nuly, do devadesáti-devíti :)")
        except:
            print("Číslo, ty jelito")


def get_pos():
    global MODE
    MODE = "loop"
    print(f"Klikni na požadované místo klikání")
    pos = ()

    def on_click(x: int, y: int, button: Button, pressed: bool):
        nonlocal pos
        if pressed:
            pos = (x, y)
            print(f"souřadnice jsou {pos}")

        return False

    listener = mouseListener(on_click = on_click)
    listener.start()    
    while listener.is_alive():
        if STOP_ALL.is_set():
            exit()
        if STOP_LOOP.is_set():
            listener.stop()
            STOP_LOOP.clear()
            return None
        time.sleep(.25)

    return pos


def keyboard_listener():

    def on_key_press(key):
        if key == Key.esc:
            STOP_ALL.set()
            exit()

        if MODE == "loop":
            print("\nZmáčknul jsi klávesu, Klik3000 přerušen")
            STOP_LOOP.set()
        
        if MODE == "get_input":
            return

    listen_keyboard = keyboardListener(on_press = on_key_press, suppress = False)
    listen_keyboard.start()


def clear_input():
    if platform == "win":
        while msvcrt.kbhit():
            msvcrt.getch()
    else: termios.tcflush(sys.stdin, termios.TCIFLUSH)


def main():

    keyboard_listener()
    print("\nVítej v utilitě Klik3000\n")

    while not STOP_ALL.is_set():
        loop_click(get_interval(), get_pos())
        do_repeat()

main()