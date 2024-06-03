#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sys

class InteractivePlotPopup:
    def __init__(self, root):
        self.root = root
        self.points = []
        self.labels = []

        # Create a popup window
        self.popup = tk.Toplevel(root)
        self.popup.title("Insane Lipid Grid Generator")
        self.popup.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle window close event

        # Main frame to hold the plot and controls
        main_frame = tk.Frame(self.popup)
        main_frame.pack(fill=tk.BOTH, expand=1)

        # Create the matplotlib figure and axes
        self.fig = Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylim(0, 10)
        self.ax.set_xlim(-5, 5)
        self.ax.set_xlabel('lipidsx', fontweight='bold')
        self.ax.set_ylabel('lipidsz', fontweight='bold')
        self.ax.grid(True)

        # Create the canvas to display the plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Connect the click event
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)

        # Frame for controls on the right
        control_frame = tk.Frame(main_frame)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Resname input
        tk.Label(control_frame, text="Resname:").pack(padx=5, pady=5)
        self.resname_var = tk.StringVar(value='UNK')
        self.resname_entry = ttk.Entry(control_frame, textvariable=self.resname_var)
        self.resname_entry.pack(padx=5, pady=5)

        # Label input
        tk.Label(control_frame, text="Label:").pack(padx=5, pady=5)
        self.label_var = tk.StringVar(value='BEAD')
        self.label_entry = ttk.Entry(control_frame, textvariable=self.label_var)
        self.label_entry.pack(padx=5, pady=5)
        
        # Y-axis max value input
        tk.Label(control_frame, text="Y-axis max:").pack(padx=5, pady=5)
        self.ymax_var = tk.DoubleVar(value=10.0)  # Default y-axis max value
        self.ymax_entry = ttk.Entry(control_frame, textvariable=self.ymax_var)
        self.ymax_entry.pack(padx=5, pady=5)
        self.ymax_entry.bind('<Return>', self.update_ymax)

        # Toggle output format
        self.toggle_var = tk.BooleanVar(value=False)
        self.toggle_button = ttk.Checkbutton(control_frame, text="Toggle COBY output Format", variable=self.toggle_var)
        self.toggle_button.pack(padx=5, pady=5)

        # Button to save points
        self.save_button = ttk.Button(control_frame, text="Write Output", command=self.save_points)
        self.save_button.pack(padx=5, pady=5)
        
        # Button for example case
        self.example_button = ttk.Button(control_frame, text="Example Case", command=self.example_case)
        self.example_button.pack(padx=5, pady=5)
        
        # Button to close the window
        self.close_button = ttk.Button(control_frame, text="Close", command=self.on_close)
        self.close_button.pack(padx=5, pady=5)
        
        # Output widget for displaying points
        self.out = tk.Text(self.popup, height=10, width=50)
        self.out.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Print welcome message
        self.out.insert(tk.END, "Welcome to the Insane Lipid Grid Generator!\n by Luis Borges-Araujo. 2024 @ ENS-Lyon.\n This should help you define the initial lipid grid input used by insane & COBY to create lipid membranes.\n\n 1) Define your lipid resname on the right.\n 2) Bead by bead, following the order in your itp file, input your bead name and place it as you believe them to roughly be.\n Note: Remember that in CG resolution this process only needs to be roughly accurate. Typical location depths of the POPC headgroup, phosphodiester (PO4), lipid glycerol and acyl-chains are displayed. Beads can be moved by dragging. If you made a mistake you can delete a bead by right clicking.\n 3) Tap 'Save points' to get your output. This should be pasted in your insane.py script. COBY input formats are also available, albeit needing a bit of manual adjustment to bead charges.")
        
        # Variables for dragging points
        self.dragging_point = None

        # Draw the shaded regions and labels
        self.draw_shaded_regions()

    def example_case(self):
        self.resname_var.set('POPC')
        self.points = [
            (0, 8), (0, 7), (0, 6), (.5, 6), (0, 5), 
            (0, 4), (0, 3), (0, 2), (1, 5), (1, 4), 
            (1, 3), (1, 2)
        ]
        self.labels = [
            'NC3', 'PO4', 'GL1', 'GL2', 'C1A', 
            'D2A', 'C3A', 'C4A', 'C1B', 'C2B', 
            'C3B', 'C4B'
        ]
        self.update_plot()
        self.save_points()
        
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        x, y = event.xdata, event.ydata
        if event.button == 1:  # Left-click to add/move points
            for i, (px, py) in enumerate(self.points):
                if np.hypot(px - x, py - y) < 0.3:
                    self.dragging_point = i
                    return
            label = self.label_var.get()
            self.points.append((x, y))
            self.labels.append(label)
            self.update_plot()
        elif event.button == 3:  # Right-click to delete points
            for i, (px, py) in enumerate(self.points):
                if np.hypot(px - x, py - y) < 0.3:
                    del self.points[i]
                    del self.labels[i]
                    self.update_plot()
                    return

    def on_motion(self, event):
        if self.dragging_point is not None and event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            self.points[self.dragging_point] = (x, y)
            self.update_plot()

    def on_release(self, event):
        self.dragging_point = None

    def update_plot(self):
        self.ax.clear()
        self.ax.set_ylim(0, self.ymax_var.get())
        self.ax.set_xlim(-5, 5)
        self.ax.set_xlabel('lipidsx', fontweight='bold')
        self.ax.set_ylabel('lipidsz', fontweight='bold')
        self.ax.grid(True)
        self.draw_shaded_regions()
        points_array = np.array(self.points)
        if len(points_array) > 0:
            self.ax.plot(points_array[:, 0], points_array[:, 1], marker='o', linestyle=' ', color="tab:grey", markersize=40, alpha=.2)
            self.ax.plot(points_array[:, 0], points_array[:, 1], 'ro')
            for (x, y), label in zip(self.points, self.labels):
                self.ax.text(x, y, label, fontsize=9, ha='right')
        self.canvas.draw()

    def draw_shaded_regions(self):
        ymax = self.ymax_var.get()
        if ymax < 8.5:
            return  # Avoid drawing regions if ymax is too small

        # Draw shaded regions and lines
        # self.ax.axhline(y=8, color='blue', alpha=0.3, linewidth=2)
        self.ax.axhspan(7.5, 8.5, color='blue', alpha=0.3)
        self.ax.text(-4.5, 8, "Choline Headgroup", color='blue', va='bottom', alpha=0.7)
        
        if ymax >= 7:
            # self.ax.axhline(y=7, color='orange', alpha=0.3, linewidth=2)
            self.ax.axhspan(6.5, 7.5, color='orange', alpha=0.3)
            self.ax.text(-4.5, 7, "PO4", color='darkorange', va='bottom', alpha=0.7)
        
        if ymax >= 6:
            # self.ax.axhline(y=6, color='red', alpha=0.3, linewidth=2)
            self.ax.axhspan(5.5, 6.5, color='red', alpha=0.3)

            self.ax.text(-4.5, 6, "Glycerol Region", color='red', va='bottom', alpha=0.7)
        
        if ymax >= 5:
            self.ax.axhspan(0, 5.5, color='grey', alpha=0.3)
            self.ax.text(-4.5, 2.5, "Acyl-chains", color='black', va='center', alpha=0.7)
            
    def update_ymax(self, event=None):
        self.update_plot()

    def save_points(self):
        self.out.delete('1.0', tk.END)
        points_array = np.array(self.points)
        
        lipidsx = points_array[:, 0]
        lipidsy = np.zeros_like(lipidsx)
        lipidsz = points_array[:, 1]
        
        resname = self.resname_var.get() or "UNK"
        
        # Format with single decimal point
        lipidsx_str = ', '.join(f'{x:.1f}' for x in lipidsx)
        lipidsy_str = ', '.join(f'{y:.1f}' for y in lipidsy)
        lipidsz_str = ', '.join(f'{z:.1f}' for z in lipidsz)

        if self.toggle_var.get():
            outlist = ["## COBY format output\n",
                   f"""lipid_type, params = "{resname}", "default"\n""",
                        "lipid_defs[(lipid_type, params)] = {}\n",
                        f"""lipid_defs[(lipid_type, params)]["x"] = ({lipidsx_str})\n""",
                        f"""lipid_defs[(lipid_type, params)]["y"] = ({lipidsy_str})\n""",
                        f"""lipid_defs[(lipid_type, params)]["z"] = ({lipidsz_str})\n""",
                        """lipid_defs[(lipid_type, params)]["center"] = 6 # CP\n""",
                            
                        """lipid_defs[(lipid_type, params)]["bd"] = (0.25, 0.25, 0.3)\n""",
                        """lipid_defs[(lipid_type, params)]["charges"] = () ### WARNING: Needs to be manually defined... could be something like this: (("NC3", 1), ("PO4", -1))\n""",
                        """lipid_defs[(lipid_type, params)]["lipids"] =  #   {""" + ', '.join(map(str, range(len(self.labels))))+"""\n""",
                        f"""    ("{resname}", "beads"): ({' '.join(self.labels)}),\n""",
                        "}\n" ]         
            output=''.join(outlist)
        else:
            output = f"""## Insane format output 
moltype = "{resname}"
lipidsx[moltype] = ({lipidsx_str})
lipidsy[moltype] = ({lipidsy_str})
lipidsz[moltype] = ({lipidsz_str})
lipidsa.update({{       #   {', '.join(map(str, range(len(self.labels))))}
    "{resname}": (moltype, "   {' '.join(self.labels)}  "),
}})"""

        self.out.insert(tk.END, output)

    def on_close(self):
        self.root.quit()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    # Create the main application window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    app = InteractivePlotPopup(root)
    root.mainloop()
