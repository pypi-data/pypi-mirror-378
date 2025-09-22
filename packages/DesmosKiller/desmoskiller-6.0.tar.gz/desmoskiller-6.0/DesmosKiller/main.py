# next lib
#Note: if overrides are smaller than the min or max within the list, they will be ignored. They only work for making the graph larger, so min override must be smaller than the min in list and same for max
import matplotlib.pyplot as plt
import numpy as np


def graph(xlist=None, ylist=None, color=None, shw=None, showAxes=None, showXaxis=None, showYaxis=None, fitToscreen=None, givenYMIN=None, givenYMAX=None, givenXMIN=None, givenXMAX=None): #this doesn't need a parametric version as it supports custom x and y values
    #(it does not generate values, so yeah. Pretty self-explanatory)
    #givenYMIN and givenYMAX are there so you can calculate the max and min y-axis values beforehand so it doesn't get overwritten

    #padding out lists and list data checks
    if (xlist is None) and (ylist is None):
        print("Both lists (x list and y list) are None")
    if (xlist is None):
        xlist = []
        print("x list is None")
        for carrier in range(len(ylist)):
            xlist.append(carrier)
    if (ylist is None):
        ylist = []
        print("y list is None")
        for carrier in range(len(xlist)):
            ylist.append(carrier)
    if len(xlist) != len(ylist):
        print("Error: No x and y values passed or imbalanced lists. Pass two equally-sized arrays for x and y")
        if len(xlist) < len(ylist):#pad out the list
            for carrier in range(len(ylist)-len(xlist)):
                xlist.append(10)
        else:
            for carrier in range(len(xlist)-len(ylist)):
                ylist.append(20)
    #end of padding (now we can calc the mins and maxes and save(cache is the wrong word) the values in a variable (so in RAM))

    #get mins and maxes for x and y axes
    min_x, max_x, min_y, max_y = min(xlist), max(xlist), min(ylist), max(ylist)

    #update lims (we don't know if graph is called or if generate was called, generate has checks for lims in itself. But if it is called by graph() then we have to check, so check either way as )
    if givenYMIN is not None:
        if givenYMIN < min_y:
            min_y = givenYMIN
    if givenYMAX is not None:
        if givenYMAX > max_y:
            max_y = givenYMAX

    if givenXMIN is not None:
        if givenXMIN < min_x:
            min_x = givenXMIN
    if givenXMAX is not None:
        if givenXMAX > max_x:
            max_x = givenXMAX

    #axes showing
    if showXaxis or showAxes:
        x_axis(min_x, max_x)
    if showYaxis or showAxes:
        y_axis(min_y, max_y)

    #fit to screen (limits)
    if not fitToscreen: #rediscovered these lines actually do something (this affects the view of the graph, so how zoomed in or out it is)
        #if no lims are set, the graph will be at max zoom, while still keeping all points within view port. Very useful rediscovery
        if min_y != max_y:
            yrange(min_y, max_y)
            # yrangeauto(ylist) #automatically finds smallest and largest vals instead of manual passing, but does not allow overriding using givenYMAX and givenYMIN
            #(already done min and max in here anyway so it's not needed imo, but there anyway)
        if min_x != max_x:
            xrange(min_x, max_x)
            # xrangeauto(xlist) #no override is given for this. Only givenYMIN and givenYMAX for overriding. Will not add it in. Overriding needs to

    #convert to numpy array
    xcoords = np.array(xlist)
    ycoords = np.array(ylist)

    #check valid color for plot
    if color is None:
        plt.plot(xcoords, ycoords, "red")
    else:
        plt.plot(xcoords, ycoords, color=color)

    #last line, should be anyway afaik maybe, maybe not. But I think you can't edit a plot after showing, or it's bad practice imo anyway
    if shw:
        show()

def plot():
    return("Yeah, this ain't happening chief. Use the built-in one using import matplotlib.pyplot as plt")

def show():
    plt.show()

# lims not needed; check in generate_array_then_graph for the lims. Lims are not needed because they're useless. Just generate values outside the range its calm
def yrangeauto(ylist):
   plt.ylim(min(ylist), max(ylist))
def xrangeauto(xlist):
   plt.xlim(min(xlist), max(xlist))
def xrange(xmin, xmax):
   plt.xlim(xmin, xmax)
def yrange(ymin, ymax):
   plt.ylim(ymin, ymax)

