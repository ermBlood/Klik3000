import time
import sys
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController, Listener

mouse = MouseController()
keyboard = KeyboardController()


def on_key_press(key):
    print("\nZmáčknul jsi klávesu, Klik3000 přerušen")
    return False   # tím řekneš: po první klávese přestaň poslouchat


def loop_click(interval):

    listen_keyboard = Listener(on_press = on_key_press, suppress = True)
    listen_keyboard.start()

    while True:
        print("klik")
        mouse.click(Button.left)

        time.sleep(0.1)

        print("Čekám")
        for i in range(interval):
            time.sleep(1)
            if not listen_keyboard.is_alive():
                return



def repeat():
    while True:
        repeat = input("\nSpustit znova? Y/N: ")
        if repeat.lower().strip() in ["y", "yes", "ano", "yy", "kk", "k", "yup", "j", "jj"]:
            break
        elif repeat.lower().strip() in ["n", "nn", "no", "nope", "ne"]:
            print("\nUkončuji")
            time.sleep(.5)
            sys.exit(0)
        else: pass


def get_interval():

    while True:
        interval = input("Zadej interval kliků (v sekundách, rozmezí 1-99): ")
        try:
            interval = round(float(interval))
            if 0 < interval < 100:
                return interval
            else:
                print("..erm, celé číslo v rozmezí od nuly, do devadesáti-devíti :)")
        except:
            print("Číslo, ty jelito")
    

def main():

    print("\nVítej v utilitě Klik3000\n")

    while True:
                
        loop_click(get_interval())
        repeat()

main()