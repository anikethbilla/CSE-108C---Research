import sys
import math
import numpy as np
import random

#class PathORAM:
inFile = sys.argv[1]    # input file 'in.txt'
outFile = sys.argv[2]   # output file 'out.txt'

read_op = list()        # read or write
read_block = list()     # number

r_buffer = list() # buffer stores output data
w_buffer = list()

# read input file and store data on the lists
with open(inFile,'r') as f:
    N = int(f.readline().strip()) # total number of blocks
    for line in f.readlines():
        read_op.append(line.strip().split()[0])
        read_block.append(line.strip().split()[1])

length = int(math.ceil(math.log(N, 2)) - 1) # length of tree path
numLeafs = int(math.pow(2, length) - 1)
treeSize = int(math.pow(2, length + 1) - 1)
tree = [0] * treeSize
for i in range(1, N + 1):
    tree[i] = i
random.shuffle(tree)

def read_leaf(branch):
    return int(int(math.pow(2, length)) + int(branch) - 1);

def get_parent(node):
    return int(math.floor((node - 1) / 2.0))

def get_path(branch):
    path = list()
    for i in range(0, length + 1):
        path.append(branch)
        branch = get_parent(branch)
    return list(reversed(path))

# Random path from leaf to root
def random_path(node):
    rand = random.randint(0, 1)
    child1 = 2 * node + 1
    child2 = 2 * node + 2
    if (child2 > (treeSize - 1)):
        return int (node - numLeafs)

    else:
        if(rand == 0):
            return random_path(child1)
        else:
            return random_path(child2)

def read_bucket(block):
    r_buffer.append(['R', block])
    return data[block]

def write_bucket(block, new_data):
    w_buffer.append(['W', block])
    data[block] = new_data

# Initialize the position map
position_map = dict((x, random.randint(0, numLeafs - 1))
            for x in range(1, N + 1))

# Initialize the tree
for i in range(treeSize):
    block = tree[i]
    if(block != 0):
        position_map[block] = random_path(i)

# Initialize the stash
stash = list()
stash_data = dict()
data = dict()
for i in tree:              # block 0 has dummy data
    data[i] = random.randint(1000, 10000)

def access(op, block, new_data):
    """Perform a read or write operation on block 'a'."""
    x = position_map.get(block) # position of block 'a' in the tree
    position_map[block] = np.random.randint(0, numLeafs - 1)

    leafNode = read_leaf(x)
    path = get_path(leafNode) # path from leaf to root
    for node in path:
        blocks = tree[node]
        stash.append(blocks)
        stash_data[blocks] = read_bucket(blocks)

    # Perform the operation on the block
    if(op == 'W'):
        stash_data[block] = new_data

    # Write the stash back to the tree
    for node in reversed(path):
        n = tree[node]
        write_bucket(n, stash_data.get(n))
        for i in stash:
            if (i == 0):
                stash.remove(i)
                stash_data.pop(i, None)
            else:
                current_branch = position_map.get(i)
                a = get_path(current_branch)
                if(node in a):
                    tree[node] = i
                    stash.remove(i)
                    stash_data.pop(i, None)

def write_file(o):
    buffer = r_buffer + list(reversed(w_buffer))
    for i in buffer:
        o.write(str(i[0]) + ' ' + str(i[1]) + '\n')

o = open(outFile, "w")
unit_test = {}
for i in range (len(read_op)):
    if(read_op[i] == 'R'):
        access(read_op[i], int(read_block[i]), None)
        write_file(o)

    else:
        access(read_op[i], int(read_block[i]), random.randint(1000, 5000))
        write_file(o)
    unit_test[read_block[i]] = r_buffer
    buffer = []
    r_buffer = []
    w_buffer = []
o.close()

print(unit_test)
