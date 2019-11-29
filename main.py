#!/usr/bin/env python3

# Requires Python 3.6 and above

from os import chdir
from math import pi, sin, cos
from tkinter import *  # pylint: disable=W0401,W0614
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
                              command=lambda: messagebox.showinfo("About", "v1.0"))

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
        self.outputDXFPolyLines = IntVar()
        self.outputDXFPolyLines.set(0)

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
        self.loadButton = ttk.Button(parentFrame, text="Open csv file/s", command=self.load)
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
        ttk.Checkbutton(parentFrame, text="Output PolyLine in DXF", variable=self.outputDXFPolyLines)\
            .grid(column=column+1, row=5, sticky=W, padx=5, pady=0)

        ttk.Checkbutton(parentFrame, text="Output to Circles csv", variable=self.outputCircles)\
            .grid(column=column, row=6, columnspan=2, sticky=W, padx=5, pady=5)

        ttk.Checkbutton(parentFrame, text="Output to Points csv", variable=self.outputPoints)\
            .grid(column=column, row=7, columnspan=2, sticky=W, padx=5, pady=5)

        ttk.Label(parentFrame, text="Number of points on circle:")\
            .grid(column=column, row=8, columnspan=2, sticky=W, padx=5, pady=(5, 0))
        # TODO: disable when neither output points in DXF or output points csv are selected
        self.NumEntry(4, 0, 9999, parentFrame, textvariable=self.outputPointsNum)\
            .grid(column=column, row=9, columnspan=2, sticky=W, padx=5, pady=0)

        ttk.Label(parentFrame, text="Output Folder:")\
            .grid(column=column, row=10, columnspan=2, sticky=W, padx=5, pady=(5, 0))
        ttk.Entry(parentFrame, textvariable=self.outputFolder)\
            .grid(column=column, row=11, columnspan=2, sticky=(W, E), padx=5, pady=0)

        self.browseButton = ttk.Button(parentFrame, text="Browse", command=self.browse)
        self.browseButton.grid(column=column, row=14, columnspan=2, padx=5, pady=(5, 0))

        self.saveButton = ttk.Button(parentFrame, text="Save", command=self.save)
        self.saveButton.grid(column=column, row=15, columnspan=2, padx=5, pady=(0, 5))
        self.saveButton.state(["disabled"])

    def load(self):
        # Bound to loadButton
        fileNames = filedialog.askopenfilenames(filetypes=[("csv files", "*.csv")])
        if not fileNames:
            return

        polygons = []
        for fileName in fileNames:
            polygons.extend(parseData(fileName))
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
        # TODO(Derek): create folder if not existing?
        dxfFileName = "circles.dxf"
        circlesFileName = "circles.csv"
        pointsFileName = "points.csv"

        if not self.outputFolder.get():
            messagebox.showerror(title="Error", message="Output Folder not set.")
            return
        if self.outputFolder.get()[-1] != "/":
            self.outputFolder.set(self.outputFolder.get()+"/")

        if self.outputPoints.get() or self.outputDXFPoints.get() or self.outputDXFPolyLines.get():
            if int(self.outputPointsNum.get()) < 3:
                messagebox.showerror(title="Error", message="Number of points on circle should be greater than 2.")
                return

        if self.outputDXF.get():
            if self.outputDXFCircle.get() or self.outputDXFDiameter.get() or self.outputDXFLabel.get() or self.outputDXFPoints.get() or self.outputDXFPolyLines.get():
                self.saveDXF(self.outputFolder.get()+dxfFileName)
            else:
                messagebox.showerror(title="Error", message="Output to DXF is selected, at least one of the sub options needs to also be selected.")
                return
        if self.outputCircles.get():
            self.saveCircles(self.outputFolder.get()+circlesFileName)
        if self.outputPoints.get():
            self.savePoints(self.outputFolder.get()+pointsFileName)

        messagebox.showinfo(title="Success", message="Saved File/s")

    def saveDXF(self, outFileNameDXF):
        try:
            with r12writer(outFileNameDXF) as dxf:
                for i, circle in enumerate(self.circles):
                    pointsNum = int(self.outputPointsNum.get())

                    centre = circle[0]
                    radius = circle[1]

                    x = centre[0]
                    x1 = x + radius
                    x2 = x - radius
                    y = centre[1]
                    z = centre[2]

                    arc = 2 * pi / pointsNum

                    # Draw the circle
                    if self.outputDXFCircle.get():
                        dxf.add_circle(centre, radius=radius, layer="Circle"+str(i))

                    # Draw the diameter line
                    if self.outputDXFDiameter.get():
                        dxf.add_line((x1, y, z), (x2, y, z), layer="Circle"+str(i))

                    # Draw the diameter label
                    if self.outputDXFLabel.get():
                        diameter = radius * 2.0  # polylabel gives the radius of the circle, we want the diameter
                        lineCentre = [(x2-x1)/2.0 + x1, y + 0.2, z]  # Centre of the line with a slight offset
                        dxf.add_text(f"{diameter:.2f}", lineCentre, align="CENTER", layer="Circle"+str(i))

                    # Draw the points approximating circle
                    if self.outputDXFPoints.get():
                        # For each circle calculate outputPointsNum number of points around it
                        for j in range(pointsNum):
                            angle = arc * j
                            currX = x + radius*cos(angle)
                            currY = y + radius*sin(angle)
                            dxf.add_point((currX, currY, z), layer="Circle"+str(i))

                    # Draw the polylines approximating circle
                    if self.outputDXFPolyLines.get():
                        # For each circle calculate outputPointsNum number of points around it
                        points = [(x+radius*cos(arc*j), y+radius*sin(arc*j), z) for j in range(pointsNum)]
                        points.append(points[0])
                        dxf.add_polyline(points, layer="Circle"+str(i))
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


