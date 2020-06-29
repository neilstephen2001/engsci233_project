# ENGSCI 233: Project
# project_code.py

# Name: Stephen Parinas
# ID: 875329986

# imports
from project_utils import *
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from time import time
from multiprocessing import Pool

def split_rest_homes(network, rest_homes):
    """ Splits the rest homes into four destination lists, one for each courier, depending on their location
	
        Parameters
        ----------
        network : networkx.Graph
            The Auckland public transport network represented as a graph/network
        rest_homes : list
            The list of 143 rest homes in Auckland to be visited
            
        Returns
        -------
        courier_1 : list
            The list of rest homes to be visited by courier 1
        courier_2 : list
            The list of rest homes to be visited by courier 2
        courier_3 : list
            The list of rest homes to be visited by courier 3
        courier_4 : list
            The list of rest homes to be visited by courier 4
            
        Notes
        -----
        The rest homes are divided roughly into the following locations/regions
        But also in such a way that all four couriers would have very similar travel times
            Courier 1 - North Shore  
            Courier 2 - West Auckland  
            Courier 3 - Central Auckland  
            Courier 4 - East/South Auckland  
	"""

    # create empty list for each courier
    courier_1 = []
    courier_2 = []
    courier_3 = []
    courier_4 = []

    # divide rest homes by geography into the four couriers and append to the corresponding destination list
    for rest_home in rest_homes:
        if network.nodes[rest_home]['lat'] > -36.83 and network.nodes[rest_home]['lng'] < 174.67:
            courier_1.append(rest_home)
        elif network.nodes[rest_home]['lat'] > -36.78:
            courier_1.append(rest_home)
        elif network.nodes[rest_home]['lng'] < 174.748:
            courier_2.append(rest_home) 
        elif network.nodes[rest_home]['lng'] < 174.84:
            courier_3.append(rest_home)  
        else:
            courier_4.append(rest_home)
        
    return courier_1, courier_2, courier_3, courier_4


def plot_rest_homes(network, couriers):
    """ Plots the location of the rest homes over an image of the Auckland region
	
        Parameters
        ----------
        network : networkx.Graph
            The Auckland public transport network represented as a graph/network
        couriers : tuple
            The destination lists of the four couriers, containing the rest homes to be visited
            
        Notes
        -----
        Generates a file, 'all_nodes.png', which contains the plotted rest homes
        The colours of the dots depend on the courier list that the rest home is in:
            Courier 1 - cyan, Courier 2 - red, Courier 3 - yellow, Courier 4 - magenta
            Auckland Airport is plotted as a white x
	"""

    # Generate plot
    f,ax = plt.subplots(nrows=1,ncols=1)

    # Reading the image that is to be the background of the plot
    # This is a zoomed in photo of the Auckland region
    img = plt.imread('akl_zoom.png')
    
    # Run through each courier list, plotting different coloured dots for each courier
    for i in range(len(couriers)):
        for rest_home in couriers[i]:
            if i == 0:
                ax.plot(network.nodes[rest_home]['lng'], network.nodes[rest_home]['lat'], 'c.')
            elif i == 1:
                ax.plot(network.nodes[rest_home]['lng'], network.nodes[rest_home]['lat'], 'r.')
            elif i == 2:
                ax.plot(network.nodes[rest_home]['lng'], network.nodes[rest_home]['lat'], 'y.')
            else:
                ax.plot(network.nodes[rest_home]['lng'], network.nodes[rest_home]['lat'], 'm.')

    # Determine and plot the location of Auckland Airport
    airport = [network.nodes['Auckland Airport']['lng'], network.nodes['Auckland Airport']['lat']]
    ax.plot(airport[0], airport[1], 'wx')

    # Setting axes limits 
    ax.imshow(img, extent =[174.48866, 175.001869, -37.09336, -36.69258])

    # Saving the plot as a .png file
    # plt.savefig('all_nodes.png', dpi = 600)


