import sys
from queue import PriorityQueue
from PIL import Image, ImageDraw

class Node():
    def __init__(self, state, parent, action, cost, priority):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority

class MazeAStar():
    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()

        if contents.count("A") != 1:
            raise Exception("Maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("Maze must have exactly one goal")

        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None
        self.cost_to_reach = {}  # Costları saklamak için bir sözlük

    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("#", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()

    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def heuristic(self, state):
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])

    def solve(self):
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None, cost=0, priority=0)
        frontier = PriorityQueue()
        frontier.put((0, start))
        self.explored = set()
        self.cost_to_reach[self.start] = 0  # Başlangıç durumu için cost

        while not frontier.empty():
            _, node = frontier.get()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells, self.cost_to_reach[self.goal])
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if state not in self.explored:
                    if state not in self.cost_to_reach or node.cost + 1 < self.cost_to_reach[state]:
                        self.cost_to_reach[state] = node.cost + 1
                        priority = self.cost_to_reach[state] + self.heuristic(state)
                        child = Node(state=state, parent=node, action=action, cost=node.cost + 1, priority=priority)
                        frontier.put((priority, child))

    def output_image(self, filename, show_solution=True, show_explored=False):
        cell_size = 50
        cell_border = 2
        img = Image.new("RGBA", (self.width * cell_size, self.height * cell_size), "black")
        draw = ImageDraw.Draw(img)
        solution = self.solution[1] if self.solution is not None else None

        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    fill = (40, 40, 40)
                    text = None  # text değişkenini tanımla
                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                    text = None  # text değişkenini tanımla
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)
                    text = None  # text değişkenini tanımla
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)
                    cost = self.cost_to_reach.get((i, j), 0)
                    text = str(cost)
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)
                    cost = self.cost_to_reach.get((i, j), 0)
                    text = str(cost)
                else:
                    fill = (237, 240, 252)

                draw.rectangle(
                    [(j * cell_size + cell_border, i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)],
                    fill=fill)

                if text is not None:  # text değişkenini kontrol et ve yalnızca tanımlandığında kullan
                    text_width, text_height = draw.textsize(text)
                    text_x = (j * cell_size + cell_size / 2) - text_width / 2
                    text_y = (i * cell_size + cell_size / 2) - text_height / 2
                    draw.text((text_x, text_y), text, fill="black")


        img.save(filename)

if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = MazeAStar(sys.argv[1])
print("Maze:")
m.print()
print("Solving...")
m.solve()
print("States Explored:", m.num_explored)
print("Solution:")
m.print()
m.output_image("maze.png", show_solution=True, show_explored=True)
