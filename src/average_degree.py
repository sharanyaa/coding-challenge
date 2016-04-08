#!/usr/bin/python3

import sys
from os.path import isfile
from json import loads
from itertools import combinations
from collections import OrderedDict
from time import mktime, strptime

class Graph:
    ''' Graph class is implemented as a dictionary with vertices as keys and a list of neighbor nodes as values '''
    def __init__ (self, graph_dict = {}):
        ''' Constructor takes a dictionary as argument. '''
        self.__graph_dict = graph_dict

    def __str__ (self):
        return str(self.__graph_dict)

    def add_edge (self, edge):
        """ edge is of type set, tuple or list;
        Method creates a new list or appends to the list of neighbor nodes for the corresponding vertices
        """
        edge = set(edge)
        vertex1 = edge.pop()
        vertex2 = edge.pop()
        if vertex1 in self.__graph_dict:
            self.__graph_dict[vertex1].append(vertex2)
        else:
            self.__graph_dict[vertex1] = [vertex2]
        if vertex2 in self.__graph_dict:
            self.__graph_dict[vertex2].append(vertex1)
        else:
            self.__graph_dict[vertex2] = [vertex1]
        # Removes duplicates in the list of neighbor nodes to remove duplicate edges in the hashtag graph.
        self.__graph_dict[vertex1] = list(set (self.__graph_dict[vertex1]))
        self.__graph_dict[vertex2] = list(set (self.__graph_dict[vertex2]))

    def remove_edge(self, edge):
        '''
        Method removes an edge from the hashtag graph.
        '''
        global tweet_dict
        # Check if edge is formed by another tweet in the 60 second window.
        # If flag is True, edge can be deleted, if flag is False, do no delete the edge.
        flag = True
        for lst in tweet_dict.values():
            if edge in lst:
                flag = False
        if flag:
            edge = set(edge)
            v1 = edge.pop()
            if edge:
                v2 = edge.pop()
            try:
                if self.__graph_dict:
                    if v1 in self.__graph_dict:
                        self.__graph_dict[v1].remove(v2)
                    if v2 in self.__graph_dict:
                        self.__graph_dict[v2].remove(v1)
            except:
                pass

    def evict_old_hashtags(self):
        '''
        Method removes old hashtags, with a timestamp older the oldest timestamp in the graph;
        '''
        global oldest_ts
        global tweet_dict
        edges_to_remove = []
        keys = (list(tweet_dict.keys()))
        index = 0
        while index < len(keys):
            timestamp = keys[index]
            index += 1
            if timestamp - oldest_ts > 60:
                edges_to_remove.extend(tweet_dict[oldest_ts])
                del tweet_dict[oldest_ts]
                oldest_ts = list(tweet_dict)[0]
            else:
                 continue
        for edge in edges_to_remove:
            self.remove_edge(edge)

    def remove_disconnected_nodes(self):
        '''
        Method removes disconnected nodes by finding vertices with no neighboring nodes.
        '''
        keys = list(self.__graph_dict.keys())
        for vertex in keys:
            if not self.__graph_dict[vertex]:
                del self.__graph_dict[vertex]

    def calc_avg_degree (self):
        '''
        Returns a formatted string of the average degree of the graph
        '''
        n = 0
        deg = 0
        x = "0.00"
        for v in self.__graph_dict:
            n += 1
            deg += len(self.__graph_dict[v])
        try:
            f = deg / n
        except:
            f = 0.000
        x = "%.3f" % f
        #print(f, x)
        return x[0:-1]

# Global Variables
oldest_ts = None # Oldest timestamp in the 60 second window
tweet_graph = Graph() # the twitter hashatg graph
tweet_dict = {} # The tweet_dict dictionary associates edges with the timestamp when they were created;
                # The dictionary is stored in sorted order of keys, which are timestamps.

def process_input_file(ipfile):
    '''
    Function takes an input file path as parameter, processes the tweets,
    constructs an output string to be written into an output file and return the string.
    '''
    global oldest_ts
    global tweet_graph
    global tweet_dict
    s = ""
    for line in ipfile:
        parsed_json = loads (line)
        # If entities is present, it's a tweet;
        # Else, it's a rate limit message which is ignored and no changes are made to the hashtag graph or average degree
        if "entities" in parsed_json and "created_at" in parsed_json:
            # Parse the tweets and timestamp from the input file
            timestamp = parsed_json["created_at"]
            newest_ts = (mktime (strptime (timestamp, "%a %b %d %H:%M:%S +0000 %Y")))
            # For the first tweet:
            if oldest_ts == None:
                oldest_ts = newest_ts
            # We ignore all tweets that are older than the oldest tweet in the 60 second window;
            # Otherwise, determine the possible edges produced by the set of unique hashatgs in each tweet
            # Append the new_edges to tweet_dict using the timestamp as key.
            if newest_ts >= oldest_ts:
                hashtags = []
                if "hashtags" in parsed_json["entities"]:
                    tags = parsed_json["entities"]["hashtags"]
                    for hashtag in tags:
                        if "text" in hashtag:
                            hashtags.append (hashtag["text"])
                    hashtags = set (hashtags)
                    new_edges = []
                    for hashtag in hashtags:
                        new_edges = list (combinations (hashtags, 2))
                    try:
                        tweet_dict[newest_ts].extend (new_edges)
                    except:
                        tweet_dict[newest_ts] = new_edges
                    # Remove the old hashtags in the hashtag graph;
                    # Sort tweet_dict in increasing order of timestamps;
                    # Remove the disconnected nodes in the graph and add the new_edges to the graph
                    tweet_graph.evict_old_hashtags ()
                    tweet_dict = OrderedDict (sorted (tweet_dict.items ()))
                    tweet_graph.remove_disconnected_nodes ()
                    if newest_ts - oldest_ts < 60:
                        for edge in new_edges:
                            tweet_graph.add_edge (edge)
            # Finally append a formatted string of the average degree of the graph to an output string.
            s += (tweet_graph.calc_avg_degree ()) + "\n"
            #print (tweet_graph, "\n")
    return s

def main ():
    s = ""
    newest_ts = None # The newest timestamp has the timestamp of the latest tweet to arrive.

    opfile = open(sys.argv[2], "w+")
    if (isfile(sys.argv[1])):
        ipfile = open(sys.argv[1], "r")
    else:
        # Terminates if input file path is invalid
        print("Invalid input path: ", sys.argv[1])
        exit(0)
    print ("TWEET INPUT: {0}, OUTPUT: {1}".format (sys.argv[1], sys.argv[2]))
    # Call process_input_file and write the output string into the output file.
    output_string = process_input_file(ipfile)
    #print (output_string)
    opfile.write(output_string)
    ipfile.close()
    opfile.close()

if __name__ == '__main__':
    main()