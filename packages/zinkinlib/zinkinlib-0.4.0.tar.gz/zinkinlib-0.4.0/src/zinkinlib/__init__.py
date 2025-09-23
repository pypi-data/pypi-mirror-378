def getStdout(amount, modifier):
    val = []
    for i in range(0, amount):
        val.append(modifier(input()))
    if len(val) == 1:
        return val[0]
    else:
        return val

def getLastDigit(value):
    return int(str(abs(value))[-1])

def getFirstDigit(value):
    return int(str(abs(value))[0])

def getSum(*args):
    if len(args):
        return sum(args)

def getNDigit(value, nOfDigit):
    s = str(abs(value))
    return int(s[nOfDigit - 1]) if 0 < nOfDigit <= len(s) else None
def isOdd(value):
    return value %2 == 0
