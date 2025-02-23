def ensure_bucket_size(blocks, Z):
    """Ensures that a bucket has exactly Z blocks by adding dummy blocks."""
    while len(blocks) < Z:
        blocks.append(('DUMMY', None, None))
    return blocks[:Z]  # Trim if overfilled
