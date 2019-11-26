#!/usr/bin/env python3

# Requires Python 3.6 and above

import sys
from polylabel import polylabel
from math import pi, sin, cos


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


def output(circles, outFileNameCircles, outFileNamePoints):
    circleSections = 16

    try:
        with open(outFileNameCircles, "w") as f:
            for circle in circles:
                # Output to 2 decimal places
                output = f"{circle[0][0]:.2f},{circle[0][1]:.2f},{circle[0][2]:.2f},{circle[1]:.2f}\n"
                f.write(output)
    except OSError:
        print("Error, could not write to output file:", outFileNameCircles)
        sys.exit(1)

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
        outFileNameCircles = "circles.csv"
        outFileNamePoints = "points.csv"
    elif len(sys.argv) == 3:
        outFileNameCircles = sys.argv[2]
        outFileNamePoints = ""
    elif len(sys.argv) == 4:
        outFileNameCircles = sys.argv[2]
        outFileNamePoints = sys.argv[3]
    else:
        print("Error, incorrect arguments, Usage:", sys.argv[0], "inputFileName [outputFileNameCircles [outputFileNamePoints]]")
        sys.exit(1)


    polygons = parseData(sys.argv[1])
    for polygon in polygons:
        # circle is formatted as [[x,y,z],radius]
        circle = list(polylabel(polygon[0], precision=0.001, with_distance=True))
        circle[1] *= 2.0  # polylabel gives the radius of the circle, we want the diameter
        circle[0].append(sum(polygon[1])/len(polygon[1]))
        circles.append(circle)

    output(circles, outFileNameCircles, outFileNamePoints)
