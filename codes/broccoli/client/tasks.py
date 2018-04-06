from canvas import Task

@Task
def add(x, y, op=None):
    return op(x, y) if op else x + y

@Task
def xsum(x):
    return sum(x)

@Task
def mul(x, y, op=None):
    return op(x, y) if op else x * y

@Task
def mapper(word):
    return (word, 1) if len(word) > 3 else None
