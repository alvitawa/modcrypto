#!/opt/python/latest/bin/python3

import random
import string
import numpy as np
from scipy.special import loggamma

letterFrequency = {
    "E": 12.0,
    "T": 9.10,
    "A": 8.12,
    "O": 7.68,
    "I": 7.31,
    "N": 6.95,
    "S": 6.28,
    "R": 6.02,
    "H": 5.92,
    "D": 4.32,
    "L": 3.98,
    "U": 2.88,
    "C": 2.71,
    "M": 2.61,
    "F": 2.30,
    "Y": 2.11,
    "W": 2.09,
    "G": 2.03,
    "P": 1.82,
    "B": 1.49,
    "V": 1.11,
    "K": 0.69,
    "X": 0.17,
    "Q": 0.11,
    "J": 0.10,
    "Z": 0.07,
}

f_freq = np.zeros(0x100)
for k, f in letterFrequency.items():
    f_freq[ord(k.lower())] = f
f_freq /= np.sum(f_freq)

p = lambda i: "{0:b}".format(i)

C1 = "F96DE8C227A259C87EE1DA2AED57C93FE5DA36ED4EC87EF2C63AAE5B9A7EFFD673BE4ACF7BE8923CAB1ECE7AF2DA3DA44FCF7AE29235A24C963FF0DF3CA3599A70E5DA36BF1ECE77F8DC34BE129A6CF4D126BF5B9A7CFEDF3EB850D37CF0C63AA2509A76FF9227A55B9A6FE3D720A850D97AB1DD35ED5FCE6BF0D138A84CC931B1F121B44ECE70F6C032BD56C33FF9D320ED5CDF7AFF9226BE5BDE3FF7DD21ED56CF71F5C036A94D963FF8D473A351CE3FE5DA3CB84DDB71F5C17FED51DC3FE8D732BF4D963FF3C727ED4AC87EF5DB27A451D47EFD9230BF47CA6BFEC12ABE4ADF72E29224A84CDF3FF5D720A459D47AF59232A35A9A7AE7D33FB85FCE7AF5923AA31EDB3FF7D33ABF52C33FF0D673A551D93FFCD33DA35BC831B1F43CBF1EDF67F0DF23A15B963FE5DA36ED68D378F4DC36BF5B9A7AFFD121B44ECE76FEDC73BE5DD27AFCD773BA5FC93FE5DA3CB859D26BB1C63CED5CDF3FE2D730B84CDF3FF7DD21ED5ADF7CF0D636BE1EDB79E5D721ED57CE3FE6D320ED57D469F4DC27A85A963FF3C727ED49DF3FFFDD24ED55D470E69E73AC50DE3FE5DA3ABE1EDF67F4C030A44DDF3FF5D73EA250C96BE3D327A84D963FE5DA32B91ED36BB1D132A31ED87AB1D021A255DF71B1C436BF479A7AF0C13AA14794"
C2 = "4576C64965DEAF6D87706D830B5EE48239CF7070830045EB9C2C9C656CD60A5FF89C28CF6576C21D0BEC822180666D83005FAD9A22CF7870D70C59EE8B3D9B317FCF0444FE9A6D8A677BD1105FE58723883F3EF4005FE5CE3987786D830A4AFD8F2F867D77D71007AD9A258A3168C21A5FAD832C857E6CCA1D52AD812BCF796BCE0845AD8D22827C6BCD0048EC9A24807F6D830859E8CE2C9A6571CE085FE48D2C837D67830045EA8B3E9B747A831E42F986229A653ED70859EA8B39867F798D4962EBCE04CF667FCD1D4EE9CE3980316DC60C0BF481389D317BCE0842E19D6D80633EDA065EFFCE3A86777B841A0BFD8622817432830847E1CE04CF797FD50C0BF9816D8B7E3ECA1A0BF89D28CF7870D70C59EE8B3D9B623083200BEE8F23CF767BD74952E29B3FCF7473C20047FEC26D9F706DD01E44FF8A3EC3316ECB0645E8CE3F8A7271D10D58A1CE2E9D747ACA1D0BEE8F3F8B623083200BE98123C8653ED40845F9CE39803172CA1F4EAD8723CF703ED00648E48B3996316ACB085FAD8A228A623ED7014EFE8B6D9C7E6CD74944EBCE39877870C41A05A3C06DA6317ACC4945E29A6D987070D7495FE2CE2186677B830045AD8F6D987E6CCF0D0BFA86289D743EC61F4EFF9739877870C44962AD8A22CF7070C74958EC976D86623ED10C48E29C298A7530833D43EC9A6D86623ECD065FAD9D2282746ACB0045EACE04CF7073831E42E1822481763ED7060BFE9B3D9F7E6CD74944FFCE2186677B831C45E98B3FC1"

RANDOM = "".join([random.choice(string.hexdigits) for _ in range(400)]).upper()


def lp(bag):
    """
    This probability is based on the dirichlet distribution.
    """
    log_probability = loggamma(bag + 1).sum(axis=1)
    log_probability += loggamma(bag.shape[0])

    log_probability -= loggamma(bag.sum(axis=1) + bag.shape[0])

    return log_probability


def as_array(c):
    pairs = np.array([int(hexc, base=0x10) for hexc in c], dtype=np.uint8).reshape(
        (-1, 2)
    )
    pairs[:, 0] *= 0x10
    return np.sum(pairs, axis=1)


def cfreqs(a, l):
    # Make array divisible
    padded = np.repeat(0x100, (len(a) // l) * l + l)
    padded[: len(a)] = a

    # everything in chunks[0] is encrypted with the first byte of the key
    # everything in chunks[1] with the second... etc
    chunks = padded.reshape((l, -1), order="F")

    freqs = np.apply_along_axis(
        lambda same_keyed: np.bincount(same_keyed, minlength=0x101), axis=1, arr=chunks
    )
    return freqs[:, :0x100] # Ignore the last bin, which holds the padded values


def decrypt(c):
    a = as_array(c)
    length_scores = np.zeros(len(a))
    length_scores[0] = -np.inf
    for l in range(1, int(len(a) / 1)):
        freqs = cfreqs(a, l)

        # Here I calculate a score for this key length with a different
        # method as the one in the video.
        # The score is the log-probability of each chunk being independently
        # distributed (each chunk being presumably encrypted with a different
        # character, and thus having differently distributed values).
        # Basically, if a smaller amount of different values appear more often
        # across all the chunks, the score is higher (akin to the inverse of entropy).
        score = np.sum(lp(freqs))
        
        length_scores[l] = score
    l = np.argmax(length_scores)
    freqs = cfreqs(a, l)

    score_table = np.zeros((0x100, l))
    # go through each possible key character
    # and evaluate how likely it is to be
    # the actual key character for each character in the key
    for i in range(0x100):
        xored = np.arange(0x100, dtype=np.uint8) ^ i
        scores = np.sum(freqs[:, xored] * f_freq, axis=1)
        score_table[i] = scores

    # now get the most likely key character for each character in the key
    key = np.argmax(score_table.T, axis=1).astype(np.uint8)

    m = a ^ np.resize(key, len(a))

    skey = hex(sum([ai*256**i for i,ai in enumerate(reversed(key))]))
    sm = "".join([chr(i) for i in m]).replace("\x00", " ")
    return (skey, sm)


if __name__ == "__main__":
    key, m = decrypt(C1)
    print(f"\nFirst message (key={key}):\n")
    print(m)
    key, m = decrypt(C2)
    print(f"\nSecond message (key={key}):\n")
    print(m)
    key, m = decrypt(RANDOM)
    print(f"\nRandom ciphertext (key={key}):\n")
    print(m)