def parseData(fileName):
    # Parses data from the file fileName of either a basic csv format:
        # poly1Point1X,poly1Point1Y,poly1Point1Z
        # poly1Point2X,poly1Point2Y,poly1Point2Z
        #
        # poly2Point1X,poly2Point1Y,poly2Point1Z
    # Or approximately the csv format GEM4D outputs, main requirements are:
        # At least one line with no numbers separating each polygon
        # Comma separated values
        # 3 consecutive numbers on each polygon line interpreted as x,y,z
    polygons = []
    try:
        with open(fileName, "r") as f:
            points = []
            elevations = []

            firstLine = f.readline()
            if not firstLine:
                messagebox.showerror(title="Error", message=f"Tried reading empty file: {fileName}")
                return []
            # Reset position in file to beginning after reading first line
            f.seek(0)

            firstToken = firstLine.split(",")[0]

            # Check if the first token is a number, if so then it's probably in basic format
            try:
                float(firstToken)
                for line in f:
                    # If blank line, move onto next polygon
                    if line.strip() == "":
                        if points:
                            if len(points) < 3:
                                messagebox.showerror(title="Error", message=f"Not enough points in number {len(polygons)} polygon in file: {fileName}")
                                return []
                            polygons.append([points, elevations])
                        points = []
                        elevations = []
                    else:
                        point = [float(num) for num in line.split(",")]
                        points.append(point[0:2])
                        elevations.append(point[2])
                if points:
                    if len(points) < 3:
                        messagebox.showerror(title="Error", message=f"Not enough points in number {len(polygons)} polygon in file: {fileName}")
                        return []
                    polygons.append([points, elevations])
            except ValueError:
                # If not, check if first token is "DHid", if so then probably GEM4D csv file
                # If not, then try to parse as a GEM4D csv file and show warning.

                if firstToken != "DHid":
                    messagebox.showwarning(title="Warning", message=f"{fileName} not in recognised format, trying to parse as GEM4D output.")

                for line in f:
                    tokens = line.split(",")

                    # Searches the line for a group of 3 consecutive numbers
                    for i in range(len(tokens)-2):
                        try:
                            points.append([float(tokens[i]), float(tokens[i+1])])
                            elevations.append(float(tokens[i+2]))
                            break
                        except ValueError:
                            continue
                    else:
                        # If line is either too short or doesn't contain 3 floats,
                        #   then it counts as an empty line and we move onto the next polygon
                        if points:
                            if len(points) < 3:
                                messagebox.showerror(title="Error", message=f"Not enough points in number {len(polygons)} polygon in file: {fileName}")
                                return []
                            polygons.append([points, elevations])
                        points = []
                        elevations = []
                if points:
                    if len(points) < 3:
                        messagebox.showerror(title="Error", message=f"Not enough points in number {len(polygons)} polygon in file: {fileName}")
                        return []
                    polygons.append([points, elevations])
    except OSError:
        messagebox.showerror(title="Error", message=f"Could not open input file: {fileName}")
        return []

    if not polygons:
        messagebox.showerror(title="Error", message=f"No polygons found in file: {fileName}")
        return []

    return polygons


if __name__ == '__main__':
    Gui().mainloop()
