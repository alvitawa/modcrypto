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

IV = np.array(IV)
c = np.array(c)
m = np.array(m)

Oracle_Connect()

# Find the padding in the last block
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

m[1, -padding:] = [padding]*padding

def testc(catt):
    tatt = catt.flatten()
    return Oracle_Send(list(IV) + list(tatt), 3)

# Decrypt the last block back-to-front
for l in range(padding, 0x10):
    # Projected values
    dil = np.repeat(0, 0x10)
    dil[-l:] = l + 1
    
    # Real, known, values
    dir_ = np.repeat(0, 0x10)
    dir_[-padding:] = padding
    dir_[-l:-padding] = m[1, -l:-padding]

    ir = None
    for i in range(0x100):
        dil[-l-1] = i
        tatt = np.array(ctext)
        tatt[0x10:0x20] ^= dil ^ dir_
        rc = Oracle_Send(list(tatt), 3)
        if rc:
            print 'm1: ', l, i
            ir = i
            break
    
    # import pdb; pdb.set_trace()
    m[1, -l-1] = (l + 1) ^ ir
    
def decode(a):
    return ''.join(chr(x) for x in a)
    
print "Last block decrypted: %s" % decode(m[-1, :-padding]) 

# Do the same again to the first block, by acting as if 
# the last block doesn't exist, and the padding was 0.
for l in range(0, 0x10):
    # Projected values
    dil = np.repeat(0, 0x10)
    dil[-l:] = l + 1
    
    # Real, known, values
    dir_ = np.repeat(0, 0x10)
    if l != 0:
        dir_[-l:] = m[0, -l:]

    ir = None
    for i in range(0x100):
        dil[-l-1] = i
        tatt = np.array(ctext)
        tatt[:0x10] ^= dil ^ dir_
        rc = Oracle_Send(list(tatt[:0x20]), 2)
        if rc:
            print 'm0: ', l, i
            ir = i
            break
    
    # import pdb; pdb.set_trace()
    m[0, -l-1] = (l + 1) ^ ir


print "First block decrypted: %s" % decode(m[0]) 

print "Complete message: \n\n\t%s\n\n" % decode(m.flatten())

Oracle_Disconnect() 
