import math

def float_time(val):
    h1 = 0
    m1 = 0
    for va in val:
        if va > 0.0:
            a = math.modf(va)
            h = "%d" % (a[1])
            m = "%.2f" % (a[0])
            a = m.split('.')
            h1 += int(h)
            m1 += int(a[1])
            if m1 > 59:
                h1 += 1
                m1 = m1 - 60
    valu = str(h1)+'.'+str(m1)
    va = float(valu)
    value =  "%.2f" % (va)
    return value
