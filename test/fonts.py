#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 10:36:05 2023

@author: itqs
"""

import tkinter as tk
from tkinter import font

# Function to generate frame for displaying fonts in tkinter dialog
def generate_frm(frame):
    row = 1
    for fitem in fonts:
        if fitem != 'Noto Color Emoji':
            tk.Label(frame,
                     font=(fitem, 16, "normal"),
                     text=fitem).grid(row=row, column=1)
            row = row + 1

# Tool dialog configuration
root = tk.Tk()
root.geometry('400x600')
root.title('Font Families with Respective Style')

# Get available font families and sort them
fonts = list(font.families())
fonts.sort()

# Frame creation with scrollbar
canvas = tk.Canvas(root)
frame = tk.Frame(canvas)
scrolbr = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrolbr.set)
scrolbr.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((20,4), window=frame, anchor="nw")
frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))
generate_frm(frame)

root.mainloop()