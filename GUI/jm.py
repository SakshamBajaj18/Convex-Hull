from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, CustomJS, ColumnDataSource, HoverTool, TapTool, PointDrawTool, Button, WheelZoomTool, ResetTool, BoxZoomTool, FileInput, PanTool
import math
from bokeh.layouts import column, row
from bokeh.io import curdoc
from functools import partial
import random
import base64
from math import log

#Create a sample data source
# initial_points = {'x': [0], 'y': [0]}
source = ColumnDataSource({'x': [], 'y': []})

# Create a figure
p = figure(title="Hover to see coordinates, Click  on the graph to add points. Zoom Options are on the side panel", tools="tap",x_range=(-500,500),y_range=(-500,500), name="jm_plot", width=850)

# Add a circle renderer with hover and tap tool
renderer = p.scatter('x', 'y', size=10, source=source, color='purple')

# Add hover tool
hover = HoverTool(renderers=[renderer],
                  tooltips=[('X', '@x'), ('Y', '@y')],
                  mode='mouse')
p.add_tools(hover)

draw_tool = PointDrawTool(renderers=[renderer], empty_value='black')
p.add_tools(draw_tool)

# Add wheel zoom, reset and box zoom tools
p.add_tools(WheelZoomTool())
p.add_tools(ResetTool(name="Reset Zoom"))
p.add_tools(BoxZoomTool())
p.add_tools(PanTool())


def generate_random_points(n):
    global flag,renderers_line
    source.data = {'x': [], 'y': []}
    if(len(renderers_line)!=0):
        for line in renderers_line:
            p.renderers.remove(line) 
    renderers_line=[]
    if n==100:
        flag=1
        for i in range(n):
            x = random.randint(-500, 500)
            y = random.randint(-500, 500)
            source.stream({'x': [x], 'y': [y]})
        p.x_range.start=-600
        p.x_range.end=600
        p.y_range.start=-600
        p.y_range.end=600
        renderer.glyph.size=10
    elif n==1000:
        flag=2
        for i in range(n):
            x = random.randint(-5000, 5000)
            y = random.randint(-5000, 5000)
            source.stream({'x': [x], 'y': [y]})
        p.x_range.start=-5500
        p.x_range.end=5500
        p.y_range.start=-5500
        p.y_range.end=5500
        renderer.glyph.size=5

def distance(p1, p2):
  dx = p2[0] - p1[0]
  dy = p2[1] - p1[1]
  return math.sqrt(dx**2 + dy**2)

def checkCounterClockWise(p1, p2, p3):
  return (p2[1] - p1[1]) * (p3[0] - p2[0]) - (p2[0] - p1[0]) * (p3[1] - p2[1])

renderers_line = []
line1=[]
line2=[]
line3=[]
count=0
delay_time=50
flag=0
queued_functions=[]
skip_flag=False
def remove_dashed_lines(line):
    global renderers_line,delay_time,skip_flag
    if(skip_flag==True):
        return
    renderers_line.remove(line[0])
    p.renderers.remove(line.pop(0))


def draw_dashed_with_delay(x_coords, y_coords,colour):
    global line1,line2,line3,count,renderers_line,delay_time,queued_functions,skip_flag
    def draw_dashed_line(x_coords, y_coords,colour):
        global skip_flag
        if(skip_flag==True):
            return
        line_renderer=p.line(x_coords, y_coords, line_color=colour, line_width=2, line_dash="dashed")
        if(colour=="green"):
            line3.append(line_renderer)
        elif(colour=="blue"):
            line1.append(line_renderer)
        elif(colour=="black"):
            line2.append(line_renderer)
        renderers_line.append(line_renderer)

   
    timeoutId= curdoc().add_timeout_callback(partial(draw_dashed_line,x_coords, y_coords,colour), count*delay_time)
    queued_functions.append(timeoutId)

def draw_solid_line(x_coords, y_coords):
    global count,renderers_line,delay_time,queued_functions,skip_flag
    def draw_with_delay(x_coords, y_coords):
        global skip_flag
        if(skip_flag==True):
            return
        solid_line=p.line(x_coords, y_coords, line_color="green", line_width=2)
        renderers_line.append(solid_line)
    timeoutId=curdoc().add_timeout_callback(partial(draw_with_delay,x_coords, y_coords), count*delay_time)
    queued_functions.append(timeoutId)

