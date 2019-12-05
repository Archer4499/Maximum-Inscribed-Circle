#!/usr/bin/env python3

# Requires Python 3.6 and above

from os import chdir, makedirs, path
from sys import platform
from math import pi, sin, cos, inf
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ezdxf.r12writer import r12writer
from polylabel import polylabel

# Use Windows high DPI scaling
if platform == 'win32':
    try:
        from ctypes import OleDLL
        OleDLL('shcore').SetProcessDpiAwareness(1)
    except (ImportError, AttributeError, OSError):
        pass


class MenuBar(tk.Menu):
    def __init__(self, root):
        super().__init__()

        self.option_add("*tearOff", False)

        file_menu = tk.Menu(self)
        file_menu.add_command(label="Exit", command=root.quit)

        help_menu = tk.Menu(self)
        help_menu.add_command(label="Support", command=lambda: webbrowser.open(r"https://github.com/Archer4499/Maximum-Inscribed-Circle"))
        help_menu.add_command(label="About",
                              command=lambda: messagebox.showinfo("About", "Reads data files containing polygons and outputs the co-ordinates and diameter "
                                                                           "(and optionally points of the circle) of maximum inscribed circles to be "
                                                                           "contained within the digitized polygons.\n\n"
                                                                           "Read more at https://github.com/Archer4499/Maximum-Inscribed-Circle\n\n"
                                                                           "This project is licensed under the MIT License."))

        self.add_cascade(menu=file_menu, label="File")
        self.add_cascade(menu=help_menu, label="Help")

        root.config(menu=self)


