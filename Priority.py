import matplotlib.pyplot as plt
import numpy as np

np.random.seed(2)

# Task class represents a computational task
class Task:
    def __init__(self, priority, time, start_time):
        self.priority = priority
        self.time = time
        self.done = False
        self.start_time = start_time
        self.cpu_cost = np.random.randint(0, 10)
        self.rom_cost = np.random.randint(0, 10)

    def __repr__(self):
        return f"Task({self.priority}, {self.time}, {self.done})"

# Node class represents a computing node (FOG, USER, CLOUD)
class Node:
    def __init__(self, pos, node_type):
        self.pos = pos
        self.neighbors = []  # Neighboring nodes
        self.type = node_type
        self.tasks = []  # Tasks assigned to the node

    def add_neighbor(self, node):
        if node not in self.neighbors:
            self.neighbors.append(node)

    def draw(self):
        # Plotting nodes based on type and tasks assigned
        marker_color = 'r' if self.type == "FOG" else 'b' if self.type == "CLOUD" else 'g'
        marker_face_color = 'none' if (self.type == "FOG" or self.type == "USER") and len(self.tasks) == 0 else marker_color
        plt.plot(self.pos[0], self.pos[1], f'{marker_color}o', markerfacecolor=marker_face_color,
                 markeredgecolor=marker_color, markersize=10)

        # Drawing edges between neighboring nodes
        for neighbor in self.neighbors:
            plt.plot([self.pos[0], neighbor.pos[0]], [self.pos[1], neighbor.pos[1]], 'black')

# Graph class represents the entire computing graph
class Graph:
    def __init__(self):
        self.nodes = []  # List of nodes in the graph
        self.completed = []  # Completed tasks
        self.cloud_used = 0  # Total cloud processing time
        self.fog_used = 0  # Total fog processing time

    def add_node(self, node):
        self.nodes.append(node)

    def connect(self):
        for i, node_i in enumerate(self.nodes):
            if node_i.type == "FOG":
                self.connect_fog(node_i)
            elif node_i.type == "USER":
                self.connect_user(node_i)

    def connect_fog(self, fog_node):
        # Connects a fog node to the last node in the graph (assumed to be CLOUD)
        fog_node.add_neighbor(self.nodes[-1])
        self.nodes[-1].add_neighbor(fog_node)

    def connect_user(self, user_node):
        # Connects a user node to the nearest fog node
        min_dist = float('inf')
        min_fog_node = None
        for fog_node in filter(lambda x: x.type == "FOG", self.nodes):
            distance = np.linalg.norm(np.array(user_node.pos) - np.array(fog_node.pos))
            if distance < min_dist:
                min_dist = distance
                min_fog_node = fog_node
        user_node.add_neighbor(min_fog_node)

    def draw(self):
        plt.clf()
        for node in self.nodes:
            node.draw()
        plt.pause(1)

    def generate_task(self, time):
        # Generates tasks for USER nodes with a 20% probability
        for user_node in filter(lambda x: x.type == "USER", self.nodes):
            if np.random.rand() < 0.2:
                user_node.tasks.append(Task(np.random.randint(1, 10), np.random.randint(1, 10), time))

    def transfer_task(self):
        # Transfers tasks from USER nodes to their neighboring FOG nodes
        for user_node in filter(lambda x: x.type == "USER" and len(x.tasks) > 0, self.nodes):
            task = user_node.tasks.pop(0)
            user_node.neighbors[0].tasks.append(task)

    def process_node_tasks(self, node, time):
        # Processes tasks for a given node
        if len(node.tasks) > 0:
            for task in node.tasks:
                if task.priority < 5:
                    task.start_time -= 3
                    self.nodes[-1].tasks.append(task)
                    node.tasks.remove(task)

            node.tasks.sort(key=lambda x: x.priority, reverse=True)
            if len(node.tasks) > 0:
                node.tasks[0].time -= 3
                self.fog_used += 2
                if node.tasks[0].time <= 0:
                    node.tasks[0].done = True
                    node.tasks[0].end_time = time
                    self.completed.append(node.tasks[0])
                    node.tasks.remove(node.tasks[0])

            for i in range(1, len(node.tasks)):
                self.nodes[-1].tasks.append(node.tasks.pop(-1))

    def fog(self, time):
        # Processes tasks for FOG nodes
        for fog_node in filter(lambda x: x.type == "FOG" and len(x.tasks) > 0, self.nodes):
            self.process_node_tasks(fog_node, time)

    def cloud(self, time):
        # Processes tasks for CLOUD node
        for cloud_node in filter(lambda x: x.type == "CLOUD" and len(x.tasks) > 0, self.nodes):
            cloud_node.tasks.sort(key=lambda x: x.priority, reverse=True)
            i = 0
            for task in cloud_node.tasks:
                self.cloud_used += task.time
                task.done = True
                task.end_time = time + i
                self.completed.append(task)
                task.start_time -= 3
                cloud_node.tasks.remove(task)
                i += task.time // 4


FOG = 5
USERS = 50

def main():
    graph = Graph()
    for _ in range(FOG):
        graph.add_node(Node([np.random.randint(low=-100, high=100), np.random.randint(low=-100, high=100)], "FOG"))

    for _ in range(USERS):
        graph.add_node(Node([np.random.randint(low=-300, high=300), np.random.randint(low=-300, high=300)], "USER"))

    graph.add_node(Node([0, 0], "CLOUD"))

    graph.connect()
    for i in range(10000):
        graph.generate_task(i)
        graph.draw()
        graph.transfer_task()
        graph.fog(i)
        graph.cloud(i)

    data = []
    for task in graph.completed:
        if task.start_time < 0:
            task.end_time -= task.start_time
            task.start_time = 0
        data.append({
            "priority": task.priority,
            "total_time": task.end_time - task.start_time
        })

    import json
    with open('data_p3.json', 'w') as outfile:
        json.dump({"data": data, "fog_used": graph.fog_used, "cloud_used": graph.cloud_used}, outfile)

if __name__ == "__main__":
    main()