def jarvis_march(points):
    global line1,line2,line3,count,renderers_line,delay_time,queued_functions
    renderers_line = []
    if len(points) <= 2:
        return points

    hull = []
    start = min(points)
    current = start
    while True:
        hull.append(current)
        next_point = points[0]
        # line3 = plt.plot([current[0], next_point[0]], [current[1], next_point[1]], color = 'green', linestyle = 'dashed')
        
        draw_dashed_with_delay([current[0], next_point[0]], [current[1], next_point[1]],"green")
        count+=1
        # plt.pause(0.01)
        for point in points[1:]:
            if point == current:
                continue
            # line1 = plt.plot([current[0], next_point[0]], [current[1], next_point[1]], color = 'blue', linestyle = 'dashed')
            draw_dashed_with_delay([current[0], next_point[0]], [current[1], next_point[1]],"blue")
            count+=1
            # plt.pause(0.05)
            # line2 = plt.plot([point[0], next_point[0]], [point[1], next_point[1]], color = 'black', linestyle = 'dashed')
            draw_dashed_with_delay([point[0], next_point[0]], [point[1], next_point[1]],"black")
            count+=1
            # plt.pause(0.05)
            turn = checkCounterClockWise(current, next_point, point)  
            if turn < 0 or (turn == 0 and distance(current, point) > distance(current, next_point)):
                # line3.pop().remove()
                timeoutId1=curdoc().add_timeout_callback(partial(remove_dashed_lines,line3),count*delay_time)
                queued_functions.append(timeoutId1)
                count+=1 
                # line3 = plt.plot([current[0], next_point[0]], [current[1], next_point[1]], color = 'green', linestyle = 'dashed')
                draw_dashed_with_delay([current[0], next_point[0]], [current[1], next_point[1]],"green")
                count+=1
                # plt.pause(0.05)
                
                next_point = point
            # line1.pop().remove()
            # line2.pop().remove()
            timeoutId3= curdoc().add_timeout_callback(partial(remove_dashed_lines,line1),count*delay_time)
            queued_functions.append(timeoutId3)
            count+=1
            timeoutId4= curdoc().add_timeout_callback(partial(remove_dashed_lines,line2),count*delay_time)
            queued_functions.append(timeoutId4)
            count+=1
        timeoutId2=curdoc().add_timeout_callback(partial(remove_dashed_lines,line3),count*delay_time)
        queued_functions.append(timeoutId2)
        count+=1
        draw_solid_line([current[0], next_point[0]], [current[1], next_point[1]])
        count+=1
        
        # plt.pause(0.05)
        current = next_point 
        if current == start:
            break
    return hull

def set_button_disabled():
    clear_button.disabled = False
    clear_button.button_type = "danger"
    submit_button.disabled = False
    submit_button.button_type = "success"
    show_solution.disabled = False
    show_solution.button_type = "light"
    generate_hundred_points.disabled = False
    generate_hundred_points.button_type = "light"
    generate_thousand_points.disabled = False
    generate_thousand_points.button_type = "light"

def compute_convex_hull():
    submit_button.disabled = True
    submit_button.button_type = "warning"
    clear_button.disabled = True
    clear_button.button_type = "warning"
    show_solution.disabled = True
    show_solution.button_type = "warning"
    generate_hundred_points.disabled = True
    generate_hundred_points.button_type = "warning"
    generate_thousand_points.disabled = True
    generate_thousand_points.button_type = "warning"
    global count, line1, line2, line3,renderers_line,delay_time,flag,skip_flag,queued_functions
    skip_flag=False
    points = list(zip(source.data['x'], source.data['y']))
    
    if len(points) < 3:
        print("At least 3 points are required to form a convex hull")
        set_button_disabled()
        return
    
    points=[(point[0],point[1]) for point in points]
    delay_time=50
    if(100>len(points)>50):
        delay_time=50
    elif(len(points)>100):
        flag=1
    elif(1000>len(points)>500):
        delay_time=2.5
    elif(len(points)>1000):
        flag=2

    if(len(renderers_line)!=0):
        for line in renderers_line:
            p.renderers.remove(line)
    renderers_line=[]   

    count = 0
    line1 = []
    line2 = []
    line3 = []
    if(flag==1):
        delay_time=10
    elif(flag==2):
        delay_time=0.5
    convex_hull_points = jarvis_march(points)
    tid=curdoc().add_timeout_callback(partial(plot_hull_points,convex_hull_points), count*delay_time)
    count+=1
    queued_functions.append(tid)
    tid=curdoc().add_timeout_callback(set_button_disabled, count*delay_time)
    queued_functions.append(tid)
    count=0
    delay_time=0

def plot_hull_points(points):
    global renderers_line
    renderers_line.append(p.scatter(x=[point[0] for point in points],y=[point[1] for point in points],color='blue',size=renderer.glyph.size))

