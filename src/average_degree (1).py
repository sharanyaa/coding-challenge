#!/usr/bin/python3

import sys
from os.path import isfile
from json import loads
from itertools import combinations
from collections import OrderedDict
from time import mktime, strptime

class Graph:
    ''' Graph class is implemented as a dictionary with vertices as keys and a list of neighbor nodes as value's '''
    def __init__ (self, graph_dict = {}):
        # Constructor takes a dictionary as argument, builds a dictionary without disconnected vertices
        # and assigns it to the underlying dict of the class
        self.__graph_dict = graph_dict

    def generate_vertices (self):
        # Returns a list of connected vertices in the graph
        return list(self.__graph_dict.keys())

    def generate_edges (self):
        """ A static method generating the edges of the
            graph "graph". Edges are represented as sets
            with one (a loop back to the vertex) or two
            vertices
        """
        edges = []
        for vertex in self.__graph_dict:
            for neighbour in self.__graph_dict[vertex]:
                if {neighbour, vertex} not in edges:
                    edges.append({vertex, neighbour})
        return edges

    # Used for debugging
    def print_graph(self):
        # Prints the underlying dict of the class
        return (self.__graph_dict)

    def __str__ (self):
        # Prints a list of vertices and edges in the graph
        s = "V: "
        for vertex in self.generate_vertices():
            s += str(vertex) + " "
        s += "\nE: "
        for edge in self.generate_edges():
            s += str(edge) + " "
        return s

    def add_edge (self, edge):
        """ assumes that edge is of type set, tuple or list;
            between two vertices can be multiple edges!
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

    def remove_edge(self, edge):
        edge = set(edge)
        v1 = edge.pop()
        if edge:
            v2 = edge.pop()
        #print (v1, v2)
        try:
            if self.__graph_dict:
                if v1 in self.__graph_dict:
                    self.__graph_dict[v1].remove(v2)
                if v2 in self.__graph_dict:
                    self.__graph_dict[v2].remove(v1)
        except:
            pass

    def evict_old_hashtags(self):
        global oldest_ts
        global tweet_dict
        edges_to_remove = []
        keys = (list(tweet_dict.keys()))
        index = 0
        old_timestamps = []
        while index < len(keys):
            timestamp = keys[index]
            #print (timestamp,"\n"+ str(tweet_dict))
            index += 1
            if timestamp - oldest_ts > 60:
                #print (list(tweet_dict)[0])
                edges_to_remove.extend(tweet_dict[oldest_ts])
                #old_timestamps.append(oldest_ts)
                del tweet_dict[oldest_ts]
                oldest_ts = list(tweet_dict)[0]
            else:
                 continue
        print (timestamp, oldest_ts, "\tedges_remove: "+str(edges_to_remove))
        for edge in edges_to_remove:
            #print (edge)
            self.remove_edge(edge)
        print
       # for ts in old_timestamps:
        #    del tweet_dict[ts]

    def remove_disconnected_nodes(self):
        keys = list(self.__graph_dict.keys())
        for vertex in keys:
            if not self.__graph_dict[vertex]:
                del self.__graph_dict[vertex]

    def calc_avg_degree (self):
        # Returns a formatted string of the average degree of the graph
        n = 0
        deg = 0
        x = "0.00"
        for v in self.__graph_dict:
            n += 1
            deg += len(self.__graph_dict[v])
            f = deg / n
            x = "%.3f" % f
        print (deg, x)
        return x[0:-1]

oldest_ts = None
tweet_graph = Graph()
tweet_dict = {}

def main ():
    global oldest_ts
    global tweet_graph
    global tweet_dict

    s = ""
    text = ""
    #tweet_graph = Graph({"d": ["f"], 2: ["d"], 3: ["f", "d"]})
    #print (tweet_graph.print_graph())
    #tweet_graph.remove_edge({"d", "f"})
    #print (tweet_graph.print_graph())
    #tweet_graph.remove_disconnected_nodes()
    #print (tweet_graph.print_graph())

    opfile = open(sys.argv[2], "w+")
    newest_ts = None
    # Reads input file and writes feauture 1 into output file as specified in cmd arguments
    if (isfile(sys.argv[1])):
        ipfile = open(sys.argv[1], "r")
    else:
        # Terminates if input file path is invalid
        print("Invalid input path: ", sys.argv[1])
        exit(0)
    print ("TWEET INPUT: {0}, OUTPUT: {1}".format(sys.argv[1],sys.argv[2]))
    tweetnum = 0
    for line in ipfile:
        parsed_json = loads(line)
        if "entities" and "created_at" in parsed_json:
            timestamp = parsed_json["created_at"]
            newest_ts = (mktime(strptime(timestamp, "%a %b %d %H:%M:%S +0000 %Y")))
            if oldest_ts == None:
                oldest_ts = newest_ts
            tweetnum+=1
            print ("tweet num: ",tweetnum,"oldest ts: ", oldest_ts,"newest ts: ", newest_ts, "newest - oldest: ", newest_ts - oldest_ts)
            #if newest_ts - oldest_ts < 60:
            if newest_ts >= oldest_ts:
                hashtags = []
                tags = parsed_json["entities"]["hashtags"]
                for hashtag in tags:
                    #text += hashtag["text"] + " "
                    hashtags.append(hashtag["text"])
                hashtags = set(hashtags)
                new_edges = []
                for hashtag in hashtags:
                    new_edges = list(combinations(hashtags, 2))
                try:
                    tweet_dict[newest_ts].extend(new_edges)
                except:
                    tweet_dict[newest_ts] = new_edges
                tweet_graph.evict_old_hashtags()
                tweet_dict = OrderedDict(sorted(tweet_dict.items()))
                tweet_graph.remove_disconnected_nodes()
                if newest_ts - oldest_ts < 60:
                    for edge in new_edges:
                        tweet_graph.add_edge(edge)
            print (tweet_graph.print_graph(), "new edges: ", new_edges)
            print ("\tavg degree: ", tweet_graph.calc_avg_degree(), "\n", tweet_graph)
            print ("\n============================")
            s += (tweet_graph.calc_avg_degree()) + "\n"

            #print ("\n", tweet_graph.print_graph(), tweet_graph)
            # print ("\n"+str(hashtags)+" "+timestamp+"\n============================")
            # s += text + "\tcreated_at: " + timestamp + "\n"
            # print (oldest_ts, newest_ts)
            # print ("\t\tnew edges: " + str(new_edges))

    print (s)
    opfile.write(s)
    # for k in tweet_dict:
    # print (k, " ", tweet_dict[k])

    #print (tweet_graph)
    #print (tweet_graph.generate_edges())
    ipfile.close()
    opfile.close()


# Execution starts here
if __name__ == "__main__":
    main()
