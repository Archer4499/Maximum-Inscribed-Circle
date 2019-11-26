# Maximum Inscribed Circle

Outputs the co-ordinates and radius (and optionally points of the circle) of a maximum inscribed circle to be contained within a digitized polygon

## Getting Started:

Either download and extract the repository zip file or just main.py and polylabel.py (and optionally exampleData.csv), and run the following in a console to use the example data:
```
python3 main.py exampleData.csv circles.csv points.csv
```
If just the input filename is given it will output the data to files named `circles.csv` and `points.csv`. If the first output file name is also given it will output the center point and radius of each maximum inscribed circle to the given output filename. And if both output names are given it will also output the points defining the a 16-sided polygon (can easily be changed at the top of the output function in the main.py file) approximation of each maximum inscribed circle to the second given output filename.

The expected input is a csv file with an blank line seperating each polygon, in the following format:
```
poly1Point1X,poly1Point1Y,poly1Point1Z
poly1Point2X,poly1Point2Y,poly1Point2Z
poly1Point3X,poly1Point3Y,poly1Point3Z
poly1Point4X,poly1Point4Y,poly1Point4Z

poly2Point1X,poly2Point1Y,poly2Point1Z
poly2Point2X,poly2Point2Y,poly2Point2Z
poly2Point3X,poly2Point3Y,poly2Point3Z
```

The first (circles) output file contains the center point and radius of each maximum inscribed circle in the following format:
```
circle1X,circle1Y,circle1Z,circle1Radius
circle2X,circle2Y,circle2Z,circle2Radius
circle3X,circle3Y,circle3Z,circle3Radius
```

The optinal second (points) output file contains the points defining each maximum inscribed circle in the following format, with an blank line seperating each circle:
```
circle1X,circle1Y,circle1Z,circle1Radius
circle2X,circle2Y,circle2Z,circle2Radius
circle3X,circle3Y,circle3Z,circle3Radius
```

### Usage:
```
python3 main.py inputFileName [outputFileNameCircles [outputFileNamePoints]]
```


---
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

The Pole of Inaccessibility calculation uses code slightly modified by me from a port to python: https://github.com/Twista/python-polylabel of the original algorithm from MapBox: https://github.com/mapbox/polylabel