def courier_path(network, courier, path_name):
    """ Determines the shortest path for the courier that visits all rest homes in its destination list, using the nearest-neighbour algorithm
	
        Parameters
        ----------
        network : networkx.Graph
            The Auckland public transport network represented as a graph/network
        courier : list
            The list of rest homes that the courier is to visit
        path_name : str
            The name to be used for the .txt and .png files that are to be generated

        Returns
        -------
        courier_distance : float
            The travel time taken by the courier to visit all the rest homes in its destination list

        Notes
        -----
        The courier must start at Auckland Airport, visit all the rest homes, then finish at Auckland Airport
        
        In addition to determining the courier distance, two files are generated:
            path_name.png is a plot of the path taken by the courier, over a photo of the Auckland region
            path_name.txt contains the list of rest homes in the order they were visited by the courier
            One line for each rest home, and it contains Auckland Airport in both the first and last lines
	"""

    # Starting node is Auckland Airport, preallocate a list for the path and a variable for the distance
    current_node = 'Auckland Airport'
    courier_path = []
    courier_distance = 0

    # Create a new file in which to write the list of rest homes visited
    # then write the starting node name onto the first line 
    fp = open(path_name+'.txt', 'w+')
    fp.write(current_node + '\n')
 
    while len(courier) > 0:

        # Initialise variables to determine the nearest location in the list from the current node
        # then store its distance and path from the current node, and its name
        shortest_distance = np.inf
        nearest_path = None
        nearest_rest_home = None

        # Run through each rest home in the list, determining the shortest path and its path length, from the current node
        for node in courier:
            path = nx.shortest_path(network, current_node, node, weight='weight')
            distance = nx.shortest_path_length(network, current_node, node, weight='weight')

            # Set rest home, and its path and distance, if the distance between it and the current node is 
            # less than the distance to the currently saved nearest rest home
            if distance < shortest_distance:
                shortest_distance = distance
                nearest_path = path
                nearest_rest_home = node
        
        # Extend courier path list to add the path between the current node and the nearest rest home
        # and add the distance between the two to the courier distamce
        courier_path.extend(nearest_path)
        courier_distance += shortest_distance

        # Change current node to that of the nearest rest home, then write this onto a new line in the path_name.txt file
        current_node = nearest_rest_home
        fp.write(current_node + '\n')

        # Remove the rest home from the courier destination list once it has been visited
        # Exit condition of the while loop is when all the rest homes have been visited (list length is zero)
        courier.remove(nearest_rest_home)

    # Determine path and distance from final rest home to Auckland Airport, which is the courier's end node
    airport_path = nx.shortest_path(network, current_node, 'Auckland Airport', weight='weight')
    airport_distance = nx.shortest_path_length(network, current_node, 'Auckland Airport', weight='weight')

    # Extend path list and add distance, from final rest home to Auckland Airport
    courier_path.extend(airport_path)
    courier_distance += airport_distance

    # Write the final destination name onto the file then close it
    fp.write('Auckland Airport')
    fp.close()

    # Plotting the path taken by the courier
    plot_path(network, courier_path, save=path_name+'.png')

    return courier_distance 

    
def main():  
    """ Divides list of Auckland rest homes into four couriers, and for each courier, determines the travel time and path taken to visit all rest homes in its list """

    # Read the Auckland public transport network and the list of rest homes
    akl = read_network('network.graphml')
    rest_homes = get_rest_homes('rest_homes.txt')

    # Split the list of rest homes into four lists 
    couriers = split_rest_homes(akl, rest_homes)

    # Print the number of rest homes that each courier has to visit
    # print('\nCourier 1 has {:d} nodes, Courier 2 has {:d} nodes'.format(len(couriers[0]),len(couriers[1])))
    # print('Courier 3 has {:d} nodes, Courier 4 has {:d} nodes\n'.format(len(couriers[2]),len(couriers[3])))
    
    # Plot the location of the rest homes over a photo of Auckland
    plot_rest_homes(akl, couriers)
    
    # Create the multiprocessing pool, using 4 CPUs (one for each courier path)
    p = Pool(4)

    # Create the list of inputs for each iteration of the courier_path function, which makes use of the nearest neighbour algorithm
    inputs = [[akl, couriers[0], 'path_1'], [akl, couriers[1], 'path_2'], [akl, couriers[2], 'path_3'], [akl, couriers[3], 'path_4']]
    
    # Determining the solution's computation time (parallelised using starmap which allows for multiple inputs)
    t0 = time()
    courier_distances = p.starmap(courier_path, inputs)
    t1 = time()
    
    #print('The travel time of Courier 1 is {:.2f} hours'.format(courier_distances[0]))
    #print('The travel time of Courier 2 is {:.2f} hours'.format(courier_distances[1]))
    #print('The travel time of Courier 3 is {:.2f} hours'.format(courier_distances[2]))
    #print('The travel time of Courier 4 is {:.2f} hours'.format(courier_distances[3]))
    #print('\nThe total time taken to find a solution in parallel (using 4 CPUs) is {:.0f} seconds'.format(t1-t0))

if __name__ == "__main__":
    main()