#!/opt/python/latest/bin/python3

import numpy as np
import itertools as it
from scipy.sparse import csr_matrix
from scipy.special import loggamma


asciicommon = "aeorisn1tl2md0cp3hbuk45g9687yfwjvzxqASERBTMLNPOIDCHGKFJUW.!Y*@V-ZQX_$#,/+?;^ %~=&`\)][:<(æ>\"ü|{'öä}"
asciicommon2 = "aeorisn1tl2md0cp3hbuk45g9687yfwjvzxqASERBTMLNPOIDCHGKFJUW.!Y*@V-ZQX_$#,/+?;"



cs = [
    "BB3A65F6F0034FA957F6A767699CE7FABA855AFB4F2B520AEAD612944A801E",
    "BA7F24F2A35357A05CB8A16762C5A6AAAC924AE6447F0608A3D11388569A1E",
    "A67261BBB30651BA5CF6BA297ED0E7B4E9894AA95E300247F0C0028F409A1E",
    "A57261F5F0004BA74CF4AA2979D9A6B7AC854DA95E305203EC8515954C9D0F",
    "BB3A70F3B91D48E84DF0AB702ECFEEB5BC8C5DA94C301E0BECD241954C831E",
    "A6726DE8F01A50E849EDBC6C7C9CF2B2A88E19FD423E0647ECCB04DD4C9D1E",
    "BC7570BBBF1D46E85AF9AA6C7A9CEFA9E9825CFD5E3A0047F7CD009305A71E",
]

def as_array(c):
    pairs = np.array([int(hexc, base=0x10) for hexc in c], dtype=np.uint8).reshape(
        (-1, 2)
    )
    pairs[:, 0] *= 0x10
    return np.sum(pairs, axis=1)

def str_as_array(st):
    return np.array([ord(x) for x in st])

asciic = str_as_array(asciicommon)
asciic2 = str_as_array(asciicommon2)

def xorall(arr):
    repd = np.tile(arr, (arr.shape[0],1))
    return repd ^ repd.T

as_ = np.array([as_array(c) for c in cs])

# note: it appears all values in each row/column are unique
iix = xorall(asciic2)

# maski = np.mask_indices(asciic.shape[0], np.triu, k=1)

info = []
for b in as_.T:
    bbx = xorall(b)

    conjunction = []
    # scores = np.zeros((b.shape[0], asciic.shape[0]))
    for cc in range(bbx.shape[0]):
        disjunction = []
        for mc in range(iix.shape[0]):
            # import pdb; pdb.set_trace()
            # matches = [c in iix[mc] for c in bbx[cc]]
            
            info_matrix = iix[np.repeat(mc, bbx.shape[0])] == bbx[cc].reshape((-1, 1))
            disjunction.append(info_matrix)
    
        conjunction.append(np.array(disjunction))
    conjunction = np.array(conjunction)
    info.append(conjunction)
        
info = np.array(info)

def get_wheels(char_index):
    conjunction = info[char_index]
    for firstc in range(iix.shape[0]):
        
        # alla = conjunction[range(as_.shape[0]), [comb]]
        info_matrix = conjunction[0, firstc] # set the first character, all the others follow
        if not np.all(np.any(info_matrix, axis=1)):
            # The character being tested on the first message cannot be firstc
            continue
        characters = np.argmax(info_matrix, axis=1)

        # Only one character from a message determines all the others in the same position from different messages
        assert np.all([np.argmax(conjunction[i, characters[i]], axis=1) for i in range(characters.shape[0])])

        yield characters

w0 = list(get_wheels(0))

# attempt = np.zeros(as_.shape)-1

# def set_part(start, string, cipher):
#     arr = as_array(string)

#     for conjunction in info[start:start+len(arr)]:

#         alla = conjunction[range(as_.shape[0]), c]


import pdb; pdb.set_trace()

# http://www.fergemann.com/cryptology/otpcrack.html

