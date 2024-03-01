#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 21:24:04 2024

@author: szabi
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class Interactive3DCurve:
    def __init__(self, fig, ax, x, y, z):
        self.ax = ax
        self.x = x
        self.y = y
        self.z = z
        self.selected_point = None
        self.curve, = ax.plot(self.x, self.y, self.z, 'o-', picker=5)  # 5 points tolerance for picking
        self.cidpick = fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.cidkey = fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_pick(self, event):
        if event.artist == self.curve:
            N = len(event.ind)
            if not N: return True
            
            # For simplicity, pick the first of the selected points
            self.selected_point = event.ind[0]
            print(f"Selected point {self.selected_point} at position ({self.x[self.selected_point]}, {self.y[self.selected_point]}, {self.z[self.selected_point]})")

    def on_key(self, event):
        if self.selected_point is None: return
        if event.key == 'up':
            self.y[self.selected_point] += 0.01  # Move the point up
        elif event.key == 'down':
            self.y[self.selected_point] -= 0.01  # Move the point down
        elif event.key == 'left':
            self.x[self.selected_point] -= 0.01  # Move the point up
        elif event.key == 'right':
            self.x[self.selected_point] += 0.01  # Move the point up
        elif event.key == 'a':
             self.z[self.selected_point] += 0.01  # Move the point up
        elif event.key == 'y':
             self.z[self.selected_point] -= 0.01  # Move the point up
        else:
            return
        self.update_curve()

    def update_curve(self):
        self.curve.set_data_3d(self.x, self.y, self.z)
        plt.draw()

# # Initial 3D curve data
# x = np.linspace(0, 1, 10)
# y = np.sin(x * 2 * np.pi)
# z = np.cos(x * 2 * np.pi)

# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.set_title('Use mouse to select a point and keyboard arrows to move it up/down')

# interactive_curve = Interactive3DCurve(ax, fig, x, y, z)

# plt.show()