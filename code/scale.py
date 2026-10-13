from display_support import (
    configure_tk_scaling,
    enable_process_dpi_awareness,
    find_game_client_rect,
    calculate_map_scale,
    get_game_capture_region,
    scale_pixels,
)

enable_process_dpi_awareness()

from tkinter import *
import re
import win32gui
import traceback
import configparser
import pyautogui
import cv2

try: 

    def read_config(name):
        config = configparser.ConfigParser()
        config.read(name, encoding='utf-8')
        conf = {}
        conf['scale_x'] = config.get("Combinations", "scale_x")
        conf['scale_y'] = config.get("Combinations", "scale_y")
        conf['resolution'] = config.get("Combinations", "Resolution")
        return conf
    conf = read_config("code/buttons.ini")
    resolution = conf['resolution']

    ######################################################################
    #Создание окна масштаба

    file = open('code/scale.txt', 'r')
    scale = file.read()
    file.close()
    if scale == "" or scale == "0":
        scale = "5"
        file = open('code/scale.txt', 'w')
        file.write(scale)
        file.close()
    scale = round(float(scale), 1)   

    def get_text():
        try:
            res = entry.get()
            if res != "":
                status_label["text"] = ""
                print('')
                client_rect = find_game_client_rect()
                if client_rect is None:
                    status_label["text"] = "Game window not found"
                    return
                try:
                    region = get_game_capture_region(client_rect, resolution)
                except ValueError as error:
                    status_label["text"] = "Resolution mismatch"
                    print(error)
                    return
                screen = pyautogui.screenshot('Map.png', region=region)
                karta = cv2.imread("Map.png")
                
                letter_matches = []
                for grid_position, letter in ((1, 'a'), (5, 'e'), (7, 'g')):
                    template = cv2.imread(f"../data/resolution_{resolution}/{letter}letter.png")
                    if template is None:
                        continue
                    match = cv2.matchTemplate(karta, template, cv2.TM_CCOEFF_NORMED)
                    _, confidence, _, top_left = cv2.minMaxLoc(match)
                    print(f"top_left_corner_letter_{letter}", top_left)
                    letter_matches.append((grid_position, top_left[1], confidence))

                try:
                    scale = calculate_map_scale(letter_matches, int(res))
                except ValueError as error:
                    status_label["text"] = "Could not read map grid"
                    print(error)
                    return
                print(f'map scale {scale}')
                if scale == 0:
                    status_label["text"] = "Could not read map grid"
                    entry.delete(0, END)
                    return 
                if scale > 99:
                    status_label["text"] = "Map grid not recognized"
                    print('failed to recognize letters on the minimap')
                    return  
                file = open('code/scale.txt', 'w')
                file.write(str(scale))
                file.close()
                entry.delete(0, END)
                root.destroy()
        except Exception as e:
            file = open('error.log', 'a')
            file.write('\n\n')
            traceback.print_exc(file=file, chain=True)
            traceback.print_exc()
            file.close()

    def close():
        selectWindow()
        quit()

    def validation(newval):
        try:
            return re.match(r"^\d{0,4}$", newval) is not None
        except Exception as e:
            file = open('error.log', 'a')
            file.write('\n\n')
            traceback.print_exc(file=file, chain=True)
            traceback.print_exc()
            file.close()           

    def selectWindow(event=1):
        try:
            toplist = []
            winlist = []
            def enum_callback(hwnd, results):
                winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

            win32gui.EnumWindows(enum_callback, toplist)
            wt = [(hwnd, title) for hwnd, title in winlist if 'war thunder' in title.lower()]
            # just grab the first window that matches
            if wt !=[]:
                wt = wt[0]
                # use the window handle to set focus
                win32gui.SetForegroundWindow(wt[0])  
        except Exception as e:
            file = open('error.log', 'a')
            file.write('\n\n')
            traceback.print_exc(file=file, chain=True)
            traceback.print_exc()
            file.close()                

    root = Tk()
    ui_scale = configure_tk_scaling(root)
    bg_color = "#171c21"
    panel_color = "#222a31"
    border_color = "#39454d"
    text_color = "#e8edf0"
    muted_color = "#a1adb5"
    accent_color = "#e2ad4b"
    root.configure(bg=bg_color, highlightthickness=1, highlightbackground=border_color)
    root.resizable(False, False)
    geometry = (
        f"{scale_pixels(340, ui_scale)}x{scale_pixels(156, ui_scale)}"
        f"+{scale_pixels(int(conf['scale_x']), ui_scale)}"
        f"+{scale_pixels(int(conf['scale_y']), ui_scale)}"
    )
    root.geometry(geometry)
    root.overrideredirect(True)
    root.lift()
    root.wm_attributes("-topmost", True)

    container = Frame(root, bg=bg_color)
    container.pack(fill=BOTH, expand=True, padx=scale_pixels(12, ui_scale), pady=scale_pixels(9, ui_scale))

    header = Frame(container, bg=bg_color)
    header.pack(fill=X)
    title = Label(header, text="MAP CALIBRATION", font=("Segoe UI", 11, "bold"), fg=text_color, bg=bg_color)
    title.pack(side=LEFT)
    close_button = Button(
        header,
        text="X",
        command=close,
        font=("Segoe UI", 9, "bold"),
        fg=muted_color,
        bg=bg_color,
        activeforeground=text_color,
        activebackground=panel_color,
        relief=FLAT,
        borderwidth=0,
        padx=scale_pixels(7, ui_scale),
        pady=0,
        cursor="hand2",
    )
    close_button.pack(side=RIGHT)

    scale_row = Frame(container, bg=panel_color, padx=scale_pixels(9, ui_scale), pady=scale_pixels(5, ui_scale))
    scale_row.pack(fill=X, pady=(scale_pixels(8, ui_scale), scale_pixels(7, ui_scale)))
    current_label = Label(scale_row, text="CURRENT SCALE", font=("Segoe UI", 8, "bold"), fg=muted_color, bg=panel_color)
    current_label.pack(side=LEFT)
    current_value = Label(scale_row, text=f"{scale:.1f} px/m", font=("Segoe UI", 11, "bold"), fg=accent_color, bg=panel_color)
    current_value.pack(side=RIGHT)

    field_label = Label(container, text="GRID DISTANCE (m)", font=("Segoe UI", 8, "bold"), fg=muted_color, bg=bg_color)
    field_label.pack(anchor=W, pady=(0, scale_pixels(3, ui_scale)))

    check = (root.register(validation), "%P")
    input_row = Frame(container, bg=bg_color)
    input_row.pack(fill=X)
    entry = Entry(
        input_row,
        fg=text_color,
        bg=panel_color,
        insertbackground=accent_color,
        font=("Segoe UI", 12),
        width=8,
        relief=FLAT,
        highlightthickness=1,
        highlightbackground=border_color,
        highlightcolor=accent_color,
        validate="key",
        validatecommand=check,
    )
    entry.pack(side=LEFT, fill=X, expand=True, ipady=scale_pixels(5, ui_scale))
    entry.bind("<Return>", lambda event: get_text())

    calculate_button = Button(
        input_row,
        text="CALCULATE",
        command=get_text,
        font=("Segoe UI", 9, "bold"),
        fg=bg_color,
        bg=accent_color,
        activeforeground=bg_color,
        activebackground="#f0c46a",
        relief=FLAT,
        borderwidth=0,
        padx=scale_pixels(11, ui_scale),
        pady=scale_pixels(7, ui_scale),
        cursor="hand2",
    )
    calculate_button.pack(side=LEFT, padx=(scale_pixels(8, ui_scale), 0))

    status_label = Label(container, text="", font=("Segoe UI", 8), fg=muted_color, bg=bg_color, anchor=W)
    status_label.pack(fill=X, pady=(scale_pixels(5, ui_scale), 0))

    root.after_idle(entry.focus_force)
    
    root.mainloop()
    
    ######################################################################
except Exception as e:
    file = open('error.log', 'a')
    file.write('\n\n')
    traceback.print_exc(file=file, chain=True)
    traceback.print_exc()
    file.close()