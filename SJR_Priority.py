import matplotlib.pyplot as plt
import numpy as np

# Function to set the random seed for reproducibility
def seed():
    np.random.seed(0)

# Function to calculate the Euclidean distance between two nodes
def dist(node1, node2):
    return ((node1[0] - node2[0])**2 + (node1[1] - node2[1])**2)**0.5

# Task class represents a computational task
class Task:
    def __init__(self, priority, time, start_time, deadline):
        self.priority = priority
        self.exec_time = time
        self.done = False
        self.start_time = start_time
        self.deadline = deadline
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
        self.neighbors.append(node)

    def draw(self):
        # Plotting nodes based on type and tasks assigned
        if self.type == "FOG":
            if len(self.tasks) > 0:
                plt.plot(self.pos[0], self.pos[1], 'ro', markeredgecolor='r', markersize=10)
            else:
                plt.plot(self.pos[0], self.pos[1], 'ro', markerfacecolor='none', markeredgecolor='r', markersize=10)
        elif self.type == "CLOUD":
            plt.plot(self.pos[0], self.pos[1], 'bo', markerfacecolor='b', markeredgecolor='b', markersize=10)
        else:
            if len(self.tasks) > 0:
                plt.plot(self.pos[0], self.pos[1], 'go', markeredgecolor='g', markersize=10)
            else:
                plt.plot(self.pos[0], self.pos[1], 'go', markerfacecolor='none', markeredgecolor='g', markersize=10)

        # Drawing edges between neighboring nodes
        for n in self.neighbors:
            plt.plot([self.pos[0], n.pos[0]], [self.pos[1], n.pos[1]], 'black')

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
        for i in range(len(self.nodes)):
            if self.nodes[i].type == "FOG":
                self.nodes[i].add_neighbor(self.nodes[-1])
                self.nodes[-1].add_neighbor(self.nodes[i])

            if self.nodes[i].type == "USER":
                min_dist = float('inf')
                min_node = None
                for j in range(len(self.nodes)):
                    if self.nodes[j].type == "FOG":
                        distance = dist(self.nodes[i].pos, self.nodes[j].pos)
                        if distance < min_dist:
                            min_dist = distance
                            min_node = self.nodes[j]
                self.nodes[i].add_neighbor(min_node)

    def draw(self):
        plt.clf()
        for node in self.nodes:
            node.draw()
        plt.pause(1)

    def generate_task(self, time):
        for node in self.nodes:
            if node.type == "USER":
                # 20% probability of generating a task
                if np.random.rand() < 0.2:
                    node.tasks.append(Task(np.random.randint(1, 10), np.random.randint(1, 10), time, np.random.randint(5, 20)))

    def transfer_task(self):
        for node in self.nodes:
            if node.type == "USER" and len(node.tasks) > 0:
                task = node.tasks.pop(0)
                node.neighbors[0].tasks.append(task)

    def fog(self, time):
        for node in self.nodes:
            if node.type == "FOG" and len(node.tasks) > 0:
                for task in node.tasks:
                    if task.priority < 5:
                        task.start_time -= 3
                        self.nodes[-1].tasks.append(task)
                        node.tasks.remove(task)

                node.tasks.sort(key=lambda x: x.priority, reverse=True)
                if len(node.tasks) > 0:
                    node.tasks[0].time -= 3
                    self.fog_used += 1.5
                    if node.tasks[0].time <= 0:
                        node.tasks[0].done = True
                        node.tasks[0].end_time = time
                        self.completed.append(node.tasks[0])
                        node.tasks.remove(node.tasks[0])
                for i in range(1, len(node.tasks)):
                    self.nodes[-1].tasks.append(node.tasks.pop(-1))

    def cloud(self, time):
        for node in self.nodes:
            if node.type == "CLOUD" and len(node.tasks) > 0:
                node.tasks.sort(key=lambda x: x.time)
                i = 0
                for task in node.tasks:
                    self.cloud_used += task.time / 0.95
                    task.done = True
                    task.end_time = time
                    self.completed.append(task)
                    task.start_time -= 3
                    node.tasks.remove(task)
                    i += task.time // 4

# CONSTANTS
FOG = 5
USERS = 50

def main():
    graph = Graph()
    for i in range(FOG):
        graph.add_node(Node([np.random.randint(low=-100, high=100), np.random.randint(low=-100, high=100)], "FOG"))

    for i in range(USERS):
        graph.add_node(Node([np.random.randint(low=-300, high=300), np.random.randint(low=-300, high=300)], "USER"))

    graph.add_node(Node([0, 0], "CLOUD"))

    graph.connect()
    graph.generate_task(0)
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
            "total_time": task.end_time - task.start_time,
            "task_time": task.task_time,
        })

    import json
    with open('data_sjf_priority3.json', 'w') as outfile:
        json.dump({"data": data, "fog_used": graph.fog_used, "cloud_used": graph.cloud_used}, outfile)

if __name__ == "__main__":
    main()