def generate_array_then_graph(minimum_x=None, maximum_x=None, f=None, incrementsperunit=None, color=None, shw=None, showAxes=None, showXaxis=None, showYaxis=None, fitToscreen=None, givenYMIN=None, givenYMAX=None, givenXMIN=None, givenXMAX=None):  # reciprocal step can also be thought of as gradings between 0 and 1. So the gradings is 100 per unit if this is 100
    max_y = -9999999999999999999999999999999999999999999999999999999999  # arbitrary small number, so that the first y value is always larger than this
    min_y = 9999999999999999999999999999999999999999999999999999999999  # arbitrary large number, so that the first y value is always smaller than this
    if str(type(minimum_x)) == "<class 'float'>":
        if str(type(minimum_x)) == "<class 'int'>":
            minimum_x = int(minimum_x)
        else:
            print("missing Min x value  (Unknown Domain Lower Bound [x,..])")
            return ()
    if str(type(maximum_x)) == "<class 'float'>":
        if str(type(maximum_x)) == "<class 'int'>":
            maximum_x = int(maximum_x)
        else:
            print("missing Max x value (Unknown Domain Upper Bound [..,x])")
            return ()
    if f is None:
        print("missing function to generate y axis")
        return ()
    if incrementsperunit is None or incrementsperunit < 1:  # plan is to make parametric using carrier as t and then passing equation of x through
        print("setting default increment to 1 unit")
        incrementsperunit = 1
    # params: color, shw ... fitToscreen are physical, not logical so they're not needed for this step. They will just be passed to graph for final step (delegation)

    min_x = minimum_x
    max_x = maximum_x
    reciprocal_step = incrementsperunit  # so this is a step of 0.01 if reciprocal_step=100. Used to reduce function stepping between values. Use 1 for no stepping
    #smoothing is a default for graphing

    # data generation
    # cartesian only
    coords_x = []
    coords_y = []

    # # first generate and plot x-axis, can be generated beforehand as we have all x values before we have all y values
    # # but don't show the plot yet
    # if showXaxis or showAxes:
    #     x_axis(min_x, max_x)

    for carrier in range((min_x * reciprocal_step), (max_x * reciprocal_step) + 1, 1):  # +1 as the last value is not reached (start, iterations, step)
        # print(carrier)
        x = carrier / reciprocal_step
        coords_x.append(x)
        # merged loops together to perform quicker time
        y = f(x)
        if y > max_y:
            max_y = y
        if y < min_y:
            min_y = y
        coords_y.append(y)  # inside of bracket is the equation

    # # second, generate the y-axis; it has to be generated after all y values are generated, as we need to know the min and max y values to draw the y axis
    # # still don't show the plot yet
    # if showYaxis or showAxes:
    #     y_axis(min_y, max_y)

    # yrange(coords_y)
    # xrange(coords_x)

    #override limits added here as well
    if givenYMIN is not None:
        if givenYMIN < min_y:
            min_y = givenYMIN
    if givenYMAX is not None:
        if givenYMAX > max_y:
            max_y = givenYMAX

    #the minimum x and y as the first two parameters are for the graph generation/for y values. These two are for drawing the x axis
    if givenXMIN is not None:
        if givenXMIN < min_x:
            min_x = givenXMIN
    if givenXMAX is not None:
        if givenXMAX > max_x:
            max_x = givenXMAX


    # then finally graph f(x) using values we generated, and send to graph() which only does plotting. Delegation to reduce repetitive lines
    graph(coords_x, coords_y, color, shw, showAxes, showXaxis, showYaxis, fitToscreen, min_y, max_y, min_x, max_x) #showAxes, showXaxis, showYaxis and fitToscreen are delegated to graph
    #this way the code has less repetition (the calc would have to pass thru graph anyway so make graph do checks etc. for axes and fit)
    #no need to pass: ymin and ymax, they will be recalced anyway for accuracy and consistency in value (reliability)

#does not need to be called manually, so it is not provided in package
def x_axis(minimum_x, maximum_x):  # needed for x-axis, do not change
    graph([minimum_x, maximum_x], [0, 0], "black", False)  # do not change this, either. Gives y=0 to draw the x axis

#does not need to be called manually, so it is not provided in package
def y_axis(minimum_y, maximum_y):  # needed for y-axis, do not change
    graph([0, 0], [minimum_y, maximum_y], "black", False)  # do not change this, either. Gives x=0 to draw the y axis

def generate_array_then_parametric_graph():
    print("Behind the scenes... NOT FINISHED CRTL+C THIS RN")
    #copy code for generate, then just add z axis, and logically rotate by 90 clockwise, y going up, x going into and out, positive is out, and z is now x
    #basically, we just put z instead of x in plot

def test():
    print("program is present and is running--END OF TEST")