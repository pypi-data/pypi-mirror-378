# Graphs Library: Dijkstra's Shortest Path
This Python library provides an implementation of Dijkstra's shortest path algorithm and other graph-related utilities. The goal of this project is to practice packaging a Python library into a 
standardized format so it can be easily installed and used.

## Repository Structure: 
```text
src/
├── graphs_asaqib1/
│   ├── __init__.py
│   ├── heapq.py
│   └── sp.py
├── test.py
├── README.md
└── pyproject.toml
```

*graphs_asaqib1/sp.py: Contains the implementation of Dijkstra’s shortest path algorithm  
*graphs_asaqib1/heapq.py: Helper function for priority queue operations  
*test.py: Script to test the library  
*pyproject.toml: Packaging configuration  
*README.md: This file which contains basic information about this library  

## Installation: 
You can install the package using pip: 
```text
pip install asaqib1==1.0.0
```

## Features: 
*Finds the shortest paths from a source vertex to all other vertices in a weighted graph  
*Supports extension with other graph algorithms  
*Uses a min-heap to efficiently select the next vertex with the smallest known distance  

## Example: 
For a graph with 9 vertices, the shortest path from vertex 0 to vertex 1 may have a cost of 4, and to vertex 8 may have a cost of 14.

## Author Information
*Author: Alizah Saqib  
*GitHub: https://github.com/asaqib1  
