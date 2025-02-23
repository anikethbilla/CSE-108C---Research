from PathORAM import PathORAM

class RecursiveORAM:
    def __init__(self, N, Z):
        self.oram_layers = []
        while N > 1:
            self.oram_layers.append(PathORAM(N, Z))
            N = (N + Z - 1) // Z  # Reduce N for next layer

    def access(self, op, a, data=None):
        """Perform access across recursive ORAM layers."""
        for layer in self.oram_layers:
            a = layer.access('read', a)
        
        if op == 'write':
            self.oram_layers[-1].access('write', a, data)
        
        return a
