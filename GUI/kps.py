from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, CustomJS, ColumnDataSource, HoverTool, TapTool, PointDrawTool, Button, WheelZoomTool, ResetTool, BoxZoomTool, FileInput, PanTool
import math
from bokeh.layouts import column, row
from bokeh.io import curdoc
from functools import partial
import random
import base64
from math import log

source = ColumnDataSource({'x': [], 'y': []})

p = figure(title="Hover to see coordinates, Click  on the graph to add points. Zoom Options are on the side panel", tools="tap",x_range=(-500,500),y_range=(-500,500), name="jm_plot", width=850)

renderer = p.scatter('x', 'y', size=10, source=source, color='purple')

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

renderers_line=[]
delay_flag=0
def generate_random_points(n):
    global delay_flag,renderers_line
    source.data = {'x': [], 'y': []}
    if(len(renderers_line)!=0):
        for line in renderers_line:
            p.renderers.remove(line) 
    renderers_line=[]
    if n==100:
        delay_flag=1
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
        delay_flag=2
        for i in range(n):
            x = random.randint(-5000, 5000)
            y = random.randint(-5000, 5000)
            source.stream({'x': [x], 'y': [y]})
        p.x_range.start=-5500
        p.x_range.end=5500
        p.y_range.start=-5500
        p.y_range.end=5500
        renderer.glyph.size=5

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

