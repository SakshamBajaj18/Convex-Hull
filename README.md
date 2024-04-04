# CS_F364_DAA

Group Members:
Kolasani Amit Vishnu: 2021A7PS0151H
Rohan Pothireddy: 2021A7PS0365H
Saksham Bajaj: 2021A7PS1315H
Vashisth Choudhari: 2021A7PS1989H

Web Pages of assignments done as a part of coursework under Prof. Tathagatha Ray, BITS Pilani Hyderabad Campus. This assignment encompasses a Graphical User Interface to depict visualisation for two convex hull algorithms, namely Jarvis March and Kirkpatrick Seidel. 

We have used a Flask App in coordination with a Bokeh Server for this project. The languages used are HTML, CSS and Python. Our Flask App runs on the 5000 port and our Bokeh server runs on the 5006 port.

To run the project, follow the following steps:

	1) Enter the GUI folder
	2) run the command 
		"pip install -r requirements.txt"
	   to download all the packages and libraries required for running the application
	3) run the following command on a terminal instance in the path .\CS_F364_DAA\GUI
		"bokeh serve kps.py jm.py --allow-websocket-origin=127.0.0.1:5000"
	   to start our Bokeh Server
	4) run the Flask Server on another terminal in the path .\CS_F364_DAA\GUI by
		"python app.py"
	   to start our Flask App
	5) visit 127.0.0.1:5000 and browse

Our visualisation interface allows uploading of csv and txt files for a large number of points or specific points. The format of the points should be " x , y " with each pair in a new line. There are tools on the right margin of graph which makes interacting with the graph easier. 

The 'Skip Visualisation' option may take some time in the case of large number of points due to internal buffers of Bokeh. Using the 'Show Solution' button for quick results without the need of visualisation.

Zoom Tools and Pan Tools can be used for a seamless experience at playing around with the graph.