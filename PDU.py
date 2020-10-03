
class PDU:
    def __init__(self, addr=0, code=0, data=[]):
        self.addr = addr
        self.code = code
        self.data = data
        self.len = len(data)
        self.sum = 0