def partition5(arr, left, right):
    for i in range(left+1, right+1):
        j = i
        while(j>left and arr[j-1]>arr[j]):
            arr[j], arr[j-1] = arr[j-1], arr[j]
            j-=1
    return arr[left + (right-left)//2]



def partition(arr, low, high, pivot_value):
    pivot_index=arr.index(pivot_value)
    arr[pivot_index], arr[high] = arr[high], arr[pivot_index]
    i = low
    for j in range(low, high):
        if arr[j] < pivot_value:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[high] = arr[high], arr[i]
    return i

def median_of_medians(arr):
    if len(arr) <= 5:
        return partition5(arr,0,len(arr)-1)
    groups = [arr[i:i+5] for i in range(0, len(arr), 5)]
    medians = [partition5(group,0,len(group)-1) for group in groups]

    return median_of_medians(medians)

def quickselect(arr, low, high, k):
    if low == high:
        return arr[low]
    pivot_index = partition(arr, low, high, median_of_medians(arr[low:high+1]))
    if k == pivot_index:
        return arr[k]
    elif k < pivot_index:
        return quickselect(arr, low, pivot_index - 1, k)
    else:
        return quickselect(arr, pivot_index + 1, high, k)


def find_median_points(points):
    temp=[point[0] for point in points]
    n = len(temp)
    return quickselect(temp, 0, n - 1, n // 2)

def find_median_slope(slopes):
    n = len(slopes)
    if(n%2==0):
        return (quickselect(slopes, 0, n - 1, n // 2)+quickselect(slopes, 0, n - 1, n // 2-1))/2
    else:
        return quickselect(slopes, 0, n - 1, n // 2)

def compute_without_plot():
    global renderers_line
    points = list(zip(source.data['x'], source.data['y']))
    
    if(len(renderers_line)!=0):
        for line in renderers_line:
            p.renderers.remove(line)
    renderers_line=[]

    if len(points) < 3:
        print("At least 3 points are required to form a convex hull")
        return
    
    points=[(point[0],point[1]) for point in points]

    def get_upper_bridge(points, median):
        candidates = []
        if(len(points) == 1):
            return points
        if(len(points) == 2):
            points.sort(key=lambda x: x[0])
            return points

        pairs=[]
        if(len(points)%2 == 0):
            for i in range(0,len(points),2):
                temp=[points[i],points[i+1]]
                temp.sort(key=lambda x:x[0])
                pairs.append(tuple(temp))

        else:
            for i in range(1,len(points),2):
                temp=[points[i],points[i+1]]
                temp.sort(key=lambda x:x[0])
                pairs.append(tuple(temp))
            candidates.append(tuple(points[0]))

        slopes=[]
        temp1=[]
        for pair in pairs:
            pi,pj=pair
            if(pi[0]==pj[0]):
                if(pi[1]>pj[1]):
                    candidates.append(pi)
                else:
                    candidates.append(pj)
            else:
                temp1.append(pair)
                slope = (pi[1]-pj[1])/(pi[0]-pj[0])
                slopes.append(slope)
        if(len(slopes)==0):
            return get_upper_bridge(candidates, median)

        median_slope = find_median_slope(slopes)

        EQUAL = []
        SMALL = []
        LARGE = []

        for pair in pairs:
            pi,pj=pair
            if(pi[0]==pj[0]):
                continue
            slope = (pi[1]-pj[1])/(pi[0]-pj[0])
            if(slope<median_slope):
                SMALL.append(pair)
            elif(slope>median_slope):
                LARGE.append(pair)
            else:
                EQUAL.append(pair)
        
            
        MAX_SLOPE = max([point[1]-median_slope*point[0] for point in points])
        max_set = [point for point in points if abs(point[1]-median_slope*point[0]-MAX_SLOPE)<=1e-9]
        left = min(max_set)
        right = max(max_set)

        if(left[0]<=median and right[0]>median):
            return (left, right)
        elif(right[0]<=median):
            for pair in SMALL:
                candidates.append(pair[0])
                candidates.append(pair[1])
            for pair in EQUAL+LARGE:
                candidates.append(pair[1])
        elif(left[0]>median):
            for pair in LARGE:
                candidates.append(pair[0])
                candidates.append(pair[1])
            for pair in EQUAL+SMALL:
                candidates.append(pair[0])

        return get_upper_bridge(candidates, median)

    def get_upper_hull(pmin, pmax, points):
        if(pmin==pmax):
            return [(tuple(pmin))]
        median=find_median_points(points)

        upper_bridge=get_upper_bridge(points, median)
        if(len(upper_bridge)==1):
            return[pmin, pmax]
        pl, pr = upper_bridge
        if(pl>pr):
            pl, pr = pr, pl

        pointsToLeft=[pl,pmin]
        pointsToRight=[pr,pmax]
        x_left=(pl[0]+pmin[0])//2
        y_left=max(pl[1],pmin[1])+2
        left_distance= (x_left-pmin[0])*(pl[1]-pmin[1])-(y_left-pmin[1])*(pl[0]-pmin[0])

        x_right=(pr[0]+pmax[0])//2
        y_right=max(pr[1],pmax[1])+2
        right_distance= (x_right-pmax[0])*(pr[1]-pmax[1])-(y_right-pmax[1])*(pr[0]-pmax[0])
        for point in points:
            curr_dist_left=(point[0]-pmin[0])*(pl[1]-pmin[1])-(point[1]-pmin[1])*(pl[0]-pmin[0])
            curr_dist_right=(point[0]-pmax[0])*(pr[1]-pmax[1])-(point[1]-pmax[1])*(pr[0]-pmax[0])
            if(curr_dist_left*left_distance>0):
                pointsToLeft.append(point)
            if(curr_dist_right*right_distance>0):
                pointsToRight.append(point)

        upper_hull=[]
        if(pmin!=pl):
            upper_hull+=get_upper_hull(pmin, pl, pointsToLeft)
        else:
            upper_hull.append(pl)
        if(pmax!=pr):
            upper_hull+=get_upper_hull(pr, pmax, pointsToRight)
        else:
            upper_hull.append(pr)
        return upper_hull


    def convexUpperHull(points):
        pmin=(math.inf,-math.inf)
        pmax=(-math.inf,-math.inf)
        for point in points:
            if(point[0]<pmin[0]):
                pmin=point
            elif(point[0]==pmin[0] and point[1]>pmin[1]):
                pmin=point
            if(point[0]>pmax[0]):
                pmax=point
            elif(point[0]==pmax[0] and point[1]>pmax[1]):
                pmax=point
        x_coord=(pmin[0]+pmax[0])//2
        y_coord=max(pmin[1],pmax[1])+2
        ref_dist=(x_coord-pmin[0])*(pmax[1]-pmin[1])-(y_coord-pmin[1])*(pmax[0]-pmin[0])
        points_merge=[pmin,pmax]
        for point in points:
            curr_dist=(point[0]-pmin[0])*(pmax[1]-pmin[1])-(point[1]-pmin[1])*(pmax[0]-pmin[0])
            if(curr_dist*ref_dist>0):
                points_merge.append(point)
        upper_hull = get_upper_hull(pmin, pmax, points_merge)
        upper_hull = list(set(upper_hull))
        upper_hull.sort(key=lambda x: x[0])
    
        return upper_hull

    def convexLowerHull(points):
        points=[(-point[0],-point[1]) for point in points]
        lower_hull=convexUpperHull(points)
        lower_hull=[(-point[0],-point[1]) for point in lower_hull]
        return lower_hull

    def convexHull(points):
        upper_hull=convexUpperHull(points)
        lower_hull=convexLowerHull(points)

        if(upper_hull[-1]==lower_hull[0]):
            del upper_hull[-1]
        if(upper_hull[0]==lower_hull[-1]):
            del lower_hull[-1]

        return upper_hull+lower_hull
    
    convex_hull=convexHull(points)

    renderers_line.append(p.scatter(x=[point[0] for point in convex_hull],y=[point[1] for point in convex_hull],color='blue',size=renderer.glyph.size))
    for i in range(len(convex_hull)):
        line=p.line(x=[convex_hull[i][0],convex_hull[(i+1)%len(convex_hull)][0]],y=[convex_hull[i][1],
            convex_hull[(i+1)%len(convex_hull)][1]],line_color="green",line_width=2)
        renderers_line.append(line)

median_list=[]
count=0
delay_time=400
queued_functions=[]

def plot_median_with_delay(x_coord):
    global queued_functions,count,delay_time
    def plot_median(x_coord):
        global median_list,renderers_line,skip_flag
        if skip_flag:
            return
        median_line=p.line([x_coord,x_coord],[p.y_range.start, p.y_range.end] ,color='purple', line_width=2, alpha=0.5)
        median_list.append(median_line)
        renderers_line.append(median_line)
    
    tid=curdoc().add_timeout_callback(partial(plot_median,x_coord),count*delay_time)
    queued_functions.append(tid)

def remove_median(line):
    global renderers_line,skip_flag
    if skip_flag:
        return
    renderers_line.remove(line[-1])
    p.renderers.remove(line[-1])

def plot_upper_lower_with_delay(x_coords,y_coords):
    global queued_functions,count,delay_time
    def plot_upper_lower(x_coords,y_coords):
        global renderers_line,skip_flag
        if skip_flag:
            return
        line=p.line(x=x_coords,y=y_coords,line_color="green",line_width=2)
        renderers_line.append(line)
    tid=curdoc().add_timeout_callback(partial(plot_upper_lower,x_coords,y_coords),count*delay_time)
    queued_functions.append(tid)

separators=[]

def plot_separator_with_delay(x_coords,y_coords):
    global queued_functions,count,delay_time
    def plot_seperator(x_coords,y_coords):
        global renderers_line,separators,skip_flag
        if skip_flag:
            return
        line=p.line(x=x_coords,y=y_coords,line_color="green",line_width=2)
        separators.append(line)
        renderers_line.append(line)
    tid=curdoc().add_timeout_callback(partial(plot_seperator,x_coords,y_coords),count*delay_time)
    queued_functions.append(tid)

def remove_seperator(line):
    global renderers_line,skip_flag
    if skip_flag:
        return
    renderers_line.remove(line[-1])
    p.renderers.remove(line[-1])

connections1=[]
connections2=[]
def plot_connections_with_delay(x1,y1,x2,y2):
    global queued_functions,count,delay_time
    def plot_connections(x1,y1,x2,y2):
        global renderers_line,connections1,connections2,skip_flag
        if skip_flag:
            return
        line1=p.line(x=x1,y=y1,line_color="blue",line_width=2)
        line2=p.line(x=x2,y=y2,line_color="blue",line_width=2)
        connections1.append(line1)
        connections2.append(line2)
        renderers_line.append(line1)
        renderers_line.append(line2)
    tid=curdoc().add_timeout_callback(partial(plot_connections,x1,y1,x2,y2),count*delay_time)
    queued_functions.append(tid)

def remove_connections(line1,line2):
    global renderers_line,skip_flag
    if skip_flag:
        return
    renderers_line.remove(line1[-1])
    renderers_line.remove(line2[-1])
    p.renderers.remove(line1[-1])
    p.renderers.remove(line2[-1])

def plot_bridge_with_delay(x_coords,y_coords):
    global queued_functions,count,delay_time
    def plot_bridge(x_coords,y_coords):
        global renderers_line,skip_flag
        if skip_flag:
            return
        line=p.line(x=x_coords,y=y_coords,line_color="green",line_width=2)
        renderers_line.append(line)
    tid=curdoc().add_timeout_callback(partial(plot_bridge,x_coords,y_coords),count*delay_time)
    queued_functions.append(tid)

left_right_lines=[]
def plot_left_right_with_delay(x_coords,y_coords):
    global queued_functions,count,delay_time
    def plot_left_right(x_coords,y_coords):
        global renderers_line,left_right_lines,skip_flag
        if skip_flag:
            return
        line=p.line(x=x_coords,y=y_coords,line_color="black",line_width=2)
        left_right_lines.append(line)
        renderers_line.append(line)
    tid=curdoc().add_timeout_callback(partial(plot_left_right,x_coords,y_coords),count*delay_time)
    queued_functions.append(tid)

def remove_left_right(line):
    global renderers_line,skip_flag
    if skip_flag:
        return
    renderers_line.remove(line[-1])
    p.renderers.remove(line[-1])

slope_plots=[]

def plot_slope_with_delay(points, median_slope, flag):
    global queued_functions,count,delay_time
    def plot_slope(points, median_slope, flag):
        global renderers_line, slope_plots,skip_flag
        if skip_flag:
            return
        temp=[]
        x=abs(p.x_range.end-p.x_range.start)
        x=x//10
        for point in points:
            x_values=[point[0]-x,point[0]+x]
            y_values=[point[1]+median_slope*(x-point[0]) for x in x_values]
            if flag:
                line=p.line(x_values,y_values, line_color='red', line_width=1)
            else:
                line=p.line([-x for x in x_values],[-y for y in y_values], line_color='red', line_width=1)
            temp.append(line)
            renderers_line.append(line)
        slope_plots.append(temp)
    tid=curdoc().add_timeout_callback(partial(plot_slope,points,median_slope,flag),count*delay_time)
    queued_functions.append(tid)

def remove_slope_plots(line):
    global renderers_line,skip_flag
    if skip_flag:
        return
    for plot in line[-1]:
        p.renderers.remove(plot)
        renderers_line.remove(plot)

def plot_active_points_with_delay(points,flag,colour):
    global queued_functions,count,delay_time
    def plot_active_points(points,flag):
        global renderers_line,skip_flag
        if skip_flag:
            return
        if flag:
            active=p.scatter([p[0] for p in points], [p[1] for p in points], color = colour, size=renderer.glyph.size)
        else:
            active=p.scatter([-p[0] for p in points], [-p[1] for p in points], color = colour, size=renderer.glyph.size)
        renderers_line.append(active)
    tid=curdoc().add_timeout_callback(partial(plot_active_points,points,flag),count*delay_time)
    queued_functions.append(tid)


def compute_convex_hull():
    global renderers_line, count, delay_time, slope_plots, left_right_lines, connections1, connections2, median_list, separators, delay_flag, queued_functions,skip_flag
    def get_upper_bridge(points, median,flag):
        global count,delay_time,slope_plots,left_right_lines, queued_functions
        candidates = []
        if(len(points) == 1):
            return points
        if(len(points) == 2):
            points.sort(key=lambda x: x[0])
            return points

        pairs=[]
        if(len(points)%2 == 0):
            for i in range(0,len(points),2):
                temp=[points[i],points[i+1]]
                temp.sort(key=lambda x:x[0])
                pairs.append(tuple(temp))

        else:
            for i in range(1,len(points),2):
                temp=[points[i],points[i+1]]
                temp.sort(key=lambda x:x[0])
                pairs.append(tuple(temp))
            candidates.append(tuple(points[0]))

        slopes=[]
        temp1=[]
        for pair in pairs:
            pi,pj=pair
            if(pi[0]==pj[0]):
                if(pi[1]>pj[1]):
                    candidates.append(pi)
                else:
                    candidates.append(pj)
            else:
                temp1.append(pair)
                slope = (pi[1]-pj[1])/(pi[0]-pj[0])
                slopes.append(slope)
        if(len(slopes)==0):
            return get_upper_bridge(candidates, median)

        median_slope = find_median_slope(slopes)

        EQUAL = []
        SMALL = []
        LARGE = []

        for pair in pairs:
            pi,pj=pair
            if(pi[0]==pj[0]):
                continue
            slope = (pi[1]-pj[1])/(pi[0]-pj[0])
            if(slope<median_slope):
                SMALL.append(pair)
            elif(slope>median_slope):
                LARGE.append(pair)
            else:
                EQUAL.append(pair)
        
            
        MAX_SLOPE = max([point[1]-median_slope*point[0] for point in points])
        max_set = [point for point in points if abs(point[1]-median_slope*point[0]-MAX_SLOPE)<=1e-9]
        left = min(max_set)
        right = max(max_set)

        tid=plot_slope_with_delay(points, median_slope, flag)
        count+=1
        queued_functions.append(tid)

        tid=curdoc().add_timeout_callback(partial(remove_slope_plots,slope_plots),count*delay_time)
        count+=1
        queued_functions.append(tid)

        if flag:
            plot_left_right_with_delay([left[0],right[0]],[left[1],right[1]])
        else:
            plot_left_right_with_delay([-left[0],-right[0]],[-left[1],-right[1]])
        count+=1

        tid=curdoc().add_timeout_callback(partial(remove_left_right,left_right_lines),count*delay_time)
        count+=1
        queued_functions.append(tid)

        if(left[0]<=median and right[0]>median):
            return (left, right)
        elif(right[0]<=median):
            for pair in SMALL:
                candidates.append(pair[0])
                candidates.append(pair[1])
            for pair in EQUAL+LARGE:
                candidates.append(pair[1])
        elif(left[0]>median):
            for pair in LARGE:
                candidates.append(pair[0])
                candidates.append(pair[1])
            for pair in EQUAL+SMALL:
                candidates.append(pair[0])

        return get_upper_bridge(candidates, median,flag)

    def get_upper_hull(pmin, pmax, points,flag):
        global count,delay_time,connections1,connections2,median_list,queued_functions
        if(pmin==pmax):
            return [(tuple(pmin))]
        median=find_median_points(points)

        if flag:
            # median_line=plt.axvline(x=median, color='green')
            plot_median_with_delay(median)
        else:
            # median_line=plt.axvline(x=-median, color='green')
            plot_median_with_delay(-median)
        count+=1
        # plt.pause(0.5)
        upper_bridge=get_upper_bridge(points, median,flag)
        if(len(upper_bridge)==1):
            return[pmin, pmax]
        pl, pr = upper_bridge
        if(pl>pr):
            pl, pr = pr, pl

        if flag:
            # bridge=plt.plot([pl[0],pr[0]],[pl[1],pr[1]],color="green")
            plot_bridge_with_delay([pl[0],pr[0]],[pl[1],pr[1]])
        else:
            # bridge=plt.plot([-pl[0],-pr[0]],[-pl[1],-pr[1]],color="green")
            plot_bridge_with_delay([-pl[0],-pr[0]],[-pl[1],-pr[1]])
        count+=1
        # plt.pause(0.5)
        pointsToLeft=[pl,pmin]
        pointsToRight=[pr,pmax]
        x_left=(pl[0]+pmin[0])//2
        y_left=max(pl[1],pmin[1])+2
        left_distance= (x_left-pmin[0])*(pl[1]-pmin[1])-(y_left-pmin[1])*(pl[0]-pmin[0])

        x_right=(pr[0]+pmax[0])//2
        y_right=max(pr[1],pmax[1])+2
        right_distance= (x_right-pmax[0])*(pr[1]-pmax[1])-(y_right-pmax[1])*(pr[0]-pmax[0])
        for point in points:
            curr_dist_left=(point[0]-pmin[0])*(pl[1]-pmin[1])-(point[1]-pmin[1])*(pl[0]-pmin[0])
            curr_dist_right=(point[0]-pmax[0])*(pr[1]-pmax[1])-(point[1]-pmax[1])*(pr[0]-pmax[0])
            if(curr_dist_left*left_distance>0):
                pointsToLeft.append(point)
            if(curr_dist_right*right_distance>0):
                pointsToRight.append(point)
        
        if flag:
            plot_connections_with_delay([pl[0],pmin[0]],[pl[1],pmin[1]],[pr[0],pmax[0]],[pr[1],pmax[1]])

        else:
            plot_connections_with_delay([-pl[0],-pmin[0]],[-pl[1],-pmin[1]],[-pr[0],-pmax[0]],[-pr[1],-pmax[1]])

        plot_active_points_with_delay(pointsToLeft,flag,'blue')
        plot_active_points_with_delay(pointsToRight,flag,'blue')
        count+=1

        upper_hull=[]
        
        plot_active_points_with_delay(pointsToLeft,flag,'pink')
        plot_active_points_with_delay(pointsToRight,flag,'pink')
        tid=curdoc().add_timeout_callback(partial(remove_connections,connections1,connections2),count*delay_time)
        count+=1
        queued_functions.append(tid)
        # remove_connections()
        tid=curdoc().add_timeout_callback(partial(remove_median,median_list),count*delay_time)
        count+=1
        queued_functions.append(tid)
        # remove_median()
        if(pmin!=pl):
            upper_hull+=get_upper_hull(pmin, pl, pointsToLeft,flag)
        else:
            upper_hull.append(pl)
        if(pmax!=pr):
            upper_hull+=get_upper_hull(pr, pmax, pointsToRight,flag)
        else:
            upper_hull.append(pr)
        return upper_hull


    def convexUpperHull(points,flag):
        global count,delay_time,separators,queued_functions
        pmin=(math.inf,-math.inf)
        pmax=(-math.inf,-math.inf)
        for point in points:
            if(point[0]<pmin[0]):
                pmin=point
            elif(point[0]==pmin[0] and point[1]>pmin[1]):
                pmin=point
            if(point[0]>pmax[0]):
                pmax=point
            elif(point[0]==pmax[0] and point[1]>pmax[1]):
                pmax=point
        if flag:
            # separator=plt.plot([pmin[0],pmax[0]],[pmin[1],pmax[1]],color="red")
            plot_separator_with_delay([pmin[0],pmax[0]],[pmin[1],pmax[1]])
        else:
            # separator=plt.plot([-pmin[0],-pmax[0]],[-pmin[1],-pmax[1]],color="red")
            plot_separator_with_delay([-pmin[0],-pmax[0]],[-pmin[1],-pmax[1]])
        count+=1
        # plt.pause(0.5)
        
        x_coord=(pmin[0]+pmax[0])//2
        y_coord=max(pmin[1],pmax[1])+2
        ref_dist=(x_coord-pmin[0])*(pmax[1]-pmin[1])-(y_coord-pmin[1])*(pmax[0]-pmin[0])
        points_merge=[pmin,pmax]
        for point in points:
            curr_dist=(point[0]-pmin[0])*(pmax[1]-pmin[1])-(point[1]-pmin[1])*(pmax[0]-pmin[0])
            if(curr_dist*ref_dist>0):
                points_merge.append(point)

        plot_active_points_with_delay(points_merge,flag,'pink')    

        upper_hull = get_upper_hull(pmin, pmax, points_merge,flag)
        upper_hull = list(set(upper_hull))
        upper_hull.sort(key=lambda x: x[0])

        # separator.pop().remove()
        tid=curdoc().add_timeout_callback(partial(remove_seperator,separators),count*delay_time)
        count+=1
        queued_functions.append(tid)
        plot_active_points_with_delay(points_merge,flag,'purple')
        count+=1
        # remove_seperator()
        # active.remove()

        return upper_hull

    def convexLowerHull(points,flag):
        points=[(-point[0],-point[1]) for point in points]
        lower_hull=convexUpperHull(points,flag)
        lower_hull=[(-point[0],-point[1]) for point in lower_hull]
        return lower_hull

    def convexHull(points):
        global count
        upper_hull=convexUpperHull(points,True)
        lower_hull=convexLowerHull(points,False)

        if(upper_hull[-1]==lower_hull[0]):
            del upper_hull[-1]
        else:
            # plt.plot([upper_hull[-1][0],lower_hull[0][0]],[upper_hull[-1][1],lower_hull[0][1]],color='green')
            plot_upper_lower_with_delay([upper_hull[-1][0],lower_hull[0][0]],[upper_hull[-1][1],lower_hull[0][1]])
            count+=1
        if(upper_hull[0]==lower_hull[-1]):
            del lower_hull[-1]
        else:
            # plt.plot([upper_hull[0][0],lower_hull[-1][0]],[upper_hull[0][1],lower_hull[-1][1]],color='green')
            plot_upper_lower_with_delay([upper_hull[0][0],lower_hull[-1][0]],[upper_hull[0][1],lower_hull[-1][1]])
            count+=1
        
        return upper_hull+lower_hull
    
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
    points = list(zip(source.data['x'], source.data['y']))
    if len(points) < 3:
        print("At least 3 points are required to form a convex hull")
        return

    skip_flag=False
    count=0
    connections1=[]
    connections2=[]
    median_list=[]
    separators=[]
    slope_plots=[]
    left_right_lines=[]
    delay_time=400

    if(len(renderers_line)!=0):
        for line in renderers_line:
            p.renderers.remove(line)
    renderers_line=[]   

    points=[(point[0],point[1]) for point in points]

    # if(100>len(points)>50):
    #     delay_time=350
    # elif(len(points)>100):
    #     flag=1
    # elif(1000>len(points)>500):
    #     delay_time=200
    # elif(len(points)>1000):
    #     flag=2

    # if delay_flag==1:
    #     delay_time=300
    # elif delay_flag==2:
    #     delay_time=150

    convex_hull=convexHull(points)
    tid=curdoc().add_timeout_callback(partial(plot_hull_points,convex_hull), count*delay_time)
    queued_functions.append(tid)
    count+=1
    tid=curdoc().add_timeout_callback(set_button_disabled, count*delay_time)
    queued_functions.append(tid)
    count=0

def plot_hull_points(points):
    global renderers_line
    renderers_line.append(p.scatter(x=[point[0] for point in points],y=[point[1] for point in points],color='blue',size=renderer.glyph.size))

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

skip_flag=False

def skip_execution():
    global queued_functions,skip_flag

    skip_flag=True
    for tid in queued_functions:
        try:
            curdoc().remove_timeout_callback(tid)
            queued_functions.remove(tid)
        except ValueError:
            queued_functions.remove(tid)
            continue
    while(queued_functions!=[]):
        for timeoutId in queued_functions:
            try:
                curdoc().remove_timeout_callback(timeoutId)
                queued_functions.remove(timeoutId)
            except ValueError:
                queued_functions.remove(timeoutId)
                continue
    queued_functions=[]
    compute_without_plot()
    set_button_disabled()



submit_button = Button(label="Generate Convex Hull", button_type="success")
submit_button.on_click(compute_convex_hull)

show_solution = Button(label="Show Solution", button_type="light")
show_solution.on_click(compute_without_plot)

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

temp=row(submit_button,skip_visualiastion,generate_hundred_points,generate_thousand_points,show_solution, clear_button, width=850, sizing_mode="stretch_width")
# Set up layout
temp1=row(file_input)
layout = column(temp1,p, temp,width=850)

# Add layout to current document
curdoc().add_root(layout)