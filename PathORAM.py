class PathORAM:
    def __init__(self, N, Z):
        self.N = N
        self.Z = Z
        self.tree = self._init_tree()
        self.position_map = {}  # Consider using a database for large datasets
        self.stash = {}  # Use a dictionary for faster lookups

    def _init_tree(self):
        L = (self.N).bit_length()  # More accurate tree height calculation
        return {i: [] for i in range(2 ** (L + 1) - 1)}

    def access(self, op, a, data=None):
        if a not in self.position_map:
            self.position_map[a] = random.randint(0, 2 ** (self.N).bit_length() - 1)

        x = self.position_map[a]
        self.position_map[a] = random.randint(0, 2 ** (self.N).bit_length() - 1)
        path = self.get_path(x)

        # Read and clear the path
        for node in path:
            self.stash.update({b[0]: b for b in self.tree[node]})
            self.tree[node] = []

        # Handle the operation
        block = self.stash.get(a)
        if op == 'write':
            if block:
                del self.stash[a]
            self.stash[a] = (a, self.position_map[a], data)
        elif op == 'read':
            if block:
                return block[2]
            else:
                return None

        # Write back blocks to the tree
        for node in reversed(path):
            bucket_blocks = [b for b in self.stash.values() if self.get_path(b[1])[-1] == node]
            for b in bucket_blocks:
                del self.stash[b[0]]
            self.tree[node] = bucket_blocks[:self.Z]

        return None
