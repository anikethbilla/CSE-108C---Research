import random
from EncryptionUtils import EncryptionUtils
from dummy_blocks import ensure_bucket_size

class PathORAM:
    def __init__(self, N, Z):
        self.N = N  # Total number of blocks
        self.Z = Z  # Bucket capacity
        self.L = (N - 1).bit_length()  # Tree height
        self.tree = self.initialize_tree()
        self.position_map = self.initialize_position_map()
        self.stash = []
        self.encryption = EncryptionUtils()
    
    def initialize_tree(self):
        """Initialize the tree with encrypted dummy blocks."""
        return {i: [self.encryption.encrypt_data(str(('DUMMY', None, None))) for _ in range(self.Z)] 
                for i in range(2 ** (self.L + 1) - 1)}
    
    def initialize_position_map(self):
        """Initialize position map with random leaf node mappings."""
        return {i: random.randint(0, 2 ** self.L - 1) for i in range(self.N)}

    def read_bucket(self, bucket_index):
        """Read and decrypt all blocks from a bucket."""
        return [eval(self.encryption.decrypt_data(block)) for block in self.tree[bucket_index]]
    
    def write_bucket(self, bucket_index, blocks):
        """Write blocks into a bucket after encryption."""
        blocks = ensure_bucket_size(blocks, self.Z)  # Ensure bucket size Z
        self.tree[bucket_index] = [self.encryption.encrypt_data(str(block)) for block in blocks]
    
    def access(self, op, a, data=None): 
        """Perform a read or write operation on block 'a'."""
        x = self.position_map[a]  # Get current position
        self.position_map[a] = random.randint(0, 2 ** self.L - 1)  # Remap block to new random position
        path = self.get_path(x)  # Get path from leaf x to root
        
        # Read path into stash
        for bucket in path:
            self.stash.extend(self.read_bucket(bucket))
        
        # Retrieve block from stash
        block = next((b for b in self.stash if b[0] == a), ('DUMMY', None, None))
        if op == 'write':
            self.stash.remove(block)
            self.stash.append((a, self.position_map[a], data))
        
        # Write path back, filling buckets greedily from leaf to root
        for bucket in reversed(path):
            bucket_blocks = [b for b in self.stash if self.get_path(b[1])[-1] == bucket]
            self.stash = [b for b in self.stash if b not in bucket_blocks]
            self.write_bucket(bucket, bucket_blocks)
        
        return block[2] if op == 'read' else None
    
    def get_path(self, leaf):
        """Return the path from a leaf node to the root."""
        path = []
        node = leaf + (2 ** self.L - 1)
        while node >= 0:
            path.append(node)
            node = (node - 1) // 2
        return path
