class QueueManager:
    def __init__(self):
        self.queue = []

    def get_size(self):
        return len(self.queue)

    def get_queue(self):
        return self.queue

    def enqueue(self, player_id):
        self.queue.append(player_id)

    def dequeue(self):
        return self.queue.pop(0)