class NumEntry(ttk.Spinbox):
    # A number validated Spinbox
    def __init__(self, length, min_val, max_val, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.length = length
        self.min_val = min_val
        self.max_val = max_val
        self.default_val = self.get()
        self.configure(from_=self.min_val, to=self.max_val, width=self.length + 1, validate="all",
                       validatecommand=(self.register(self.on_validate), "%P", "%d", "%V"))

    def on_validate(self, new_value, action_type, validate_type):
        if validate_type == "key":
            # Don't validate if action is delete
            if action_type != "0" and new_value.strip() != "":
                try:
                    value = int(new_value)
                except ValueError:
                    self.bell()
                    return False
        elif validate_type == "focusout":
            try:
                value = int(new_value)
                if value < self.min_val:
                    self.bell()
                    self.set(self.min_val)
                    return False
                if value > self.max_val:
                    self.bell()
                    self.set(self.max_val)
                    return False
            except ValueError:
                self.bell()
                self.set(self.default_val)
                return False

        return True


class Gui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.polygons = []
        self.numPolygons = tk.IntVar()
        self.numPolygons.set(0)
        self.circles = []

        # Settings
        self.outputDXF = tk.IntVar()
        self.outputDXF.set(1)
        self.outputDXFCircle = tk.IntVar()
        self.outputDXFCircle.set(0)
        self.outputDXFDiameter = tk.IntVar()
        self.outputDXFDiameter.set(1)
        self.outputDXFLabel = tk.IntVar()
        self.outputDXFLabel.set(0)
        self.outputDXFPoints = tk.IntVar()
        self.outputDXFPoints.set(0)
        self.outputDXFPolyLines = tk.IntVar()
        self.outputDXFPolyLines.set(1)

        self.outputCircles = tk.IntVar()
        self.outputCircles.set(0)

        self.outputPoints = tk.IntVar()
        self.outputPoints.set(1)

        self.outputPointsNum = tk.StringVar()
        self.outputPointsNum.set("16")

        self.outputFolder = tk.StringVar()
        self.outputFolder.set("./")

        self.title("Maximum Inscribed Circle")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        MenuBar(self)

        mainframe = ttk.Frame(self)
        mainframe.grid(column=0, row=0, sticky="NESW")
        # Clear focus from text boxes on click
        mainframe.bind("<1>", lambda event: mainframe.focus_set())

        # TODO(Derek): Not sure how to set correct minsizes
        # Uses 3 columns
        self.initLoad(mainframe, 1)
        mainframe.columnconfigure(1, weight=1)
        mainframe.columnconfigure(2, weight=0)
        mainframe.columnconfigure(3, weight=1)

        ttk.Separator(mainframe, orient="vertical")\
            .grid(column=4, row=0, rowspan=30, padx=5, pady=0, sticky="NS")
        mainframe.rowconfigure(29, weight=1)

        # Uses 2 columns
        self.initSave(mainframe, 5)
        mainframe.columnconfigure(5, weight=0, minsize=15)
        mainframe.columnconfigure(6, weight=2)

    def initLoad(self, parentFrame, column):
        self.loadButton = ttk.Button(parentFrame, text="Open csv file/s", command=self.load)
        self.loadButton.grid(column=column, row=0, padx=5, pady=5)
        self.loadButton.focus_set()

        ttk.Label(parentFrame, text="Number of polygons found:")\
            .grid(column=column+1, row=0, sticky="E", padx=(5, 0), pady=0)
        ttk.Label(parentFrame, textvariable=self.numPolygons)\
            .grid(column=column+2, row=0, sticky="W", padx=(0, 5), pady=0)


        ttk.Label(parentFrame, text="Preview of polygons and output circles:", anchor="center")\
            .grid(column=column, columnspan=3, row=2, sticky="EW", padx=5, pady=0)
        self.canvas = tk.Canvas(parentFrame, background="white")
        self.canvas.grid(column=column, columnspan=3, row=3, rowspan=27, sticky="NESW", padx=(10, 5), pady=(0, 10))
        self.canvas.bind("<Configure>", self.drawShapes)

    def initSave(self, parentFrame, column):
        ttk.Checkbutton(parentFrame, text="Output to DXF", variable=self.outputDXF, command=self.disableDXF)\
            .grid(column=column, row=0, columnspan=2, sticky="W", padx=5, pady=(5, 0))

        self.dxfCheckButtons = []
        self.dxfCheckButtons.append(ttk.Checkbutton(parentFrame, text="Output Circle in DXF", variable=self.outputDXFCircle))
        self.dxfCheckButtons.append(ttk.Checkbutton(parentFrame, text="Output Diameter Line in DXF", variable=self.outputDXFDiameter))
        self.dxfCheckButtons.append(ttk.Checkbutton(parentFrame, text="Output Diameter Label in DXF", variable=self.outputDXFLabel))
        self.dxfCheckButtons.append(ttk.Checkbutton(parentFrame, text="Output Points in DXF", variable=self.outputDXFPoints, command=self.disablePointsNum))
        self.dxfCheckButtons.append(ttk.Checkbutton(parentFrame, text="Output PolyLine in DXF", variable=self.outputDXFPolyLines, command=self.disablePointsNum))
        for i, button in enumerate(self.dxfCheckButtons):
            button.grid(column=column+1, row=i+1, sticky="W", padx=5, pady=0)

        ttk.Checkbutton(parentFrame, text="Output to Circles csv", variable=self.outputCircles)\
            .grid(column=column, row=6, columnspan=2, sticky="W", padx=5, pady=5)

        ttk.Checkbutton(parentFrame, text="Output to Points csv", variable=self.outputPoints, command=self.disablePointsNum)\
            .grid(column=column, row=7, columnspan=2, sticky="W", padx=5, pady=5)

        ttk.Label(parentFrame, text="Number of points on circle:")\
            .grid(column=column, row=8, columnspan=2, sticky="W", padx=5, pady=(5, 0))

        self.pointsNumCheckButton = NumEntry(4, 3, 9999, parentFrame, textvariable=self.outputPointsNum)
        self.pointsNumCheckButton.grid(column=column, row=9, columnspan=2, sticky="W", padx=5, pady=0)

        ttk.Label(parentFrame, text="Output Folder:")\
            .grid(column=column, row=10, columnspan=2, sticky="W", padx=5, pady=(5, 0))
        ttk.Entry(parentFrame, textvariable=self.outputFolder)\
            .grid(column=column, row=11, columnspan=2, sticky="EW", padx=5, pady=0)

        self.browseButton = ttk.Button(parentFrame, text="Browse", command=self.browse)
        self.browseButton.grid(column=column, row=14, columnspan=2, padx=5, pady=(5, 0))

        self.saveButton = ttk.Button(parentFrame, text="Save", command=self.save)
        self.saveButton.grid(column=column, row=15, columnspan=2, padx=5, pady=(0, 5))
        self.saveButton.state(["disabled"])

    def disableDXF(self):
        # Bound to dxf CheckButton
        if self.outputDXF.get():
            for button in self.dxfCheckButtons:
                button.state(["!disabled"])
        else:
            for button in self.dxfCheckButtons:
                button.state(["disabled"])
        self.disablePointsNum()

    def disablePointsNum(self):
        # Bound to CheckButtons related to pointsNumCheckButton
        if self.outputPoints.get() or self.outputDXF.get() and (self.outputDXFPoints.get() or self.outputDXFPolyLines.get()):
            self.pointsNumCheckButton.state(["!disabled"])
        else:
            self.pointsNumCheckButton.state(["disabled"])

    def load(self):
        # Bound to loadButton
        fileNames = filedialog.askopenfilenames(filetypes=[("All Data Files", ".csv .str .txt .arch_d"),
                                                           ("CSV", ".csv"),
                                                           ("STR", ".str"),
                                                           ("Text", ".txt"),
                                                           ("Vulcan Data", ".arch_d")])
        if not fileNames:
            return

        polygons = []
        for fileName in fileNames:
            polygons.extend(parseData(fileName))
        if not polygons:
            return

        circles = []

        for polygon in polygons:
            # TODO(Derek): polylabel sometimes infinite loops if bad data is given
            #               contained multiple polygons in one, with 0, 0 in between.
            # circle is formatted as [[x,y,z],radius]
            circle = list(polylabel(polygon[0], precision=0.001, with_distance=True))
            if not circle[1]:
                prettyPolygon = [[polygon[0][i][0], polygon[0][i][1], polygon[1][i]] for i in range(len(polygon[0]))]
                messagebox.showerror(title="Error", message=f"Could not create circle from polygon:\n{prettyPolygon}")
                return
            circle[0].append(sum(polygon[1])/len(polygon[1]))
            circles.append(circle)

        self.polygons = polygons
        self.circles = circles

        self.numPolygons.set(len(polygons))
        self.saveButton.state(["!disabled"])

        self.drawShapes()

    def drawShapes(self, _=None):
        # Bound to self.canvas resize event
        # _ argument to allow being used as resize callback
        if self.polygons:
            # Clear the canvas before drawing new shapes
            self.canvas.delete("all")

            colours = ["#e6194B", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
                       "#42d4f4", "#f032e6", "#fabebe", "#469990", "#e6beff",
                       "#9A6324", "#fffac8", "#800000", "#aaffc3", "#000075",
                       "#a9a9a9", "#000000"]

            xMin = inf
            xMax = 0
            yMin = inf
            yMax = 0

            # Polygon max and mins
            for polygon in self.polygons:
                for point in polygon[0]:
                    if point[0] < xMin:
                        xMin = point[0]
                    if point[0] > xMax:
                        xMax = point[0]
                    if point[1] < yMin:
                        yMin = point[1]
                    if point[1] > yMax:
                        yMax = point[1]

            canvasWidth = self.canvas.winfo_width()
            canvasHeight = self.canvas.winfo_height()

            # Flip y-axis because origin of canvas is top left
            xCanvasMin = 10
            xCanvasMax = canvasWidth  - 10
            yCanvasMin = canvasHeight - 10
            yCanvasMax = 10

            xScale = (xCanvasMax-xCanvasMin)/(xMax-xMin)
            yScale = (yCanvasMin-yCanvasMax)/(yMax-yMin)

            if xScale < yScale:
                scale = xScale
                # Centre vertically
                yCanvasMin -= (canvasHeight - scale*(yMax-yMin)) / 2.0
            else:
                scale = yScale
                # Centre horizontally
                xCanvasMin += (canvasWidth - scale*(xMax-xMin)) / 2.0

            for i, polygon in enumerate(self.polygons):
                scaledPoints = []
                for point in polygon[0]:
                    scaledPoints.append((point[0]-xMin)*scale + xCanvasMin)
                    scaledPoints.append((point[1]-yMin)*-scale + yCanvasMin)
                self.canvas.create_polygon(scaledPoints, fill="", outline=colours[i%len(colours)], width=1)

            for i, circle in enumerate(self.circles):
                radius = circle[1]
                x = (circle[0][0]-xMin)*scale + xCanvasMin
                y = (circle[0][1]-yMin)*-scale + yCanvasMin

                x1 = (circle[0][0]-radius-xMin)*scale + xCanvasMin
                x2 = (circle[0][0]+radius-xMin)*scale + xCanvasMin
                y1 = (circle[0][1]-radius-yMin)*-scale + yCanvasMin
                y2 = (circle[0][1]+radius-yMin)*-scale + yCanvasMin

                self.canvas.create_oval(x, y, x, y, outline=colours[i%len(colours)])
                self.canvas.create_oval(x1, y1, x2, y2, outline=colours[i%len(colours)])

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
        dxfFileName = "circles.dxf"
        circlesFileName = "circles.csv"
        pointsFileName = "points.csv"

        if not self.outputFolder.get():
            messagebox.showerror(title="Error", message="Output Folder not set.")
            return
        try:
            if self.outputFolder.get()[-1] != "/":
                makedirs(self.outputFolder.get(), exist_ok=True)
                self.outputFolder.set(self.outputFolder.get()+"/")
            else:
                makedirs(self.outputFolder.get()[:-1], exist_ok=True)
        except OSError:
            messagebox.showerror(title="Error", message=f"Output Folder: {self.outputFolder.get()} is not able to be created.")
            return


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


class AskColumns(tk.Toplevel):
    def __init__(self, fileName):
        self.parent = tk._default_root  # pylint: disable=W0212
        super().__init__(self.parent)

        self.result = None
        self.separatorList = {"Comma":",", "Whitespace":" ", "Colon":":", "Semicolon":";", "Equals Sign":"="}
        self.currSeparator = self.separatorList["Comma"]
        self.fileName = fileName
        self.csvLines = []
        self.maxWidth = 0
        self.loadLines()

        self.withdraw() # remain invisible for now
        # If the master is not viewable, don't
        # make the child transient, or else it
        # would be opened withdrawn
        if self.parent.winfo_viewable():
            self.transient(self.parent)

        self.title("Select Columns")

        # Layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.mainframe = ttk.Frame(self)
        self.mainframe.bind("<1>", lambda event: self.mainframe.focus_set())
        self.mainframe.grid(column=0, row=0, sticky="NESW")
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(1, weight=1)

        descLabel = ttk.Label(self.mainframe, text=f"Select the columns that contain the X,Y,Z co-ordinates of the polygons.\n"
                              "If the polygons aren't separated by non-numerical lines, a column needs to be chosen to use as an ID string. "
                              "The ID needs to be the same for each point in a polygon and different or not continuous between polygons.\n"
                              "Use the selection box at the bottom to change the delimiter if the file isn't comma delimited.",
                              anchor="w", justify="left", wraplength=500)
        descLabel.grid(column=0, row=0, padx=10, pady=10, sticky="EW")
        descLabel.bind('<Configure>', lambda e: descLabel.config(wraplength=descLabel.winfo_width()))
        # NOTE(Derek): possibly add tooltip for showing full path? (https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python)
        ttk.Label(self.mainframe, text=f"File: {path.basename(self.fileName)}",
                  anchor="e", justify="right", wraplength=300)\
            .grid(column=1, row=0, padx=10, pady=10, sticky="ESW")

        self.data(self.mainframe)
        self.buttonbox(self.mainframe)
        ##

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        # become visible now
        self.deiconify()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.focus_force()
        self.wait_window(self)

    def destroy(self):
        tk.Toplevel.destroy(self)

    def yview(self, *args):
        for canvas in self.dataCanvases:
            canvas.yview(*args)

    def _bind_mouse(self, _=None):
        self.dataFrame.bind_all("<4>", self._on_mousewheel)
        self.dataFrame.bind_all("<5>", self._on_mousewheel)
        self.dataFrame.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, _=None):
        self.dataFrame.unbind_all("<4>")
        self.dataFrame.unbind_all("<5>")
        self.dataFrame.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        # Linux uses event.num; Windows / Mac uses event.delta
        if event.num == 4 or event.delta > 0:
            for canvas in self.dataCanvases:
                canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            for canvas in self.dataCanvases:
                canvas.yview_scroll(1, "units")

    def data(self, master):
        def onFrameConfigure(canvas):
            # Reset the scroll region to encompass the inner frame
            x1, y1, x2, y2 = canvas.bbox("all")
            canvas.configure(scrollregion=(x1, y1, x2, y2))
            canvas.configure(width=x2-x1)

        self.dataFrame = ttk.Frame(master, relief="sunken", borderwidth=4)
        self.dataFrame.grid(column=0, columnspan=2, row=1, padx=10, pady=0, sticky="NESW")
        # self.dataFrame.grid(column=0, row=1, padx=10, pady=0, sticky="NESW")
        self.dataFrame.rowconfigure(1, weight=1)

        self.dataFrame.bind("<Enter>", self._bind_mouse)
        self.dataFrame.bind("<Leave>", self._unbind_mouse)

        scroll = tk.Scrollbar(self.dataFrame, orient="vertical", command=self.yview)
        scroll.grid(column=self.maxWidth, row=1, sticky="NS")

        options = ["Ignore", "X", "Y", "Z", "ID"]

        self.selectionBoxes = []
        self.dataCanvases = []
        for column in range(self.maxWidth):
            self.dataFrame.columnconfigure(column, weight=1)

            # Header
            header = ttk.Frame(self.dataFrame, relief="groove", borderwidth=1)
            header.grid(column=column, row=0, sticky="EW")
            header.columnconfigure(0, weight=1)

            ttk.Label(header, text=column, anchor="center")\
                .grid(column=0, row=0, sticky="EW")

            selection = ttk.Combobox(header, values=options, width=5, state="readonly")
            selection.grid(column=0, row=1, sticky="EW")
            selection.bind("<<ComboboxSelected>>", self.selected)
            selection.current(0)
            self.selectionBoxes.append(selection)

            # Show a preview of some of the data file
            canvas = tk.Canvas(self.dataFrame, borderwidth=0, highlightthickness=0)
            canvas.grid(column=column, row=1, sticky="NSW")

            canvasFrame = ttk.Frame(canvas, borderwidth=0)
            canvasFrame.grid(column=0, row=0, sticky="NESW")

            canvas.create_window((0, 0), window=canvasFrame, anchor="nw")
            canvas.configure(yscrollcommand=scroll.set)

            canvasFrame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

            self.dataCanvases.append(canvas)

            for row, line in enumerate(self.csvLines):
                if column < len(line):
                    token = line[column]
                    ttk.Label(canvasFrame, text=token.strip(), relief="sunken", borderwidth=1)\
                        .grid(column=0, row=row, padx=1, sticky="EW")
                else:
                    ttk.Label(canvasFrame, text="", borderwidth=1)\
                        .grid(column=0, row=row, padx=1, sticky="EW")

    def buttonbox(self, master):
        box = ttk.Frame(master)
        box.grid(column=0, columnspan=2, row=2, padx=10, pady=10, sticky="EW")

        # NOTE(Derek): possibly allow entering characters
        ttk.Label(box, text="Delimiter:")\
            .grid(column=0, row=0, padx=(5, 0), pady=5, sticky="E")
        self.separatorSelect = ttk.Combobox(box, values=list(self.separatorList), width=9, state="readonly")
        self.separatorSelect.grid(column=1, row=0, padx=(0, 5), pady=5, sticky="W")
        self.separatorSelect.bind("<<ComboboxSelected>>", self.separatorSet)
        self.separatorSelect.current(0)

        self.okButton = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        self.okButton.grid(column=2, row=0, padx=5, pady=5, sticky="E")
        ttk.Button(box, text="Cancel", width=10, command=self.cancel)\
            .grid(column=3, row=0, padx=5, pady=5, sticky="E")

        box.columnconfigure(1, weight=1)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

    def selected(self, event):
        current = event.widget.current()
        # Check for other selections having the same value if not "Ignore"
        #  and reset any to "Ignore".
        if current > 0:
            for selection in self.selectionBoxes:
                # Only check other widgets
                if selection is not event.widget:
                    if selection.current() == current:
                        selection.current(0)

    def separatorSet(self, event):
        newSeparator = self.separatorList[event.widget.get()]

        if newSeparator != self.currSeparator:
            self.currSeparator = newSeparator
            self.loadLines()
            self.dataFrame.grid_forget()
            self.dataFrame.destroy()
            self.data(self.mainframe)

    def loadLines(self):
        self.csvLines = []
        self.maxWidth = 0
        try:
            with open(self.fileName, "r") as f:
                for i, line in enumerate(f):
                    self.csvLines.append(smartSplit(line.strip(), self.currSeparator))
                    self.maxWidth = max(self.maxWidth, len(self.csvLines[i]))
                    # Only take at most 100 lines
                    if i > 100:
                        break
        except OSError:
            messagebox.showerror(title="Error", message=f"Could not open input file:\n{self.fileName}")
            return

    def getSelections(self):
        selections = [-1, -1, -1, -1]

        for i, selection in enumerate(self.selectionBoxes):
            current = selection.current()
            if current > 0:
                selections[current-1] = i

        return selections

    def ok(self, _=None):
        # _ to allow event binding

        # Make sure X,Y,Z are all selected (>0)
        selections = self.getSelections()
        if min(selections[:3]) < 0:
            self.bell()
            # Flash effect
            self.after(70, self.mainframe.focus_set)
            self.after(140, self.okButton.focus_set)
            self.after(210, self.mainframe.focus_set)
            self.after(280, self.okButton.focus_set)
            self.after(350, self.mainframe.focus_set)
            return

        self.withdraw()
        self.update_idletasks()

        self.result = self.getSelections()
        self.cancel()

    def cancel(self, _=None):
        # _ to allow event binding
        self.parent.focus_set()
        self.destroy()


