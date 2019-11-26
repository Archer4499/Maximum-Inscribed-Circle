# Maximum Inscribed Circle

Outputs the co-ordinates and diameter (and optionally points of the circle) of a maximum inscribed circle to be contained within a digitized polygon


### Usage:
```
python3 main.py inputFileName [d|c|p [outputFileName]]
```

## Getting Started:

Requires Python 3.6 or above.

Run the following in a console to install the required packages:
```
python3 -m pip install ezdxf
```

Either download and extract the repository zip file or just main.py and polylabel.py (and optionally exampleData.csv), and run the following in a console to use the example data and output a `.dxf` file:
```
python3 main.py exampleData.csv
```

If just the input filename is given it will output a `.dxf` file containing the maximum inscribed circles, a diameter line and a diameter label, called `circles.dxf`

The following modes can be specified and will output to default filenames or to the specified output filename:
```
d - Output a dxf file called circles.dxf, containing the maximum inscribed circles, a diameter line and a diameter label.
c - Output a csv file called circles.csv, containing the centre point and diameter of each maximum inscribed circle.
p - Output a csv file called points.csv, containing the points defining the a 16-sided polygon (can easily be changed at the top of the output function in the main.py file) approximation of each maximum inscribed circle.
```

The expected input is a csv file with a blank line separating each polygon, in the following format:
```
poly1Point1X,poly1Point1Y,poly1Point1Z
poly1Point2X,poly1Point2Y,poly1Point2Z
poly1Point3X,poly1Point3Y,poly1Point3Z
poly1Point4X,poly1Point4Y,poly1Point4Z

poly2Point1X,poly2Point1Y,poly2Point1Z
poly2Point2X,poly2Point2Y,poly2Point2Z
poly2Point3X,poly2Point3Y,poly2Point3Z
```

The circles output file contains the centre point and diameter of each maximum inscribed circle in the following format:
```
circle1X,circle1Y,circle1Z,circle1Diameter
circle2X,circle2Y,circle2Z,circle2Diameter
circle3X,circle3Y,circle3Z,circle3Diameter
```

The points output file contains the points defining each maximum inscribed circle in the following format, with a blank line separating each circle:
```
circle1Point1X,circle1Point1Y,circle1Point1Z
circle1Point2X,circle1Point2Y,circle1Point2Z
circle1Point3X,circle1Point3Y,circle1Point3Z

circle2Point1X,circle2Point1Y,circle2Point1Z
circle2Point2X,circle2Point2Y,circle2Point2Z
```


---
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgements

The Pole of Inaccessibility calculation uses code slightly modified by me from a port to python: https://github.com/Twista/python-polylabel of the original algorithm from MapBox: https://github.com/mapbox/polylabel

Uses the exdxf(https://pypi.org/project/ezdxf/) package to write .dxf files.
