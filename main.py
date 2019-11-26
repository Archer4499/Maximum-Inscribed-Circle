#!/usr/bin/env python3

# Requires Python 3.6 and above

import sys
from math import pi, sin, cos
from polylabel import polylabel
from ezdxf.r12writer import r12writer


def parseData(fileName):
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
        print("Error, could not open input file:", fileName)
        sys.exit(1)

    if not polygons:
        print("Error, no polygons found in file:", fileName)
        sys.exit(1)

    return polygons


def outputDXF(circles, outFileNameDXF):
    # Change these to choose whether to draw the line/label
    drawLine = True
    drawLabel = True

    try:
        with r12writer(outFileNameDXF) as dxf:
            for circle in circles:
                dxf.add_circle(circle[0], radius=circle[1])

                x1 = circle[0][0] + circle[1]
                x2 = circle[0][0] - circle[1]
                y = circle[0][1]
                z = circle[0][2]
                
                # Draw the diameter line
                if drawLine:
                    dxf.add_line((x1, y, z), (x2, y, z))
                
                # Add a diameter label
                if drawLabel:
                    diameter = circle[1] * 2.0  # polylabel gives the radius of the circle, we want the diameter
                    lineCentre = [(x2-x1)/2.0 + x1, y + 0.2, z]  # Centre of the line with a slight offset
                    dxf.add_text(f"{diameter:.2f}", lineCentre, align="CENTER")
    except OSError:
        print("Error, could not write to output file:", outFileNameDXF)
        sys.exit(1)


def outputCircles(circles, outFileNameCircles):
    try:
        with open(outFileNameCircles, "w") as f:
            for circle in circles:
                diameter = circle[1] * 2.0  # polylabel gives the radius of the circle, we want to print the diameter
                # Output to 2 decimal places
                output = f"{circle[0][0]:.2f},{circle[0][1]:.2f},{circle[0][2]:.2f},{diameter:.2f}\n"
                f.write(output)
    except OSError:
        print("Error, could not write to output file:", outFileNameCircles)
        sys.exit(1)


def outputPoints(circles, outFileNamePoints):
    circleSections = 16

    if outFileNamePoints:
        try:
            with open(outFileNamePoints, "w") as f:
                for circle in circles:
                    # For each circle calculate circleSections number of points around it
                    arc = 2 * pi / circleSections
                    for i in range(circleSections):
                        angle = arc * i
                        x = circle[0][0] + circle[1]*cos(angle)
                        y = circle[0][1] + circle[1]*sin(angle)
                        # Output to 2 decimal places
                        output = f"{x:.2f},{y:.2f},{circle[0][2]:.2f}\n"
                        f.write(output)
                    f.write("\n")
        except OSError:
            print("Error, could not write to output file:", outFileNamePoints)
            sys.exit(1)


if __name__ == '__main__':
    circles = []

    if len(sys.argv) == 2:
        mode = 0
        outFileName = "circles.dxf"
    elif len(sys.argv) == 3:
        modeName = sys.argv[2]
        if modeName == "d":
            mode = 0
            outFileName = "circles.dxf"
        elif modeName == "c":
            mode = 1
            outFileName = "circles.csv"
        elif modeName == "p":
            mode = 2
            outFileName = "points.csv"
        else:
            print("Error, incorrect mode, Usage:", sys.argv[0], "inputFileName [d|c|p [outputFileName]]")
            sys.exit(1)
    elif len(sys.argv) == 4:
        modeName = sys.argv[2]
        if modeName == "d":
            mode = 0
        elif modeName == "c":
            mode = 1
        elif modeName == "p":
            mode = 2
        else:
            print("Error, incorrect mode, Usage:", sys.argv[0], "inputFileName [d|c|p [outputFileName]]")
            sys.exit(1)

        outFileName = sys.argv[3]
    else:
        print("Error, incorrect arguments, Usage:", sys.argv[0], "inputFileName [d|c|p [outputFileName]]")
        sys.exit(1)


    polygons = parseData(sys.argv[1])
    for polygon in polygons:
        # circle is formatted as [[x,y,z],radius]
        circle = list(polylabel(polygon[0], precision=0.001, with_distance=True))
        circle[0].append(sum(polygon[1])/len(polygon[1]))
        circles.append(circle)

    if mode == 0:
        outputDXF(circles, outFileName)
    elif mode == 1:
        outputCircles(circles, outFileName)
    elif mode == 2:
        outputPoints(circles, outFileName)