class AskAuto(tk.Toplevel):
    def __init__(self, baseFileName):
        self.parent = tk._default_root  # pylint: disable=W0212
        super().__init__(self.parent)

        self.result = None
        self.baseFileName = baseFileName

        self.withdraw() # remain invisible for now
        # If the master is not viewable, don't
        # make the child transient, or else it
        # would be opened withdrawn
        if self.parent.winfo_viewable():
            self.transient(self.parent)

        self.title("Process File")

        # Layout
        self.resizable(False, False)
        self.geometry("+%d+%d" % (self.parent.winfo_rootx()+50,
                                  self.parent.winfo_rooty()+50))
        self.mainframe = ttk.Frame(self)
        self.mainframe.bind("<1>", lambda event: self.mainframe.focus_set())
        self.mainframe.grid(column=0, row=0, sticky="NESW")
        self.mainframe.columnconfigure(0, weight=1)

        self.body(self.mainframe)
        self.buttonbox(self.mainframe)
        ##

        self.protocol("WM_DELETE_WINDOW", self.skip)

        # become visible now
        self.deiconify()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.focus_force()
        self.wait_window(self)

    def body(self, master):
        bodyFrame = ttk.Frame(master)
        bodyFrame.grid(column=0, columnspan=4, row=0, padx=20, pady=20, sticky="NESW")
        bodyFrame.columnconfigure(3, weight=1)

        ttk.Label(bodyFrame, wraplength=400, text=f"{self.baseFileName}", font="-weight bold")\
            .grid(column=0, columnspan=4, row=0, sticky="NESW")
        ttk.Label(bodyFrame, wraplength=400, text="Is not in a recognised format.\nAttempt to parse automatically or manually specify columns?")\
            .grid(column=0, columnspan=4, row=1, sticky="NESW")
        ttk.Label(bodyFrame, wraplength=400, text="If you would like this format to be automatically processed, please report an issue to the")\
            .grid(column=0, columnspan=4, row=2, sticky="NESW")

        linkLabel = ttk.Label(bodyFrame, foreground="#0645AD", font="-underline 1", anchor="w",
                              text=r"GitHub")
        linkLabel.grid(column=0, row=3, sticky="NW")
        linkLabel.bind("<Button-1>", lambda event: webbrowser.open(r"https://github.com/Archer4499/Maximum-Inscribed-Circle"))

        ttk.Label(bodyFrame, anchor="w", text="page or email")\
            .grid(column=1, row=3, sticky="NW")

        emailLabel = ttk.Label(bodyFrame, foreground="#0645AD", font="-underline 1", anchor="w",
                               text=r"king.dm49@gmail.com")
        emailLabel.grid(column=2, row=3, sticky="NW")
        emailLabel.bind("<Button-1>", lambda event: webbrowser.open(r"mailto:?to=king.dm49+mic@gmail.com&subject=Add%20support%20for%20new%20file%20format"))

    def buttonbox(self, master):
        autoButton = ttk.Button(master, text="Auto", command=self.auto, default=tk.ACTIVE)
        autoButton.grid(column=1, row=1, padx=0, pady=10, sticky="E")
        autoButton.focus_set()
        ttk.Button(master, text="Manual", command=self.manual)\
            .grid(column=2, row=1, padx=5, pady=10, sticky="E")
        ttk.Button(master, text="Skip", command=self.skip)\
            .grid(column=3, row=1, padx=10, pady=10, sticky="E")

        self.bind("<Return>", self.auto)
        self.bind("<Escape>", self.skip)

    def auto(self, _=None):
        self.result = True
        self.skip()

    def manual(self, _=None):
        self.result = False
        self.skip()

    def skip(self, _=None):
        self.parent.focus_set()
        self.destroy()


