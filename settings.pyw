import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code'))

from display_support import configure_tk_scaling, enable_process_dpi_awareness, scale_pixels

enable_process_dpi_awareness()

from tkinter import *
import tkinter as tk
from tkinter import ttk
import configparser
import traceback
import psutil
from contextlib import suppress
import re

try:

    window = tk.Tk()
    ui_scale = configure_tk_scaling(window)

    def px(value):
        return scale_pixels(value, ui_scale)

    window.title("Settings")
    bg_color = "#171c21"
    panel_color = "#222a31"
    field_color = "#192127"
    border_color = "#39454d"
    text_color = "#e8edf0"
    muted_color = "#a1adb5"
    accent_color = "#e2ad4b"
    body_font = ("Segoe UI", 10)
    section_font = ("Segoe UI", 10, "bold")
    title_font = ("Segoe UI", 17, "bold")
    window.configure(bg=bg_color)
    window.option_add("*Frame.background", panel_color)
    window.option_add("*Label.background", panel_color)
    window.option_add("*Label.foreground", text_color)
    window.option_add("*Radiobutton.background", panel_color)
    window.option_add("*Radiobutton.foreground", text_color)
    window.option_add("*Radiobutton.activeBackground", panel_color)
    window.option_add("*Radiobutton.selectColor", field_color)
    window.option_add("*Checkbutton.background", panel_color)
    window.option_add("*Checkbutton.foreground", text_color)
    window.option_add("*Checkbutton.activeBackground", panel_color)
    window.option_add("*Checkbutton.selectColor", field_color)
    window.option_add("*Entry.background", field_color)
    window.option_add("*Entry.foreground", text_color)
    window.option_add("*Entry.insertBackground", accent_color)
    window.option_add("*Entry.relief", "flat")
    window.option_add("*Entry.borderWidth", 0)
    window.option_add("*Entry.highlightThickness", px(1))
    window.option_add("*Entry.highlightBackground", border_color)
    window.option_add("*Entry.highlightColor", accent_color)
    window.option_add("*Entry.justify", tk.CENTER)

    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure(
        "Settings.TCombobox",
        fieldbackground=field_color,
        background=panel_color,
        foreground=text_color,
        arrowcolor=accent_color,
        bordercolor=border_color,
        padding=(px(8), px(5)),
        font=body_font,
    )
    style.configure(
        "Settings.TCheckbutton",
        background=panel_color,
        foreground=text_color,
        indicatorbackground=field_color,
        indicatorsize=px(14),
        indicatormargin=px(4),
        padding=(px(5), px(6)),
        font=body_font,
    )
    style.map(
        "Settings.TCheckbutton",
        background=[("active", panel_color)],
        indicatorbackground=[("selected", accent_color), ("!selected", field_color)],
    )
    style.map(
        "Settings.TCombobox",
        fieldbackground=[("readonly", field_color)],
        foreground=[("readonly", text_color)],
        selectbackground=[("readonly", field_color)],
        selectforeground=[("readonly", text_color)],
    )

    header = tk.Frame(window, bg=bg_color)
    header.pack(fill=tk.X, padx=px(18), pady=(px(14), px(7)))
    tk.Label(header, text="MAP MARKER FINDER", font=section_font, fg=accent_color, bg=bg_color).pack(anchor=tk.W)
    tk.Label(header, text="Settings", font=title_font, fg=text_color, bg=bg_color).pack(anchor=tk.W, pady=(px(1), 0))
    tk.Frame(window, bg=border_color, height=px(1)).pack(fill=tk.X, padx=px(18), pady=(0, px(5)))

    # Создается новая рамка `frm_form` для ярлыков с текстом и
    # Однострочных полей для ввода информации об адресе.
    frm_form = tk.Frame(bg=panel_color, relief=tk.FLAT, borderwidth=0, padx=px(12), pady=px(8))
    # Помещает рамку на окно приложения.
    frm_form.pack(anchor=W, padx=px(12), pady=(px(12), px(6)))

    settings_form = tk.Frame(bg=bg_color)
    settings_form.pack(anchor=W, padx=px(6), pady=px(4))
    
    resolution_form = tk.Frame(master=settings_form, bg=panel_color, relief=tk.FLAT, borderwidth=0, padx=px(12), pady=px(10), highlightthickness=px(1), highlightbackground=border_color)
    resolution_form.grid(row=0, column=0, sticky='n', padx=px(6), pady=px(6))
    
    distance_form = tk.Frame(master=settings_form, bg=panel_color, relief=tk.FLAT, borderwidth=0, padx=px(12), pady=px(10), highlightthickness=px(1), highlightbackground=border_color)
    distance_form.grid(row=0, column=1, sticky='n', padx=px(6), pady=px(6))

    scale_form = tk.Frame(master=settings_form, bg=panel_color, relief=tk.FLAT, borderwidth=0, padx=px(12), pady=px(10), highlightthickness=px(1), highlightbackground=border_color)
    scale_form.grid(row=0, column=2, sticky='n', padx=px(6), pady=px(6))   
    # List of field labels.
    labels = [
        "Distance measurement",
        "Scale setting",
        "Distance measurement (mouse)",
        "Scale setting (mouse)",
    ]

    def read_config(name):
        try:
            config = configparser.ConfigParser()
            config.read(name, encoding='utf-8')
            conf = {}
            conf['distance_measurement'] = config.get("Combinations", "Distance measurement")
            conf['scale_setting'] = config.get("Combinations", "Scale setting")
            conf['distance_measurement_mouse'] = config.get("Combinations", "Distance measurement mouse")
            conf['scale_setting_mouse'] = config.get("Combinations", "Scale setting mouse")
            conf['resolution'] = config.get("Combinations", "Resolution")
            conf['print_x'] = config.get("Combinations", "print_x")
            conf['print_y'] = config.get("Combinations", "print_y")
            conf['print_time'] = config.get("Combinations", "print_time")
            conf['print_distance'] = config.get("Combinations", "print_distance")
            conf['print_azimuth'] = config.get("Combinations", "print_azimuth")
            conf['print_transparent'] = config.get("Combinations", "print_transparent")
            conf['scale_x'] = config.get("Combinations", "scale_x")
            conf['scale_y'] = config.get("Combinations", "scale_y")
            
            return conf
            
        except Exception as e:
            file = open('error.log', 'a')
            file.write('\n\n')
            traceback.print_exc(file=file, chain=True)
            traceback.print_exc()
            file.close()        

    def terminateSignals():
        
        file = open('code/pid.txt', 'a+')
        file.seek(0)
        pid = file.read()
        file.close()  
        
        file = open('code/pid1.txt', 'a+')
        file.seek(0)
        pid1 = file.read()
        file.close() 

        file = open('code/pid3.txt', 'a+')
        file.seek(0)
        pid3 = file.read()
        file.close() 
        
        file = open('code/pid5.txt', 'a+')
        file.seek(0)
        pid5 = file.read()
        file.close()                                           
        
        if pid1 == "":
            pid1 = "0"
        
        if pid3 == "":
            pid3 = "0" 
            
        if pid5 == "":
            pid5 = "0"                       
        
        processes = []
        processes.append(int(pid1))
        processes.append(int(pid3))
        processes.append(int(pid5))    
        
        for process in processes:
            
            with suppress(psutil.NoSuchProcess, ProcessLookupError):
                
                process = psutil.Process(process)

                if process.name() == 'python.exe':
                    cmdline = process.cmdline()
                    
                    for cmdAttr in cmdline:
                        regexp = r'parent_pid=' + pid + r','
                        result = re.search(regexp, cmdAttr)
                        if result != None:
                            process.terminate()
                            break  
                            
    
    def write_config():
        try:
            config = configparser.ConfigParser()
            config.add_section("Combinations")
            config.set("Combinations", "Distance measurement", frm_form.winfo_children()[1].get())
            config.set("Combinations", "Scale setting", frm_form.winfo_children()[3].get())
            config.set("Combinations", "Distance measurement mouse", frm_form.winfo_children()[5].get())
            config.set("Combinations", "Scale setting mouse", frm_form.winfo_children()[7].get())
            config.set("Combinations", "Resolution", resolution_values[resolution_selector.get()])
            config.set("Combinations", "print_x", entry_print_x.get())
            config.set("Combinations", "print_y", entry_print_y.get())
            config.set("Combinations", "print_time", entry_print_time.get())
            config.set("Combinations", "print_distance", str(print_distance.get()))
            config.set("Combinations", "print_azimuth", str(print_azimuth.get()))
            config.set("Combinations", "print_transparent", str(print_transparent.get()))
            config.set("Combinations", "scale_x", entry_scale_x.get())
            config.set("Combinations", "scale_y", entry_scale_y.get())            
            
            with open('code/buttons.ini', "w", encoding="utf-8") as file:
                config.write(file)
            
            terminateSignals()
            
            window.destroy()        
                
        except Exception as e:
            file = open('error.log', 'a')
            file.write('\n\n')
            traceback.print_exc(file=file, chain=True)
            traceback.print_exc()
            file.close()
            
    def default():
        try:
            frm_form.winfo_children()[1].delete(0, END)
            frm_form.winfo_children()[1].insert(0, 't')
            
            frm_form.winfo_children()[3].delete(0, END)
            frm_form.winfo_children()[3].insert(0, '<ctrl>+n')
            
            frm_form.winfo_children()[5].delete(0, END)
            frm_form.winfo_children()[5].insert(0, '')
            
            frm_form.winfo_children()[7].delete(0, END)
            frm_form.winfo_children()[7].insert(0, '')
            
            resolution_selector.set(resolution_labels["3"])
            print_distance.set('1')
            print_azimuth.set('1')
            print_transparent.set('1')
            
            entry_print_x.delete(0, END)
            entry_print_x.insert(0, '15')
            
            entry_print_y.delete(0, END)
            entry_print_y.insert(0, '15')
            
            entry_print_time.delete(0, END)
            entry_print_time.insert(0, '7')            
            
            entry_scale_x.delete(0, END)
            entry_scale_x.insert(0, '15')
            
            entry_scale_y.delete(0, END)
            entry_scale_y.insert(0, '71')            
                
        except Exception as e:
            file = open('error.log', 'a')
            file.write('\n\n')
            traceback.print_exc(file=file, chain=True)
            traceback.print_exc()
            file.close()
            
            
    conf = read_config("code/buttons.ini")

    # Цикл для списка ярлыков полей.
    for idx, text in enumerate(labels):
        # Создает ярлык с текстом из списка ярлыков.
        label = tk.Label(master=frm_form, text=text, font=body_font)
        # Создает текстовое поле которая соответствует ярлыку.
        entry = tk.Entry(master=frm_form, width=28, font=body_font)
        # Использует менеджер геометрии grid для размещения ярлыков и
        # текстовых полей в строку, чей индекс равен idx.
        label.grid(row=idx, column=0, sticky="e", padx=(0, px(8)), pady=px(5))
        entry.grid(row=idx, column=1, padx=px(4), pady=px(4), ipadx=px(5), ipady=px(4))

    frm_form.winfo_children()[1].insert(0, conf['distance_measurement'])
    frm_form.winfo_children()[3].insert(0, conf['scale_setting'])
    frm_form.winfo_children()[5].insert(0, conf['distance_measurement_mouse'])
    frm_form.winfo_children()[7].insert(0, conf['scale_setting_mouse'])

    resolution = conf['resolution'] or "3"
    label_header_resolution = tk.Label(master=resolution_form, text="RESOLUTION", font=section_font, fg=accent_color)
    label_header_resolution.grid(row=0, column=0, columnspan=3, sticky=W, pady=(0, px(7)))

    resolution_options = (
        ("1366x768", "0"),
        ("1440x900", "1"),
        ("1680x1050", "2"),
        ("1920x1080", "3"),
        ("1920x1200", "4"),
        ("2560x1440", "5"),
        ("3440x1440", "6"),
        ("3840x2160", "7"),
        ("5120x2880", "8"),
    )
    resolution_labels = {value: text for text, value in resolution_options}
    resolution_values = {text: value for text, value in resolution_options}
    resolution_selector = ttk.Combobox(
        master=resolution_form,
        values=tuple(text for text, value in resolution_options),
        state="readonly",
        width=16,
        justify=tk.CENTER,
        style="Settings.TCombobox",
    )
    resolution_selector.set(resolution_labels.get(resolution, resolution_labels["3"]))
    resolution_selector.grid(row=1, column=0, columnspan=3, sticky="ew", pady=px(3))

    distance_form_1 = tk.Frame(master=distance_form)
    distance_form_1.pack(anchor=W)
    distance_form_2 = tk.Frame(master=distance_form)
    distance_form_2.pack(anchor=W)
    distance_form_3 = tk.Frame(master=distance_form)
    distance_form_3.pack(anchor=W)
    distance_form_4 = tk.Frame(master=distance_form)
    distance_form_4.pack(anchor=W) 
    distance_form_5 = tk.Frame(master=distance_form)
    distance_form_5.pack(anchor=W)

    scale_form_1 = tk.Frame(master=scale_form)
    scale_form_1.pack(anchor=W)
    scale_form_2 = tk.Frame(master=scale_form)
    scale_form_2.pack(anchor=W)    
    
    label_header_distance = tk.Label(master=distance_form_1, text="DISTANCE WINDOW", font=section_font, fg=accent_color)
    label_header_distance.pack(anchor=W, pady=(0, px(7)))

    label_print_x = tk.Label(master=distance_form_2, text="X OFFSET", font=body_font, fg=muted_color)
    label_print_x.grid(row=0, column=0, pady=px(5))
    entry_print_x = tk.Entry(master=distance_form_2, width=7, font=body_font)
    entry_print_x.grid(row=0, column=1, padx=px(4), pady=px(4), ipadx=px(5), ipady=px(4))
    entry_print_x.insert(0, conf['print_x'])
    
    label_print_y = tk.Label(master=distance_form_2, text="Y OFFSET", font=body_font, fg=muted_color)
    label_print_y.grid(row=0, column=2, pady=px(5))
    entry_print_y = tk.Entry(master=distance_form_2, width=7, font=body_font)
    entry_print_y.grid(row=0, column=3, padx=px(4), pady=px(4), ipadx=px(5), ipady=px(4))
    entry_print_y.insert(0, conf['print_y'])

    print_distance = IntVar()
    print_distance.set(int(conf['print_distance']))
    checkbutton_print_distance = ttk.Checkbutton(master=distance_form_3, text="Distance", variable=print_distance, cursor="hand2", style="Settings.TCheckbutton")
    checkbutton_print_distance.grid(row=0, column=0, padx=px(4), pady=px(3), sticky=tk.W)
    
    print_azimuth = IntVar()
    print_azimuth.set(int(conf['print_azimuth']))
    checkbutton_print_azimuth = ttk.Checkbutton(master=distance_form_3, text="Azimuth", variable=print_azimuth, cursor="hand2", style="Settings.TCheckbutton")
    checkbutton_print_azimuth.grid(row=0, column=1, padx=px(4), pady=px(3), sticky=tk.W)

    print_transparent = IntVar()
    print_transparent.set(int(conf['print_transparent']))
    checkbutton_print_transparent = ttk.Checkbutton(master=distance_form_4, text="Transparent background", variable=print_transparent, cursor="hand2", style="Settings.TCheckbutton")
    checkbutton_print_transparent.pack(anchor=tk.W, pady=px(5))

    label_print_time = tk.Label(master=distance_form_5, text="DISPLAY TIME", font=body_font, fg=muted_color)
    label_print_time.grid(row=0, column=0, pady=px(5))
    entry_print_time = tk.Entry(master=distance_form_5, width=7, font=body_font)
    entry_print_time.grid(row=0, column=1, padx=px(4), pady=px(4), ipadx=px(5), ipady=px(4))
    entry_print_time.insert(0, conf['print_time'])   


    label_header_scale = tk.Label(master=scale_form_1, text="SCALE WINDOW", font=section_font, fg=accent_color)
    label_header_scale.pack(anchor=W, pady=(0, px(7)))
    
    label_scale_x = tk.Label(master=scale_form_2, text="X", font=body_font, fg=muted_color)
    label_scale_x.grid(row=0, column=0, pady=px(5))
    entry_scale_x = tk.Entry(master=scale_form_2, width=7, font=body_font)
    entry_scale_x.grid(row=0, column=1, padx=px(4), pady=px(4), ipadx=px(5), ipady=px(4)) 
    entry_scale_x.insert(0, conf['scale_x'])    
    
    label_scale_y = tk.Label(master=scale_form_2, text="Y", font=body_font, fg=muted_color)
    label_scale_y.grid(row=0, column=2, pady=px(5))
    entry_scale_y = tk.Entry(master=scale_form_2, width=7, font=body_font)
    entry_scale_y.grid(row=0, column=3, padx=px(4), pady=px(4), ipadx=px(5), ipady=px(4)) 
    entry_scale_y.insert(0, conf['scale_y'])     
    
    
    # Создает новую рамку `frm_buttons` для размещения в ней
    # кнопок "Отправить" и "Очистить". Данная рамка заполняет
    # все окно в горизонтальном направлении с
    # отступами в 5 пикселей горизонтально и вертикально.
    frm_buttons = tk.Frame(bg=bg_color)
    frm_buttons.pack(fill=tk.X, ipadx=px(5), ipady=px(5), padx=px(12), pady=(px(4), px(12)))
     
    # Создает кнопку "Отправить" и размещает ее
    # справа от рамки `frm_buttons`.

    btn_submit = tk.Button(master=frm_buttons, text="Default", command=default, font=section_font, bg=panel_color, fg=text_color, activebackground=border_color, activeforeground=text_color, relief=tk.FLAT, borderwidth=0, cursor="hand2")
    btn_submit.pack(side=tk.LEFT, padx=px(6), ipadx=px(10), ipady=px(5))

    btn_submit = tk.Button(master=frm_buttons, text="Apply", command=write_config, font=section_font, bg=accent_color, fg=bg_color, activebackground="#f0c46a", activeforeground=bg_color, relief=tk.FLAT, borderwidth=0, cursor="hand2")
    btn_submit.pack(side=tk.RIGHT, padx=px(6), ipadx=px(10), ipady=px(5))

    window.update_idletasks()
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()
    x = (window.winfo_screenwidth() - window_width) // 2
    y = (window.winfo_screenheight() - window_height) // 2
    window.geometry(f"+{x}+{y}")
    window.mainloop()
    
except Exception as e:
    file = open('error.log', 'a')
    file.write('\n\n')
    traceback.print_exc(file=file, chain=True)
    traceback.print_exc()
    file.close()    