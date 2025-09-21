# graphs_carmen

This is a Python package for graph algorithms, including Dijkstra's shortest path. It is structured for easy installation and command-line usage.

## Installation

To install locally:

    pip install .

## Usage

Run the shortest path algorithm from the command line:

    python test.py graph.txt

## Graph File Format

The input file should start with the number of vertices, followed by edges in the format:

    source destination weight

Example:

    9
    0 1 4
    0 7 8
    1 2 8
    1 7 11
    2 3 7
    2 8 2
    3 4 9
    3 5 14
    4 5 10
    5 6 2
    6 7 1
    6 8 6
    7 8 7

## Output

The script prints shortest distances from the source node (0), and the shortest path to each node.

## Repository

GitHub URL: https://github.com/csirhall/dijkstra-sp

## Branches

- `main` branch is protected
- `dev` branch is used for development