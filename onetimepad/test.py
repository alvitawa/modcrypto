#!/opt/python/latest/bin/python3

import numpy as np
import re
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

def bfreqs(as_):
    # everything in chunks[0] is encrypted with the first byte of the key
    # everything in chunks[1] with the second... etc
    chunks = as_.T.astype(np.int64)

    freqs = np.apply_along_axis(lambda same_keyed: np.bincount(same_keyed, minlength=0x101), axis=1, arr=chunks)
    return freqs[:, :0x100]  # Ignore the last bin, which holds the padded values

def xorall(arr):
    repd = np.tile(arr, (arr.shape[0],1))
    return repd ^ repd.T

def xorstrings(str1, str2):
    return hex(int(str1, 16) ^ int(str2, 16))

def isreadable(str): # check readability (allow only alphanumeric chars and some punctiation)
	return bool(re.search('^[a-zA-Z0-9\., \'\"\-_\:\(\)]+$', str))

def test(cs):
    crib = "746865"
    xoredText = xorstrings(cs[0], cs[1])
    for i in range(len(xoredText)):
        sub_xoredText = xoredText[i:]
        cribbedText = xorstrings(sub_xoredText, crib)
        if (isreadable(cribbedText)):
            print("at place {}, with crib 'the':{}, text: {}".format(i, crib, cribbedText))



def decrypt(cs):
    as_ = np.array([as_array(c) for c in cs])

    iix = xorall(asciic)

    mask = np.triu(np.ones(iix.shape))

    import pdb; pdb.set_trace()

    # freqs = bfreqs(as_)
    
    # score_table = np.zeros((0x100, as_.shape[1]))
    # # go through each possible key character
    # # and evaluate how likely it is to be
    # # the actual key character for each character in the key
    # for i in range(0x100):
    #     xored = np.arange(0x100, dtype=np.uint8) ^ i
    #     ### TODO: Change score method to probabilistic
    #     scores = np.sum(freqs[:, xored] * f_freq, axis=1)
    #     score_table[i] = scores

    # ### TODO: Try different configurations aided by the score table
    # ### bring the *overall* ascii distribution closer to english
    # keyx = np.argsort(-score_table.T, axis=1).astype(np.uint8).T
    # import pdb; pdb.set_trace()
    # # Pointers to the most likely key, which is the last
    # keyi = np.zeros(keyx.shape[1], dtype=np.uint8)
    # keys = []
    # for _ in range(10000):
    #     keys += [keyx[keyi, range(31)]]
    #     up = score_table[keyi+1, range(31)] - score_table[keyi, range(31)]
    #     keyi[np.argmax(up)] += 1

    #     np.sum(freqs[:, keyi])

    
    # # import pdb; pdb.set_trace()

    # for key in keys:
    #     ms = [a ^ np.resize(key, len(a)) for a in as_]

    #     skey = hex(sum([ai*256**i for i,ai in enumerate(reversed(key))]))
    #     sms = ["".join([chr(i) for i in m]).replace("\x00", " ") for m in ms]
    #     yield (sms)


if __name__ == "__main__":
    o = decrypt(cs)
    print(*o,sep='\n')