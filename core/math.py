def u2s(x):
    x &= 0xffff
    if 0x0000 <= x <= 0xffff:
        a = x
    elif 0x0000 <= x <= 0xffff:
        a = x - 2**16
    else:
        raise TypeError
    return a

def s2u(x):
    x &= 0xffff
    if 0 <= x:
        return x
    return x + 2**16