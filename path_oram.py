import sys
import math
import numpy as np
import random

class PathORAM:
    def __init__(self, in_file, out_file):
        self.in_file = in_file
        self.out_file = out_file
        self.read_op = []
        self.read_block = []
        self.r_buffer = []
        self.w_buffer = []
        self.position_map = {}
        self.stash = []
        self.stash_data = {}
        self.data = {}
        self.tree = []
        self.N = 0
        self.length = 0
        self.numLeafs = 0
        self.treeSize = 0
        self._initialize()

    def _initialize(self):
        """Reads input file and initializes the ORAM tree and position map."""
        with open(self.in_file, 'r') as f:
            first_line = f.readline().strip()
            if not first_line:
                raise ValueError("Input file is empty or missing the first line.")
            self.N = int(first_line)  # Number of blocks
            
            # Read operations
            for line in f.readlines():
                op, block = line.strip().split()
                self.read_op.append(op)
                self.read_block.append(int(block))

        self.length = int(math.ceil(math.log(self.N, 2)) - 1)  # Tree path length
        self.numLeafs = int(math.pow(2, self.length) - 1)
        self.treeSize = int(math.pow(2, self.length + 1) - 1)
        self.tree = [0] * self.treeSize

        for i in range(1, self.N + 1):
            self.tree[i] = i
        random.shuffle(self.tree)

        # Initialize position map
        self.position_map = {x: random.randint(0, self.numLeafs - 1) for x in range(1, self.N + 1)}

        # Assign random paths to the tree blocks
        for i in range(self.treeSize):
            block = self.tree[i]
            if block != 0:
                self.position_map[block] = self.random_path(i)

        # Initialize stash and data
        for i in self.tree:
            self.data[i] = random.randint(1000, 10000)

    def read_leaf(self, branch):
        return int(math.pow(2, self.length) + branch - 1)

    def get_parent(self, node):
        return int((node - 1) / 2)

    def get_path(self, branch):
        """Gets the path from a leaf to the root."""
        path = []
        for _ in range(self.length + 1):
            path.append(branch)
            branch = self.get_parent(branch)
        return list(reversed(path))

    def random_path(self, node):
        """Generates a random path in the ORAM tree."""
        rand = random.randint(0, 1)
        child1 = 2 * node + 1
        child2 = 2 * node + 2
        if child2 > (self.treeSize - 1):
            return int(node - self.numLeafs)
        return self.random_path(child1) if rand == 0 else self.random_path(child2)

    def read_bucket(self, block):
        """Reads a bucket and appends it to the read buffer."""
        self.r_buffer.append(['R', block])
        return self.data[block]

    def write_bucket(self, block, new_data):
        """Writes to a bucket and logs it in the write buffer."""
        self.w_buffer.append(['W', block])
        self.data[block] = new_data

    def access(self, op, block, new_data):
        """Perform a read or write operation on a block."""
        x = self.position_map.get(block)
        self.position_map[block] = np.random.randint(0, self.numLeafs - 1)

        leafNode = self.read_leaf(x)
        path = self.get_path(leafNode)

        # Read path into stash
        for node in path:
            blocks = self.tree[node]
            self.stash.append(blocks)
            self.stash_data[blocks] = self.read_bucket(blocks)

        # Perform operation
        if op == 'W':
            self.stash_data[block] = new_data

        # Write back the stash
        for node in reversed(path):
            n = self.tree[node]
            self.write_bucket(n, self.stash_data.get(n, None))
            for i in self.stash[:]:
                if i == 0:
                    self.stash.remove(i)
                    self.stash_data.pop(i, None)
                else:
                    current_branch = self.position_map.get(i)
                    a = self.get_path(current_branch)
                    if node in a:
                        self.tree[node] = i
                        self.stash.remove(i)
                        self.stash_data.pop(i, None)

    def write_file(self):
        """Writes the read/write operations to the output file."""
        buffer = self.r_buffer + list(reversed(self.w_buffer))
        print("Writing to file:", buffer)  # Debug print
        with open(self.out_file, "a") as o:
            for i in buffer:
                o.write(f"{i[0]} {i[1]}\n")
        self.r_buffer.clear()
        self.w_buffer.clear()

    def run(self):
        """Runs the ORAM simulation based on input operations."""
        unit_test = {}
        with open(self.out_file, "w") as _:  # Clear file before writing
            pass

        for i in range(len(self.read_op)):
            if self.read_op[i] == 'R':
                self.access(self.read_op[i], int(self.read_block[i]), None)
            else:
                self.access(self.read_op[i], int(self.read_block[i]), random.randint(1000, 5000))
            
            self.write_file()
            unit_test[self.read_block[i]] = self.r_buffer
            self.r_buffer = []
            self.w_buffer = []
        
        print(unit_test)  # Debug output

if __name__ == "__main__":
    in_file = sys.argv[1] if len(sys.argv) > 1 else "in.txt"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "out.txt"
    path_oram = PathORAM(in_file, out_file)
    path_oram.run()
    
