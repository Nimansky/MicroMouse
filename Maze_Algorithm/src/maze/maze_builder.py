from typing_extensions import Self
import networkx as nx #type: ignore
import numpy as np
from constants import MAZE_PATH


class MazeBuilder:
    """Builds a maze from a grid of nodes and edges"""
    def __init__(self, x: int, y: int):
        """Constructor for MazeBuilder

        Parameters
        ----------
        x : int
            number of nodes in the x direction
        y : int
            number of nodes in the y direction
        """
        self.x = x
        self.y = y
        self.nodes = [[(i,j) for i in range(x)] for j in range(y)]
        self.edges: list[tuple[tuple[int,int], tuple[int,int]]] = []

    def edge(self, p1: tuple[int,int], p2: tuple[int,int]) -> Self:
        """Add an edge between two points by coordinate

        Parameters
        ----------
        p1 : tuple[int,int]
            The first point
        p2 : tuple[int,int]
            The second point

        Returns
        -------
        Self
            Returns self for chaining

        Raises
        ------
        ValueError
            If the points are not adjacent
        """
        x1, y1 = p1
        x2, y2 = p2
        if not ((x1 + 1 == x2 or x1 - 1 == x2) and y1 == y2) and not ((y1 + 1 == y2 or y1 - 1 == y2) and x1 == x2):
            raise ValueError("Points are not adjacent")
        self.edges.append((self.nodes[y1][x1], self.nodes[y2][x2]))
        return self

    def edgei(self, i1:int , i2:int) -> Self:
        """Add an edge between two points by index

        Parameters
        ----------
        i1 : int
            The index of the first point
        i2 : int
            The index of the second point

        Returns
        -------
        Self
            Returns self for chaining

        Raises
        ------
        ValueError
            If the points are not adjacent
        """
        if not (i1 + 1 == i2 or i1 - 1 == i2) and not (i1 + self.x == i2 or i1 - self.x == i2):
            raise ValueError("Points are not adjacent")
        self.edges.append((self.nodes[i1 // self.x][i1 % self.x], self.nodes[i2 // self.x][i2 % self.x]))
        return self

    def remove_edge(self, p1: tuple[int,int], p2: tuple[int,int]) -> Self:
        """Remove an edge between two points by coordinate

        Parameters
        ----------
        p1 : tuple[int,int]
            The first point
        p2 : tuple[int,int]
            The second point

        Returns
        -------
        Self
            Returns self for chaining

        Raises
        ------
        ValueError
            If the points are not adjacent
        """
        x1, y1 = p1
        x2, y2 = p2
        if not ((x1 + 1 == x2 or x1 - 1 == x2) and y1 == y2) and not ((y1 + 1 == y2 or y1 - 1 == y2) and x1 == x2):
            raise ValueError("Points are not adjacent")
        self.edges.remove((self.nodes[y1][x1], self.nodes[y2][x2]))
        return self

    def has_edge(self, p1: tuple[int,int], p2: tuple[int,int]) -> bool:
        """Checks if an edge exists between two points by coordinate

        Parameters
        ----------
        p1 : tuple[int,int]
            The first point
        p2 : tuple[int,int]
            The second point

        Returns
        -------
        bool
            Whether the edge exists

        Raises
        ------
        ValueError
            If the points are not adjacent
        """
        x1, y1 = p1
        x2, y2 = p2
        if not ((x1 + 1 == x2 or x1 - 1 == x2) and y1 == y2) and not ((y1 + 1 == y2 or y1 - 1 == y2) and x1 == x2):
            raise ValueError("Points are not adjacent")
        return (self.nodes[y1][x1], self.nodes[y2][x2]) in self.edges

    def to_graph(self) -> nx.Graph:
        """Converts the maze to a networkx graph

        Returns
        -------
        nx.Graph
            The graph representing the maze
        """
        graph = nx.Graph()
        for row in self.nodes:
            for node in row:
                graph.add_node(node)
        for edge in self.edges:
            graph.add_edge(*edge)
        return graph

    def to_wall_list(self) -> list[list[str]]:
        """Converts the maze to a list of walls

        Returns
        -------
        list[list[str]]
            The list of walls
        """
        walls = [["" for _ in range(self.x)] for _ in range(self.y)]
        for edge in self.edges:
            node1, node2 = edge
            x1, y1 = node1
            x2, y2 = node2
            if x1 == x2:
                if y1 < y2:
                    walls[y1][x1] += "D"
                    walls[y2][x2] += "U"
                else:
                    walls[y1][x1] += "U"
                    walls[y2][x2] += "D"
            else:
                if x1 < x2:
                    walls[y1][x1] += "R"
                    walls[y2][x2] += "L"
                else:
                    walls[y1][x1] += "L"
                    walls[y2][x2] += "R"
        return walls

    def save(self, filename: str):
        """Saves the maze to a file"""
        np.save(MAZE_PATH/filename, self.to_wall_list())

    @staticmethod
    def load(filename: str) -> "MazeBuilder":
        """Loads the maze from a file"""
        walls = np.load(MAZE_PATH/filename)
        return MazeBuilder.from_paths_list(walls)


    @staticmethod
    def from_graph(graph: nx.Graph) -> "MazeBuilder":
        """Converts a graph to a maze

        Parameters
        ----------
        graph : nx.Graph
            The graph to convert

        Returns
        -------
        MazeBuilder
            The maze
        """
        mb = MazeBuilder(0,0)
        mb.x = max([node[0] for node in graph.nodes]) + 1
        mb.y = max([node[1] for node in graph.nodes]) + 1
        mb.nodes = [[(i,j) for i in range(mb.x)] for j in range(mb.y)]
        mb.edges = []
        for edge in graph.edges:
            mb.edges.append(edge)
        return mb

    @staticmethod
    def from_paths_list(walls: list[list[str]]) -> "MazeBuilder":
        """Converts a list of walls to a maze

        Parameters
        ----------
        walls : list[list[str]]
            The list of walls

        Returns
        -------
        MazeBuilder
            The maze
        """
        walls = MazeBuilder.maze_preprocess(walls)
        mb = MazeBuilder(0,0)
        mb.x = len(walls[0])
        mb.y = len(walls)
        mb.nodes = [[(i,j) for i in range(mb.x)] for j in range(mb.y)]
        mb.edges = []
        for y, row in enumerate(walls):
            for x, paths in enumerate(row):
                if "L" in paths and x > 0:
                    edge = (mb.nodes[y][x], mb.nodes[y][x-1])
                    if (edge[1],edge[0]) not in mb.edges:
                        mb.edges.append((mb.nodes[y][x], mb.nodes[y][x-1]))
                if "R" in paths and x < len(row) - 1:
                    edge = (mb.nodes[y][x], mb.nodes[y][x+1])
                    if (edge[1],edge[0]) not in mb.edges:
                        mb.edges.append((mb.nodes[y][x], mb.nodes[y][x+1]))
                if "U" in paths and y > 0:
                    edge = (mb.nodes[y][x], mb.nodes[y-1][x])
                    if (edge[1],edge[0]) not in mb.edges:
                        mb.edges.append((mb.nodes[y][x], mb.nodes[y-1][x]))
                if "D" in paths and y < len(walls) - 1:
                    edge = (mb.nodes[y][x], mb.nodes[y+1][x])
                    if (edge[1],edge[0]) not in mb.edges:
                        mb.edges.append((mb.nodes[y][x], mb.nodes[y+1][x]))
        return mb

    @staticmethod
    def maze_preprocess(maze: list[list[str]]) -> list[list[str]]:
        """Checking partially connected quadrants and adding missing paths to connect them
            if a box at position (x,y) has a path to the left, then the box at position (x-1,y) should have a path to the right
            if a box at position (x,y) has a path to the right, then the box at position (x+1,y) should have a path to the left
            if a box at position (x,y) has a path to the top, then the box at position (x,y+1) should have a path to the bottom
            if a box at position (x,y) has a path to the bottom, then the box at position (x,y-1) should have a path to the top
            Those paths are added to the maze
        """
        for y, row in enumerate(maze):
            for x, paths in enumerate(row):
                if "L" in paths and x > 0 and "R" not in maze[y][x-1]:
                    maze[y][x - 1] += "R"
                if "R" in paths and x < len(row) - 1 and "L" not in maze[y][x+1]:
                    maze[y][x + 1] += "L"
                if "U" in paths and y > 0 and "D" not in maze[y-1][x]:
                    maze[y - 1][x] += "D"
                if "D" in paths and y < len(maze) - 1 and "U" not in maze[y+1][x]:
                    maze[y + 1][x] += "U"
        return maze



## Example Usage (needs to be in main)
if __name__ == "__main__":
    size = input("How big is the maze?")
    mb = MazeBuilder(int(size),int(size))
    # mb.edgei(0,1).edge((1,0),(1,1)).edge((2,1),(3,1)).edge((3,1),(4,1)).edge((4,1),(5,1)).edge((5,1),(6,1)).edge((6,1),(7,1)).edge((7,1),(8,1)).edge((8,1),(9,1)).edge((9,1),(10,1))
    # graph = mb.to_graph()
    # print("Nodes")
    # print(graph.nodes)
    # print("Edges")
    # print(graph.edges)
    # print("Neighbors of (1,0)")
    # print(list(graph.neighbors((1,0))))
    # print("Neighbors of (1,1)")
    # print(list(graph.neighbors((1,1))))

    # print("Walls")
    # print(np.array(mb.to_wall_list()))
    mb.save("live_edit.npy")

