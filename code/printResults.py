from display_support import (
    configure_tk_scaling,
    enable_process_dpi_awareness,
    find_game_client_rect,
    scale_pixels,
)

enable_process_dpi_awareness()

from tkinter import *
#import time
#import os
#import signal
#import asyncio   
#from threading import Timer             
import win32api, win32con, pywintypes
import traceback
import configparser
from queue import Empty
#import pdb


def drawLines(queue1, conf, root, label1, label2, waiting1, waiting2, dpi_scale=1.0):
    
    try:

        msg = 0

        client_rect = find_game_client_rect()
        if client_rect is None:
            x = scale_pixels(int(conf['print_x']), dpi_scale)
            y = scale_pixels(int(conf['print_y']), dpi_scale)
        else:
            x = client_rect[0] + scale_pixels(int(conf['print_x']), dpi_scale)
            y = client_rect[1] + scale_pixels(int(conf['print_y']), dpi_scale)
        if (root.winfo_x(), root.winfo_y()) != (x, y):
            root.geometry(f"+{x}+{y}")
        
        while True:
            try:
                msg = queue1.get_nowait()
            except Empty:
                break

            
            if msg[0] == 'clear':
                if waiting1 is not None:
                    root.after_cancel(waiting1)
                    waiting1 = None 
                    label1.pack_forget()
                if waiting2 is not None:
                    root.after_cancel(waiting2)
                    waiting2 = None 
                    label2.pack_forget()
            elif msg[0] == 'printResults':
                distance = msg[1]
                angel = msg[2]
                text1 = f'Dist: {distance}'
                text2 = f'Azimuth: {angel}'
                
                if conf['print_distance'] == "1":
                    label1['text'] = text1
                    label1.pack(anchor="nw", padx=scale_pixels(5, dpi_scale))
                    if waiting1 is not None:
                        root.after_cancel(waiting1)
                    waiting1 = root.after(int(float(conf['print_time'])*1000), lambda: label1.pack_forget()) 
                if conf['print_azimuth'] == "1":
                    label2['text'] = text2
                    label2.pack(anchor="nw", padx=scale_pixels(5, dpi_scale))
                    if waiting2 is not None:
                        root.after_cancel(waiting2)
                    waiting2 = root.after(int(float(conf['print_time'])*1000), lambda: label2.pack_forget())  
 
            elif msg[0] == 'errorArrow':
                
                text1 = 'your tank\nnot found'
                label1['text'] = text1
                label1.pack(padx=5)
                if waiting1 is not None:
                    root.after_cancel(waiting1)
                waiting1 = root.after(int(float(conf['print_time'])*1000), lambda: label1.pack_forget()) 
 
            elif msg[0] == 'errorMarker':
                
                text1 = 'marker\nnot found'
                label1['text'] = text1
                label1.pack(padx=5)
                if waiting1 is not None:
                    root.after_cancel(waiting1)
                waiting1 = root.after(int(float(conf['print_time'])*1000), lambda: label1.pack_forget()) 

            elif msg[0] == 'errorGameWindow':
                label1['text'] = 'War Thunder\nwindow not found'
                label1.pack(padx=scale_pixels(5, dpi_scale))
                if waiting1 is not None:
                    root.after_cancel(waiting1)
                waiting1 = root.after(int(float(conf['print_time'])*1000), lambda: label1.pack_forget())

            elif msg[0] == 'errorResolution':
                label1['text'] = 'Game resolution\nmismatch'
                label1.pack(padx=scale_pixels(5, dpi_scale))
                if waiting1 is not None:
                    root.after_cancel(waiting1)
                waiting1 = root.after(int(float(conf['print_time'])*1000), lambda: label1.pack_forget())
        
        root.after(15, drawLines, queue1, conf, root, label1, label2, waiting1, waiting2, dpi_scale)
        
    except Exception as e:
        file = open('error.log', 'a')
        file.write('\n\n')
        traceback.print_exc(file=file, chain=True)
        traceback.print_exc()
        file.close() 

def printResults(queue1):
    
    try:

        def read_config(name):
            config = configparser.ConfigParser()
            config.read(name, encoding='utf-8')
            conf = {}
            conf['print_x'] = config.get("Combinations", "print_x")
            conf['print_y'] = config.get("Combinations", "print_y")
            conf['print_distance'] = config.get("Combinations", "print_distance")
            conf['print_azimuth'] = config.get("Combinations", "print_azimuth")
            conf['print_transparent'] = config.get("Combinations", "print_transparent")
            conf['print_time'] = config.get("Combinations", "print_time")
            return conf
        conf = read_config("code/buttons.ini")
        
        root = Tk()
        dpi_scale = configure_tk_scaling(root)
        
        bg = ""
        fg = ""
        if conf['print_transparent'] == "1":
            bg = 'white'
            fg = 'yellow'
        else:
            bg = 'yellow'
            fg = 'black'        
        
        root.geometry("+0+0")
        root.configure(bg = bg)
        label1 = Label(root, text='', font=('Roboto','19'), fg=fg, bg=bg)
        label2 = Label(root, text='', font=('Roboto','19'), fg=fg, bg=bg)
        root.overrideredirect(True)
        root.lift()
        root.wm_attributes("-topmost", True)
        root.wm_attributes("-disabled", True)
        if conf['print_transparent'] == "1":
            root.wm_attributes("-transparentcolor", bg)        
        hWindow = pywintypes.HANDLE(int(root.frame(), 16)) 
        exStyle = win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TRANSPARENT
        win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)  

        waiting1 = None
        waiting2 = None
        
        root.after(0, drawLines, queue1, conf, root, label1, label2, waiting1, waiting2, dpi_scale)
        root.mainloop()     
        
        ######################################################################
    except Exception as e:
        file = open('error.log', 'a')
        file.write('\n\n')
        traceback.print_exc(file=file, chain=True)
        traceback.print_exc()
        file.close()