def compute_convex_hull_without_plot():
    global renderers_line
    points = list(zip(source.data['x'], source.data['y']))
    
    if len(points) < 3:
        print("At least 3 points are required to form a convex hull")
        return
    
    points=[(point[0],point[1]) for point in points]
    if(len(renderers_line)!=0):
            for line in renderers_line:
                p.renderers.remove(line)
    renderers_line=[]
    def jarvis_march_without_plot(points):
        if len(points) <= 2:
            return points

        hull = []
        start = min(points)
        current = start

        while True:
            hull.append(current)
            next_point = points[0]
            for point in points[1:]:
                if point == current:
                    continue
                turn = checkCounterClockWise(current, next_point, point)  
                if turn < 0 or (turn == 0 and distance(current, point) > distance(current, next_point)):
                    next_point = point
            current = next_point 
            if current == start:
                break
        return hull

    convex_hull=jarvis_march_without_plot(points)
    renderers_line.append(p.scatter(x=[point[0] for point in convex_hull],y=[point[1] for point in convex_hull],color='blue',size=renderer.glyph.size))
    for i in range(len(convex_hull)):
        line=p.line(x=[convex_hull[i][0],convex_hull[(i+1)%len(convex_hull)][0]],y=[convex_hull[i][1],
            convex_hull[(i+1)%len(convex_hull)][1]],line_color="green",line_width=2)
        renderers_line.append(line)

def clear_canvas():
    global renderers_line
    source.data = {'x': [], 'y': []}
    if(len(renderers_line)!=0):
        for line in renderers_line:
            p.renderers.remove(line) 
    renderers_line=[]
    p.x_range.start=-500
    p.x_range.end=500
    p.y_range.start=-500
    p.y_range.end=500
    renderer.glyph.size=10

def file_callback(attr, old, new):
    global renderers_line
    decoded=base64.b64decode(new)
    decoded=decoded.decode('utf-8')
    data=decoded.split('\n')
    x=[]
    y=[]
    for i in range(len(data)):
        if(data[i]==''):
            continue
        temp=data[i].split(',')
        if(temp[0]=='\r' or temp[0]=='' or temp[1]==''):
            continue
        x.append(float(temp[0]))
        y.append(float(temp[1]))
    source.data = {'x': x, 'y': y}
    min_x=min(x)
    max_x=max(x)
    min_y=min(y)
    max_y=max(y)
    print(min_x,max_x,min_y,max_y)
    temp1=int(log(abs(min_x),10))
    temp2=int(log(abs(max_x),10))
    temp3=int(log(abs(min_y),10))
    temp4=int(log(abs(max_y),10))
    p.x_range.start=min(min_x-5*(10**(temp1-1)),min_x-20)
    p.x_range.end=max(max_x+5*(10**(temp2-1)),max_x+20)
    p.y_range.start=min(min_y-5*(10**(temp3-1)),min_y-20)
    p.y_range.end=max(max_y+5*(10**(temp4-1)),max_y+20)
    if(len(renderers_line)!=0):
        for line in renderers_line:
            p.renderers.remove(line)
    renderers_line=[]

def skip_execution():
    global skip_flag,queued_functions
    skip_flag=True
    
    for timeoutId in queued_functions:
        try:
            curdoc().remove_timeout_callback(timeoutId)
            queued_functions.remove(timeoutId)
        except ValueError:
            queued_functions.remove(timeoutId)
            continue
    while(queued_functions!=[]):
        for timeoutId in queued_functions:
            try:
                curdoc().remove_timeout_callback(timeoutId)
                queued_functions.remove(timeoutId)
            except ValueError:
                queued_functions.remove(timeoutId)
                continue
    convex_hull=compute_convex_hull_without_plot()
    set_button_disabled()

# Create a submit button
submit_button = Button(label="Generate Convex Hull", button_type="success")
submit_button.on_click(compute_convex_hull)

show_solution = Button(label="Show Solution", button_type="light")
show_solution.on_click(compute_convex_hull_without_plot)

generate_hundred_points = Button(label="Generate 100 Random Points", button_type="light")
generate_hundred_points.on_click(partial(generate_random_points, 100))

generate_thousand_points=Button(label="Generate 1000 Random Points", button_type="light")
generate_thousand_points.on_click(partial(generate_random_points, 1000))

clear_button = Button(label="Clear", button_type="danger")
clear_button.on_click(clear_canvas)

file_input = FileInput(accept=".txt,.csv", styles={'color': 'black'})
file_input.on_change('value', file_callback)

skip_visualiastion=Button(label="Skip Visualisation",button_type="light")
skip_visualiastion.on_click(skip_execution)

temp=row(submit_button, skip_visualiastion,generate_hundred_points,generate_thousand_points,show_solution, clear_button, width=850, sizing_mode="stretch_width")
# Set up layout
temp1=row(file_input)
layout = column(temp1,p, temp,width=850)

# Add layout to current document
curdoc().add_root(layout)

