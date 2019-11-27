#!/usr/bin/env python3

# Requires Python 3.6 and above

import sys
from os import chdir
from math import pi, sin, cos
from tkinter import *
from tkinter import ttk, filedialog, messagebox
# import threading  # TODO: possibly use
from ezdxf.r12writer import r12writer
from polylabel import polylabel


class MenuBar(Menu):
    def __init__(self, root, close):
        super().__init__()

        self.option_add("*tearOff", FALSE)

        file_menu = Menu(self)
        file_menu.add_command(label="Exit", command=close)

        help_menu = Menu(self)
        help_menu.add_command(label="About",
                              command=lambda: messagebox.showinfo("About", "v0.1"))

        self.add_cascade(menu=file_menu, label="File")
        self.add_cascade(menu=help_menu, label="Help")

        root.config(menu=self)


class Gui(Tk):
    def __init__(self):
        super().__init__()

        self.polygons = []
        self.numPolygons = IntVar()
        self.numPolygons.set(0)
        self.circles = []

        # Settings
        self.outputDXF = IntVar()
        self.outputDXF.set(1)
        self.outputDXFCircle = IntVar()
        self.outputDXFCircle.set(1)
        self.outputDXFDiameter = IntVar()
        self.outputDXFDiameter.set(1)
        self.outputDXFLabel = IntVar()
        self.outputDXFLabel.set(0)
        self.outputDXFPoints = IntVar()
        self.outputDXFPoints.set(0)

        self.outputCircles = IntVar()
        self.outputCircles.set(0)

        self.outputPoints = IntVar()
        self.outputPoints.set(0)
        self.outputPointsNum = StringVar()
        self.outputPointsNum.set("16")

        self.outputFolder = StringVar()
        self.outputFolder.set("./")


        self.title("Maximum Inscribed Circle")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        MenuBar(self, self.quit)

        mainframe = ttk.Frame(self, padding=(3, 3, 0, 0))
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        # Clear focus from text boxes on click
        mainframe.bind("<1>", lambda event: mainframe.focus_set())


        self.initLoad(mainframe, 1)
        mainframe.columnconfigure(1, weight=0, uniform="a")
        self.initSave(mainframe, 2)
        mainframe.columnconfigure(2, weight=0, minsize=15)
        mainframe.columnconfigure(3, weight=1, uniform="a")

    class NumEntry(ttk.Entry):
        # A number validated Entry box
        def __init__(self, length, min_val, max_val, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.length = length
            self.min_val = min_val
            self.max_val = max_val
            self.configure(width=self.length + 1, validate="key",
                           validatecommand=(self.register(self.on_validate), "%P"))

        def on_validate(self, new_value):
            if new_value.strip() == "":
                return True
            try:
                value = int(new_value)
                if value < self.min_val or value > self.max_val or len(str(value)) > self.length:
                    raise ValueError
            except ValueError:
                self.bell()
                return False
            return True

    def initLoad(self, parentFrame, column):
        self.loadButton = ttk.Button(parentFrame, text="Open csv file", command=self.load)
        self.loadButton.grid(column=column, row=4)

        ttk.Label(parentFrame, text="Number of polygons found in the file:")\
            .grid(column=column, row=6, padx=5, pady=0)
        ttk.Label(parentFrame, textvariable=self.numPolygons)\
            .grid(column=column, row=7, padx=5, pady=0)
        # TODO: add picture of polygons and circles?

    def initSave(self, parentFrame, column):
        ttk.Checkbutton(parentFrame, text="Output to DXF", variable=self.outputDXF)\
            .grid(column=column, row=0, columnspan=2, sticky=W, padx=5, pady=(5, 0))
        # TODO: disable these when dxf is unchecked
        ttk.Checkbutton(parentFrame, text="Output Circle in DXF", variable=self.outputDXFCircle)\
            .grid(column=column+1, row=1, sticky=W, padx=5, pady=0)
        ttk.Checkbutton(parentFrame, text="Output Diameter Line in DXF", variable=self.outputDXFDiameter)\
            .grid(column=column+1, row=2, sticky=W, padx=5, pady=0)
        ttk.Checkbutton(parentFrame, text="Output Diameter Label in DXF", variable=self.outputDXFLabel)\
            .grid(column=column+1, row=3, sticky=W, padx=5, pady=0)
        ttk.Checkbutton(parentFrame, text="Output Points in DXF", variable=self.outputDXFPoints)\
            .grid(column=column+1, row=4, sticky=W, padx=5, pady=0)

        ttk.Checkbutton(parentFrame, text="Output to Circles csv", variable=self.outputCircles)\
            .grid(column=column, row=5, columnspan=2, sticky=W, padx=5, pady=5)

        ttk.Checkbutton(parentFrame, text="Output to Points csv", variable=self.outputPoints)\
            .grid(column=column, row=6, columnspan=2, sticky=W, padx=5, pady=5)

        ttk.Label(parentFrame, text="Number of points on circle:")\
            .grid(column=column, row=7, columnspan=2, sticky=W, padx=5, pady=(5, 0))
        # TODO: disable when neither output points in DXF or output points csv are selected
        self.NumEntry(4, 0, 9999, parentFrame, textvariable=self.outputPointsNum)\
            .grid(column=column, row=8, columnspan=2, sticky=W, padx=5, pady=0)

        ttk.Label(parentFrame, text="Output Folder:")\
            .grid(column=column, row=9, columnspan=2, sticky=W, padx=5, pady=(5, 0))
        ttk.Entry(parentFrame, textvariable=self.outputFolder)\
            .grid(column=column, row=10, columnspan=2, sticky=(W, E), padx=5, pady=0)

        self.browseButton = ttk.Button(parentFrame, text="Browse", command=self.browse)
        self.browseButton.grid(column=column, row=14, columnspan=2, padx=5, pady=(5, 0))

        self.saveButton = ttk.Button(parentFrame, text="Save", command=self.save)
        self.saveButton.grid(column=column, row=15, columnspan=2, padx=5, pady=(0, 5))
        self.saveButton.state(["disabled"])

    def load(self):
        # Bound to loadButton
        fileName = filedialog.askopenfilename(filetypes=[("csv files", "*.csv")])
        if not fileName:
            return

        polygons = self.parseData(fileName)
        if not polygons:
            return

        circles = []

        for polygon in polygons:
            # circle is formatted as [[x,y,z],radius]
            circle = list(polylabel(polygon[0], precision=0.001, with_distance=True))
            circle[0].append(sum(polygon[1])/len(polygon[1]))
            circles.append(circle)

        self.polygons = polygons
        self.circles = circles

        self.numPolygons.set(len(polygons))
        self.saveButton.state(["!disabled"])

    def browse(self):
        # Bound to browse_button
        directory = filedialog.askdirectory(mustexist=True)
        if not directory:
            return
        try:
            chdir(directory)
        except OSError as e:
            messagebox.showerror(title="Error", message=repr(e))
            return

        self.outputFolder.set(directory)

    def save(self):
        # Bound to saveButton
        DXFFileName = "circles.dxf"
        CirclesFileName = "circles.csv"
        PointsFileName = "points.csv"

        if not self.outputFolder.get():
            messagebox.showerror(title="Error", message="Output Folder not set")
            return
        if self.outputFolder.get()[-1] != "/":
            self.outputFolder.set(self.outputFolder.get()+"/")

        if self.outputPoints.get() or self.outputDXFPoints.get():
            if int(self.outputPointsNum.get()) < 3:
                messagebox.showerror(title="Error", message="Number of points on circle should be greater than 2.")
                return

        if self.outputDXF.get():
            if self.outputDXFCircle.get() or self.outputDXFDiameter.get() or self.outputDXFLabel.get() or self.outputDXFPoints.get():
                self.saveDXF(self.outputFolder.get()+DXFFileName)
            else:
                messagebox.showerror(title="Error", message="Output to DXF is selected, at least one of the sub options needs to also be selected.")
                return
        if self.outputCircles.get():
            self.saveCircles(self.outputFolder.get()+CirclesFileName)
        if self.outputPoints.get():
            self.savePoints(self.outputFolder.get()+PointsFileName)

        messagebox.showinfo(title="Success", message="Saved File/s")

    def parseData(self, fileName):
        # Parses data from the file fileName of the format:
            # poly1Point1X,poly1Point1Y,poly1Point1Z
            # poly1Point2X,poly1Point2Y,poly1Point2Z
            #
            # poly2Point1X,poly2Point1Y,poly2Point1Z
        polygons = []
        try:
            with open(fileName, "r") as f:
                points = []
                elevations = []
                for line in f:
                    if line.strip() == "":
                        if points:
                            if len(points) < 3:
                                print("Error, not enough points in one of the polygons in:", fileName)
                                sys.exit(1)
                            polygons.append([points, elevations])
                        points = []
                        elevations = []
                    else:
                        point = [float(num) for num in line.split(",")]
                        points.append(point[0:2])
                        elevations.append(point[2])
                if points:
                    if len(points) < 3:
                        print("Error, not enough points in one of the polygons in:", fileName)
                        sys.exit(1)
                    polygons.append([points, elevations])
        except OSError:
            messagebox.showerror(title="Error", message=f"Could not open input file: {fileName}")
            return False

        if not polygons:
            messagebox.showerror(title="Error", message=f"No polygons found in file: {fileName}")
            return False

        return polygons

    def saveDXF(self, outFileNameDXF):
        try:
            with r12writer(outFileNameDXF) as dxf:
                for i, circle in enumerate(self.circles):
                    if self.outputDXFCircle.get():
                        dxf.add_circle(circle[0], radius=circle[1], layer="Circle"+str(i))

                    x1 = circle[0][0] + circle[1]
                    x2 = circle[0][0] - circle[1]
                    y = circle[0][1]
                    z = circle[0][2]

                    # Draw the diameter line
                    if self.outputDXFDiameter.get():
                        dxf.add_line((x1, y, z), (x2, y, z), layer="Circle"+str(i))

                    # Add a diameter label
                    if self.outputDXFLabel.get():
                        diameter = circle[1] * 2.0  # polylabel gives the radius of the circle, we want the diameter
                        lineCentre = [(x2-x1)/2.0 + x1, y + 0.2, z]  # Centre of the line with a slight offset
                        dxf.add_text(f"{diameter:.2f}", lineCentre, align="CENTER", layer="Circle"+str(i))

                    if self.outputDXFPoints.get():
                        pointsNum = int(self.outputPointsNum.get())
                        # For each circle calculate outputPointsNum number of points around it
                        arc = 2 * pi / pointsNum
                        for j in range(pointsNum):
                            angle = arc * j
                            x = circle[0][0] + circle[1]*cos(angle)
                            y = circle[0][1] + circle[1]*sin(angle)
                            z = circle[0][2]
                            dxf.add_point((x, y, z), layer="Circle"+str(i))
        except OSError:
            messagebox.showerror(title="Error", message=f"Could not write to output file: {outFileNameDXF}")
            return 1
        return 0


    def saveCircles(self, outFileNameCircles):
        try:
            with open(outFileNameCircles, "w") as f:
                for circle in self.circles:
                    diameter = circle[1] * 2.0  # polylabel gives the radius of the circle, we want to print the diameter
                    # Output to 2 decimal places
                    output = f"{circle[0][0]:.2f},{circle[0][1]:.2f},{circle[0][2]:.2f},{diameter:.2f}\n"
                    f.write(output)
        except OSError:
            messagebox.showerror(title="Error", message=f"Could not write to output file: {outFileNameCircles}")
            return 1
        return 0


    def savePoints(self, outFileNamePoints):
        pointsNum = int(self.outputPointsNum.get())

        try:
            with open(outFileNamePoints, "w") as f:
                for circle in self.circles:
                    # For each circle calculate outputPointsNum number of points around it
                    arc = 2 * pi / pointsNum
                    for i in range(pointsNum):
                        angle = arc * i
                        x = circle[0][0] + circle[1]*cos(angle)
                        y = circle[0][1] + circle[1]*sin(angle)
                        # Output to 2 decimal places
                        output = f"{x:.2f},{y:.2f},{circle[0][2]:.2f}\n"
                        f.write(output)
                    f.write("\n")
        except OSError:
            messagebox.showerror(title="Error", message=f"Could not write to output file: {outFileNamePoints}")
            return 1
        return 0


if __name__ == '__main__':
    Gui().mainloop()
