from oracle import *
from copy import copy
import sys
import numpy as np

if len(sys.argv) < 2:
    print "Usage: python sample.py <filename>"
    sys.exit(-1)

f = open(sys.argv[1])
data = f.read()
f.close()

ctext = [(int(data[i:i+2],16)) for i in range(0, len(data), 2)]

IV = ctext[:0x10]
c = [ctext[x:0x10+x] for x in range(0x10,len(ctext), 0x10)]

m = [[-1] * 0x10 for _ in range(2)]

# Nothing to do with the padding, just the one-time pad
pads = [[-1] * 0x10 for _ in range(2)]

IV = np.array(IV)
c = np.array(c)
m = np.array(m)
pads = np.array(pads)

Oracle_Connect()

padding = 0
for i in range(0x10):
    tatt = copy(ctext)
    tatt[0x10+i] += 1
    tatt[0x10+i] %= 0x100
    rc = Oracle_Send(tatt, 3)
    if not rc:
        padding = 0x10-i
        break
print "Padding: %d" % padding

m[-1, -padding:] = [padding]*padding
pads[-1, -padding:] = m[-1, -padding:] ^ c[-1, -padding:]

def testc(catt):
    tatt = catt.flatten()
    return Oracle_Send(list(IV) + list(tatt), 3)

datt = np.copy(m[1])
for i in range(padding, 0x10):
    datt[-i-1] = padding
    datt[-i-1:] += 1
    
    catt = np.copy(c)
    catt[0, -i:] ^= datt[-i:]

    # Try out different pads for the newly padded byte
    for p in range(0x100):
        catt[-1, -i-1] = matt[-1, -i-1] ^ p
        rc = testc(catt)
        if rc:
            print(i, p)
    # Store the correct pad
    pads[-1, -i-1] = p

    import pdb; pdb.set_trace()

m[-1] = c[-1] ^ pads[-1]

def decode(a):
    return ''.join(chr(x) for x in a)

print "Last block decrypted: %s" % decode(m[-1, :-padding]) 

rc = Oracle_Send(ctext, 3)
print "Oracle returned: %d" % rc

Oracle_Disconnect() 
