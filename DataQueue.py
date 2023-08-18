class DataQueue:
    def __init__(self):
        self.queue = [] 
        
    
    def enqueue(self, value):
        self.queue.append(value)

    def dequeue(self):
        if self.is_empty():
            return "Error: Queue is empty."
        return self.queue.pop(0)

    def front(self):
        if self.is_empty():
            return "Error: Queue is empty."
        return self.queue[0]
    
    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)
    

