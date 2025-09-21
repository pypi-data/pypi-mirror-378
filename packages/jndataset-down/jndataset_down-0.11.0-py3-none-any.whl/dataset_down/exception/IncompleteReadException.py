class IncompleteReadException(Exception):
    def __init__(self, bytes_read, expected_bytes):
        self.bytes_read = bytes_read
        self.expected_bytes = expected_bytes
        super().__init__(f"Incomplete read: {bytes_read} bytes read, {expected_bytes} bytes expected")
    
    def __str__(self):
        return f"IncompleteReadException: {self.bytes_read}/{self.expected_bytes} bytes read"
    
    def __repr__(self):
        return f"IncompleteReadException(bytes_read={self.bytes_read}, expected_bytes={self.expected_bytes})"