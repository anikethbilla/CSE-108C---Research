import random

class PathORAM:
    def __init__(self, N, Z, num_orams):
        """
        Initialize multiple Path ORAMs.
        :param N: Total number of blocks per ORAM.
        :param Z: Bucket capacity (number of blocks per bucket).
        :param num_orams: Number of ORAMs (2^alpha).
        """
        self.N = N
        self.Z = Z
        self.num_orams = num_orams
        self.orams = [self._init_oram() for _ in range(num_orams)]

    def _init_oram(self):
        """Initialize a single ORAM."""
        L = (self.N - 1).bit_length()  # Tree height
        return {
            'tree': {i: [] for i in range(2 ** (L + 1) - 1)},
            'position_map': {},
            'stash': [],
        }

    def access(self, oram_id, op, a, data=None):
        """
        Perform a read or write operation on block 'a' in the specified ORAM.
        :param oram_id: The ID of the ORAM to access.
        :param op: The operation to perform ('read' or 'write').
        :param a: The block ID to access.
        :param data: The data to write (only for 'write' operations).
        :return: The data read (for 'read' operations), or None (for 'write' operations).
        """
        oram = self.orams[oram_id]
        if a not in oram['position_map']:
            oram['position_map'][a] = random.randint(0, 2 ** (self.N - 1).bit_length() - 1)
        
        x = oram['position_map'][a]
        oram['position_map'][a] = random.randint(0, 2 ** (self.N - 1).bit_length() - 1)
        path = self.get_path(x)

        # Read and clear the path
        for node in path:
            oram['stash'].extend(oram['tree'][node])
            oram['tree'][node] = []

        # Handle the operation
        block = next((b for b in oram['stash'] if b[0] == a), None)
        if op == 'write':
            if block:
                oram['stash'].remove(block)
            oram['stash'].append((a, oram['position_map'][a], data))
        elif op == 'read':
            if block:
                return block[2]  # Return data for read operation
            else:
                return None  # Block not found in stash

        # Write back blocks to the tree
        for node in reversed(path):
            bucket_blocks = [b for b in oram['stash'] if self.get_path(b[1])[-1] == node]
            oram['stash'] = [b for b in oram['stash'] if b not in bucket_blocks]
            oram['tree'][node] = bucket_blocks[:self.Z]

        return None  # For write operations

    def get_path(self, leaf):
        """Get the path from the root to the specified leaf."""
        path = []
        node = leaf + (2 ** (self.N - 1).bit_length() - 1)
        while node >= 0:
            path.append(node)
            node = (node - 1) // 2
        return path