def smartSplit(line, separator):
    # Using line.split() if whitespace used as separator allows
    #  counting multiple sequential separators as one
    if separator.isspace():
        tokens = line.split()
    else:
        tokens = line.split(separator)
    return tokens


def parseWithoutID(fileName, columns, separator):
    # Parse columns given in columns[] without ID
    polygons = []
    points = []
    elevations = []

    try:
        with open(fileName, "r") as f:
            for line in f:
                tokens = smartSplit(line, separator)

                # Make sure the line has at least as many tokens as required, otherwise treat it as empty
                if len(tokens) >= max(columns):
                    try:
                        x = float(tokens[columns[0]])
                        y = float(tokens[columns[1]])
                        z = float(tokens[columns[2]])
                        points.append([x, y])
                        elevations.append(z)
                        continue  # for line in f
                    except ValueError:
                        pass

                # If either empty line or floats can't be found in specified columns treat as end of polygon
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

    return polygons


def parseWithID(fileName, columns, separator):
    # Parse columns given in columns[] with ID
    polygons = []
    points = []
    elevations = []

    try:
        with open(fileName, "r") as f:
            currID = ""
            for line in f:
                tokens = smartSplit(line, separator)

                # Make sure the line has at least as many tokens as required, otherwise treat it as empty
                if len(tokens) > max(columns):
                    try:
                        newID = tokens[columns[3]]
                        # If ID is different we are in a new object
                        if newID != currID:
                            if len(points) >= 3:
                                polygons.append([points, elevations])
                            points = []
                            elevations = []
                            currID = newID
                        x = float(tokens[columns[0]])
                        y = float(tokens[columns[1]])
                        z = float(tokens[columns[2]])
                        points.append([x, y])
                        elevations.append(z)
                        continue  # for line in f
                    except ValueError:
                        pass

                # If either empty line or floats can't be found in specified columns treat as end of polygon
                if len(points) >= 3:
                    polygons.append([points, elevations])
                points = []
                elevations = []
            if len(points) >= 3:
                polygons.append([points, elevations])

    except OSError:
        messagebox.showerror(title="Error", message=f"Could not open input file: {fileName}")
        return []

    return polygons


