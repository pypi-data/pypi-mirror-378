seed = 0
def get_seed():
    global seed
    for i in range(100):
        seed ^= id(object())
        seed = (seed << 13) | (seed >> 17)
    return seed % 2 ** 32
state = get_seed()
def xorshift():
    global state
    state ^= state << 13
    state ^= state >> 17
    state ^= state << 5
    state &= 0xFFFFffff
    return state
def randdev(min:float = 0.0, max:float = 1.0):
    if min == 0.0 and max == 1.0:
        return xorshift() / 2 ** 32
    else:
        return min + (max - min) % (xorshift() / 2 ** 32)
    
def randint(min:int = 0, max:int = 10):
    if min > max:
        min,max = max,min
    range_size = max - min + 1
    return min + xorshift() % range_size
