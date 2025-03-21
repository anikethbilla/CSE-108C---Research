import random

class PathORAM:
    def __init__(self, N, Z):
        """
        Initialize a single Path ORAM.
        :param N: Total number of blocks.
        :param Z: Bucket capacity (number of blocks per bucket).
        """
        self.N = N
        self.Z = Z
        self.tree = self._init_tree()
        self.position_map = {}
        self.stash = []

    def _init_tree(self):
        """Initialize the ORAM tree."""
        L = (self.N - 1).bit_length()  # Tree height
        return {i: [] for i in range(2 ** (L + 1) - 1)}

    def access(self, op, a, data=None):
        """
        Perform a read or write operation on block 'a'.
        :param op: The operation to perform ('read' or 'write').
        :param a: The block ID to access.
        :param data: The data to write (only for 'write' operations).
        :return: The data read (for 'read' operations), or None (for 'write' operations).
        """
        if a not in self.position_map:
            # Assign a random leaf for the block if it doesn't exist
            self.position_map[a] = random.randint(0, 2 ** (self.N - 1).bit_length() - 1)

        x = self.position_map[a]
        # Update the position map to a new random leaf
        self.position_map[a] = random.randint(0, 2 ** (self.N - 1).bit_length() - 1)
        path = self.get_path(x)

        # Read and clear the path
        for node in path:
            self.stash.extend(self.tree[node])
            self.tree[node] = []

        # Handle the operation
        block = next((b for b in self.stash if b[0] == a), None)
        if op == 'write':
            if block:
                self.stash.remove(block)
            self.stash.append((a, self.position_map[a], data))
        elif op == 'read':
            if block:
                return block[2]  # Return data for read operation
            else:
                # If the block is not found, return None
                return None

        # Write back blocks to the tree
        for node in reversed(path):
            bucket_blocks = [b for b in self.stash if self.get_path(b[1])[-1] == node]
            self.stash = [b for b in self.stash if b not in bucket_blocks]
            self.tree[node] = bucket_blocks[:self.Z]

        return None  # For write operations

    def get_path(self, leaf):
        """Get the path from the root to the specified leaf."""
        path = []
        node = leaf + (2 ** (self.N - 1).bit_length() - 1)
        while node >= 0:
            path.append(node)
            node = (node - 1) // 2
        return path
