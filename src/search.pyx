import heapq
import math


def a_star_search(start, goal, grid):
    open_list = [(0, start)]
    closed_set = set()
    parent = {}
    g = {start: 0}  # The cost from getting to each node from the start
    moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    D = 1
    D2 = math.sqrt(2)

    while open_list:
        f, current = heapq.heappop(open_list)

        if current == goal:
            path = []
            while current != start:
                path.append(current)
                current = parent[current]
            return path

        closed_set.add(current)
        # expand the nrighbours of the current node
        for dx, dy in moves:
            x, y = current[0] + dx, current[1] + dy  # The current cell
            # if this cell is in the bounds of the grid
            if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == 1:
                neighbor = (x, y)
                # Check if the neighbor has already been evaluated
                if neighbor in closed_set:
                    continue

                tentative_g = g[current] + (dx * dy == 0) and 1 or 1.4
                # A better path has already been computed for this neighbor
                if neighbor not in g or tentative_g < g[neighbor]:
                    # Set the current best path from current to neighbor
                    parent[neighbor] = current
                    g[neighbor] = tentative_g

                    # Use the cross product to add a weight (penalize) to the heuristic
                    # The cross product is largest when two vectors are orthogonal
                    # So the further away the the path vector is with the start -> goal vector
                    # the larger the h value
                    dx1 = neighbor[0] - goal[0]
                    dy1 = neighbor[1] - goal[1]
                    dx2 = start[0] - goal[0]
                    dy2 = start[1] - goal[1]
                    cross = abs(dx1 * dy2 - dx2 * dy1)

                    # calculate the heuristic
                    dx_ = abs(neighbor[0] - goal[0])
                    dy_ = abs(neighbor[1] - goal[1])
                    h = (D * (dx_ + dy_) + (D2 - 2 * D) * min(dx_, dy_)) + cross * 0.1
                    f = g[neighbor] + h

                    heapq.heappush(open_list, (f, neighbor))
    return None
