#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 10:16:43 2023

@author: itqs
"""

from PIL import Image, ImageTk
import tkinter as tk

root = tk.Tk()  # initialize root window
root.title("Avatrainer")  # set window title
# self.destructor function gets fired when the window is closed
#self.root.protocol('WM_DELETE_WINDOW', self.destructor)

root.config(cursor="arrow",bg='lightgray')

test_image=ImageTk.PhotoImage(Image.open(r"../assets/personal_trainer.jpg").resize((640,364)))
rt_panel = tk.Label(image=test_image)
rt_panel.image = test_image#,width=640, height=364)  # initialize image panel
rt_panel.pack(side="right", padx=10, pady=10)