def parseUnknown(fileName):
    # Attempt to parse unknown format
    separators = [",", " ", ";"]
    polygons = []

    try:
        with open(fileName, "r") as f:
            for separator in separators:
                f.seek(0)  # Go back to start of file for each separator
                points = []
                elevations = []

                for line in f:
                    tokens = smartSplit(line, separator)

                    # Searches the line for a group of 3 consecutive numbers
                    for i in range(len(tokens)-2):
                        try:
                            x = float(tokens[i])
                            y = float(tokens[i+1])
                            z = float(tokens[i+2])
                            points.append([x, y])
                            elevations.append(z)
                            break
                        except ValueError:
                            pass
                    else:
                        # If line is either too short or doesn't contain 3 floats,
                        #   then it counts as an empty line and we move onto the next polygon
                        if len(points) >= 3:
                            polygons.append([points, elevations])
                        points = []
                        elevations = []
                if len(points) >= 3:
                    polygons.append([points, elevations])

                if polygons:
                    # If we found polygons in file finish processing, else try again with a different separator
                    break
    except OSError:
        messagebox.showerror(title="Error", message=f"Could not open input file: {fileName}")
        return []

    return polygons


def parseData(fileName):
    # Parses data from the file fileName in the CSV format GEM4D outputs
    # And attempts to parse similar CSV files, main requirements are:
        # At least one line, without 3 consecutive numbers, separating each polygon
        # Comma separated values
        # 3 consecutive numbers on each polygon line interpreted as x,y,z
    try:
        with open(fileName, "r") as f:
            firstLine = f.readline()
            if not firstLine:
                messagebox.showerror(title="Error", message=f"File: {fileName} is empty")
                return []
            # Reset position in file to beginning after reading first line
    except OSError:
        messagebox.showerror(title="Error", message=f"Could not open input file: {fileName}")
        return []

    polygons = []

    columns = []
    separator = ","
    firstToken = smartSplit(firstLine, separator)[0]
    baseFileName = path.basename(fileName)

    # Check for recognised formats else ask user to specify columns
    if ".csv" in baseFileName and firstToken == "DHid":
        # GEM4D csv format
        columns = [1, 2, 3, -1]
    elif ".csv" in baseFileName and  "Leapfrog" in firstToken and "v1.2" in firstToken:
        # Leapfrog v1.2 csv format
        columns = [0, 1, 2, -1]
    elif ".arch_d" in baseFileName and firstLine.split()[0] == "FMT_3":
        # Vulcan arch_d format
        columns = [2, 3, 4, -1]
        separator = " "
    elif "SimpleFormat" in firstToken:
        # Custom SimpleFormat
        columns = [0, 1, 2, -1]
    else:
        # TODO(Derek): checkbox to allow temp suppress warning? (while program still open)
        ask = AskAuto(baseFileName)
        answer = ask.result
        if answer is None:
            # Skip file
            return []
        elif not answer:
            # Ask user to specify columns
            ask = AskColumns(fileName)
            columns = ask.result
            separator = ask.currSeparator
            if columns is None:
                # Cancel, skip file
                return []

    # Parse
    if columns:
        if columns[3] < 0:
            polygons = parseWithoutID(fileName, columns, separator)
        else:
            polygons = parseWithID(fileName, columns, separator)
    else:
        polygons = parseUnknown(fileName)

    if not polygons:
        messagebox.showerror(title="Error", message=f"No polygons found in file: {fileName}")
        return []

    return polygons


if __name__ == '__main__':
    Gui().mainloop()
