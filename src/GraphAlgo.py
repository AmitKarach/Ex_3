import json
import sys
from typing import List
import queue
from src.DiGraph import DiGraph
from src.GraphAlgoInterface import GraphAlgoInterface
from src.GraphInterface import GraphInterface
from src.Node import Node


class GraphAlgo(GraphAlgoInterface):
    """This abstract class represents an interface of a graph."""

    def __init__(self, g:DiGraph=DiGraph()):
        self.graph = g


    def get_graph(self) -> GraphInterface:
        return self.graph


    def load_from_json(self, file_name: str) -> bool:
        try:
            with open (file_name,'r') as file:
               g= json.load(file)
               nodes = g['Nodes']
               edges = g['Edges']
               for n in nodes:
                   self.graph.add_node(n['id'])
                   self.graph.nodes[n['id']].location = n['pos']
               for e in edges:
                   self.graph.add_edge(e['src'], e['dest'], e['weight'])
        except IOError as e:
            print(e)

    def save_to_json(self, file_name: str) -> bool:
        my_json={'Edges':[],'Nodes':[]}
        for key in self.graph.edges_out:
            for dest in self.graph.edges_out[key]:
                newdict={}
                newdict['src'] = key
                newdict['dest']= dest
                newdict['weight']= self.graph.edges_out[key][dest]
                my_json['Edges'].append(newdict)
        for id in self.graph.nodes:
            newdict ={}
            if self.graph.nodes[id].location !=None:
                newdict['pos']=','.join(str(x) for x in id)
            else:
                newdict['pos']=None
            newdict['id']=self.graph.nodes[id].key
            my_json['Nodes'].append(newdict)
        try:
            with open (file_name,'w') as file:
                json.dump(my_json, default=lambda n: n.__dict__, indent= 4 ,fp= file)
        except IOError as e:
            print(e)

    # ','.join(str(x) for x in id)
    def shortest_path(self, id1: int, id2: int) -> (float, list):

        if id1 in self.graph.nodes and id2 in self.graph.nodes:
            if id1 ==id2:
                return (0,[id1])
            self.DJ(id1)
            return self.the_shortest_path(id2)

    def connected_component(self, id1: int) -> list:
        if id1 not in self.graph.nodes:
            return None
        c1= self.DJ(id1)
        g= self.reverse_graph()
        Rgraph = GraphAlgo(g)
        c2=Rgraph.DJ(id1)
        connect =[]
        for n in c1:
            if n in c2:
                connect.append(n)
        return connect

    def connected_components(self) -> List[list]:
        connected=[]
        for n in self.graph.nodes:
            flag = False
            c=self.connected_component(n)
            c.sort()
            for n in connected:
                n.sort()
                if n==c:
                    flag=True
            if flag != True:
                connected.append(c)

        return connected


    def plot_graph(self) -> None:
        """
        Plots the graph.
        If the nodes have a position, the nodes will be placed there.
        Otherwise, they will be placed in a random but elegant manner.
        @return: None
        """
        raise NotImplementedError

    def DJ (self, src:int ):
        connected =[]
        connected.append(src)
        for i in self.graph.nodes:
            self.graph.nodes[i].weight = sys.float_info.max
            self.graph.nodes[i].info = "unvisited"
            self.graph.nodes[i].perent= None
        pryorty_q = queue.PriorityQueue()
        self.graph.nodes[src].weight = 0
        pryorty_q.put((self.graph.nodes[src].weight, src))
        while pryorty_q.empty() !=True:
            current = pryorty_q.get()[1]
            self.graph.nodes[current].info = "visited"
            if len (self.graph.all_out_edges_of_node(current)) > 0:
                for n in self.graph.all_out_edges_of_node(current).keys():
                    if n not in connected:
                        connected.append(n)
                    if self.graph.nodes[n].info != "visited":
                        d= self.graph.edges_in[n][current]+ self.graph.nodes[current].weight
                        if d < self.graph.nodes[n].weight:
                            self.graph.nodes[n].weight = d
                            pryorty_q._put((d,n))
                            self.graph.nodes[n].perent = current
        return connected

    def the_shortest_path (self, dest:int):
        short_list=[]
        short_list.append(dest)
        current =self.graph.nodes[dest]
        while current.perent !=None:
            short_list.append(current.perent)
            current=self.graph.nodes[current.perent]

        return (self.graph.nodes[dest].weight , short_list)


    def reverse_graph (self):
        new_edges_out =self.graph.edges_in
        new_edges_in =self.graph.edges_out
        g= DiGraph()
        g.nodes = self.graph.nodes
        g.edges_out=new_edges_out
        g.edges_in=new_edges_in
        g.edges_size= self.graph.edges_size
        return g

    def __str__(self):
        return  "nodes are %s, edges are %s" % (self.graph.nodes,self.graph.edges_out)
