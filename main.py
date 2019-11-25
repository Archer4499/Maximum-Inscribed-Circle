#!/usr/bin/env python3
import sys
from polylabel import polylabel
from math import pi, sin, cos


def parseData(fileName):
    polygons = []
    try:
        with open(fileName, "r") as f:
            points = []
            elevations = []
            for line in f:
                if line.strip() == "":
                    if points:
                        polygons.append([points, elevations])
                    points = []
                    elevations = []
                else:
                    point = [float(num) for num in line.split(",")]
                    points.append(point[0:2])
                    elevations.append(point[2])
            if points:
                polygons.append([points, elevations])
    except OSError:
        print("Error, could not open input file:", fileName)
        sys.exit(1)

    if not polygons:
        print("Error, no polygons found in file:", fileName)
        sys.exit(1)
    # print(points)
    # print()
    # print(avgElvations)

    return polygons


def output(circles, outFileNameCircles, outFileNamePoints):
    circleSections = 16

    try:
        with open(outFileNameCircles, "w") as f:
            for circle in circles:
                f.write(str(circle[0][0])+","+str(circle[0][1])+","+str(circle[0][2])+","+str(circle[1])+"\n")
    except OSError:
        print("Error, could not write to output file:", outFileNameCircles)
        sys.exit(1)

    if outFileNamePoints:
        try:
            with open(outFileNamePoints, "w") as f:
                for circle in circles:
                    arc = 2 * pi / circleSections
                    for i in range(circleSections):
                        angle = arc * i
                        newX = circle[0][0] + circle[1]*cos(angle)
                        newY = circle[0][1] + circle[1]*sin(angle)
                        f.write(str(newX)+","+str(newY)+","+str(circle[0][2])+"\n")
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
        circle = polylabel(polygon[0], precision=0.001, with_distance=True)
        circle[0].append(sum(polygon[1])/len(polygon[1]))
        circles.append(circle)

    output(circles, outFileNameCircles, outFileNamePoints)
