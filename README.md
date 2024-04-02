# CS_F364_DAA
Web Pages of assignments done as a part of coursework under Prof. Tathagatha Ray, BITS Pilani Hyderabad Campus. This assignment encompasses a Graphical User Interface to depict visualisation for two convex hull algorithms, namely Jarvis March and Kirkpatrick Seidel. 

We use a Flask App in coordination with a Bokeh Server for this project. The languages used for this project are HTML, CSS and Python. Our Flask App runs on the 5000 port and our Bokeh server runs on the 5006 port.

To run the project, follow the following steps:

	1) Enter the GUI folder
	2) run the command 
		"pip install -r requirements.txt"
	   to download all the packages and libraries required for seamless running
	3) run the command on a terminal instance
		"bokeh serve kps.py jm.py --allow-websocket-origin=127.0.0.1:5000"
	   to start our Bokeh Server
	4) run the Flask Server on another terminal by
		"python app.py"
	   to start our Flask App
	5) visit 127.0.0.1:5000 and browse

Our visualisation interface allows uploading of csv and txt files for points upload. The format of the same sould be points in the format " x , y " with each pair in a new line. There are tools on the right margin of graph which makes the interacyion with graph easier. 

The skip visalisation takes a bit of time in case of large number of points due to internal buffers of Bokeh. Prefer to use the Show Solution button for quick results without the need of visualisation.

Zoom Tools and Pan Tools can be used for a seamless experience at playing around with the graph.
