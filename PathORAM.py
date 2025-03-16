import random

class PathORAM:
    def __init__(self, N, Z):
        """
        Initialize Path ORAM.
        :param N: Total number of blocks.
        :param Z: Bucket capacity (number of blocks per bucket).
        """
        self.N = N  # Total number of blocks
        self.Z = Z  # Bucket capacity
        self.L = (N - 1).bit_length()  # Tree height
        self.tree = self.initialize_tree()  # ORAM tree
        self.position_map = {}  # Position map (initially empty)
        self.stash = []  # Stash for temporarily holding blocks

    def initialize_tree(self):
        """Initialize the ORAM tree with empty buckets."""
        return {i: [] for i in range(2 ** (self.L + 1) - 1)}

    def get_path(self, leaf):
        """
        Get the path from the root to the specified leaf.
        :param leaf: The leaf node index.
        :return: A list of node indices representing the path.
        """
        path = []
        node = leaf + (2 ** self.L - 1)  # Convert leaf index to tree node index
        while node >= 0:
            path.append(node)
            node = (node - 1) // 2  # Move to the parent node
        return path

    def access(self, op, a, data=None):
        """
        Perform a read or write operation on block 'a'.
        :param op: The operation to perform ('read' or 'write').
        :param a: The block ID to access.
        :param data: The data to write (only for 'write' operations).
        :return: The data read (for 'read' operations), or None (for 'write' operations).
        """
        # If the block ID is not in the position map, add it with a random leaf
        if a not in self.position_map:
            self.position_map[a] = random.randint(0, 2 ** self.L - 1)
        
        # Get the current leaf for the block
        x = self.position_map[a]
        # Remap the block to a new random leaf
        self.position_map[a] = random.randint(0, 2 ** self.L - 1)
        # Get the path from the root to the leaf
        path = self.get_path(x)

        # Read all buckets along the path into the stash
        for node in path:
            self.stash.extend(self.tree[node])
            self.tree[node] = []  # Clear the bucket

        # Perform the operation
        block = next((b for b in self.stash if b[0] == a), None)
        if op == 'write':
            if block:
                self.stash.remove(block)  # Remove the old block
            self.stash.append((a, self.position_map[a], data))  # Add the new block
        elif op == 'read':
            if block:
                return block[2]  # Return the data

        # Write blocks back to the tree
        for node in reversed(path):
            # Select blocks that belong to this node
            bucket_blocks = [b for b in self.stash if self.get_path(b[1])[-1] == node]
            # Remove these blocks from the stash
            self.stash = [b for b in self.stash if b not in bucket_blocks]
            # Write the blocks to the bucket
            self.tree[node] = bucket_blocks[:self.Z]  # Ensure bucket capacity is not exceeded

        return None if op == 'write' else block[2]
