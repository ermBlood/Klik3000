import sys, os, signal, time, mss, numpy, cv2
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
POS_MODE = "AUTO"
INTERVAL_MODE = "AUTO"

ARROW_POS = None


def look_for_stop():
    if STOP_ALL.is_set():
        exit()
    if STOP_LOOP.is_set():
        return True


def loop_click(pos_and_scale, interval):
    if pos_and_scale == None:
        return
    pos, scale = pos_and_scale

    global MODE
    MODE = "loop"
    STOP_LOOP.clear()
    
    while True:
        for i in range(interval):
            time.sleep(1)
            if look_for_stop():
                return
            time.sleep(.1)
            if POS_MODE == "AUTO" and not is_arrow_still_there(pos, scale):
                print("Tlačítko nenalezeno")
                return
            while is_waiting_bar() == True:
                time.sleep(.1)
        
        if look_for_stop():
            return
        print("klik")
        mouse.position = pos
        mouse.click(Button.left)
        time.sleep(0.1)
        print("Čekám")


def do_repeat():
    global STOP_LOOP
    STOP_LOOP.clear()
    global MODE
    MODE = "get_input"
    global POS_MODE
    POS_MODE = "AUTO"
    global SCALE
    SCALE = None

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
    global INTERVAL_MODE
    if INTERVAL_MODE == "MANUAL":
 
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

    if INTERVAL_MODE == "AUTO":
        return 1


def get_pos_manual():
    global MODE
    MODE = "loop"
    global POS_MODE
    POS_MODE = "MANUAL"
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


def get_arrow_pos():
    arrow = cv2.imread("arrow.png")
    w = arrow.shape[1]
    h = arrow.shape[0]
    scale_list = [1, 1.2, 1.4, 1.6, .8, 1.8, 2]
    
    #search arrow with different scale
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[0])
        screen = numpy.array(screenshot)
        screen = screen[:, :, :3]

        # cv2.imshow("lol", screen)
        # cv2.waitKey(0)

        for i in scale_list:
            resized_arrow = cv2.resize(arrow, (int(w*i), int(h*i)))
            screen_match = cv2.matchTemplate(screen, resized_arrow, cv2.TM_CCOEFF_NORMED)
            screen_result = cv2.minMaxLoc(screen_match)

            if screen_result[1] > .7:
                scale = i
                arrow_x = int(screen_result[3][0] + resized_arrow.shape[1]/2)
                arrow_y = int(screen_result[3][1] + resized_arrow.shape[0]/2)
                screen_arrow_pos = (arrow_x, arrow_y)
                print(f"Pozice tlačítka je {screen_arrow_pos}")
                global ARROW_POS
                ARROW_POS = screen_arrow_pos
                return screen_arrow_pos, scale
                    
        global MODE
        MODE = "get_input"
        clear_input()
        manual = input("Tlačítko nenalezeno, vybrat manuálně? Y/N: ")
        if manual.lower().strip() in ["y", "yes", "ano", "yy", "kk", "k", "yup", "j", "jj"]:
            return get_pos_manual(), 1
        elif manual.lower().strip() in ["n", "nn", "no", "nope", "ne"]:
            return


def is_arrow_still_there(pos, scale):
    arrow = cv2.imread("arrow.png")
    w = arrow.shape[1]
    h = arrow.shape[0]
    resized_arrow = cv2.resize(arrow, (int(w*scale), int(h*scale)))

    with mss.mss() as sct:
        screenshot = sct.grab({"left": int(pos[0]-(resized_arrow.shape[1]/2)), "top": int(pos[1]-(resized_arrow.shape[0]/2)), "width": resized_arrow.shape[1], "height": resized_arrow.shape[0]})
        screen = numpy.array(screenshot)
        screen = screen[:, :, :3]
        # cv2.imshow("lol", screen)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows() 
        screen_result = cv2.matchTemplate(screen, resized_arrow, cv2.TM_CCOEFF_NORMED)
        screen_match = cv2.minMaxLoc(screen_result)

        return screen_match[1] > .7


def is_waiting_bar():
    global ARROW_POS
    if ARROW_POS == None:
        return False
    x, y = ARROW_POS

    time.sleep(.5)
 
    with mss.mss() as sct:
        screenshot = sct.grab({"left": x-150, "top": y, "width": 150, "height": 30})
        screen = numpy.array(screenshot)
        screen = screen[:, :, :3]

        # cv2.imshow("lol", screen)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        time.sleep(.5)

        with mss.mss() as sct2:
            screenshot2 = sct2.grab({"left": x-150, "top": y, "width": 150, "height": 30})
            screen2 = numpy.array(screenshot2)
            screen2 = screen2[:, :, :3]

            # cv2.imshow("lo2l", screen2)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            diff = cv2.absdiff(screen, screen2)
            if diff.mean() == 0:
                return False
            else:
                if look_for_stop():
                    return False
                print("Čekám na bar")
                return True


def main():

    keyboard_listener()
    print("\nVítej v utilitě Klik3000\n")

    while not STOP_ALL.is_set():
        loop_click(get_arrow_pos(), get_interval())
        do_repeat()

main()