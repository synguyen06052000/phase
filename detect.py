from codecs import utf_8_decode, utf_8_encode
from ctypes import sizeof
import os.path
from math import atan2, floor
import numpy as np
from scipy.io import wavfile
import array


def decode(audioLocation):
    rate, audioData = wavfile.read(audioLocation)
    audioData = audioData.copy()

    
    textLength = 8
    
    blockLength = 2 * int(2 ** np.ceil(np.log2(2 * textLength)))
    #print(blockLength)
    blockMid = blockLength // 2
    #print(blockMid)
    if len(audioData.shape) == 1:
        code = audioData[:blockLength]
    else:
        code = audioData[:blockLength, 0]
    codePhases = np.angle(np.fft.fft(code))[blockMid - textLength:blockMid]
    #print(codePhases)
    
    codeInBinary = (codePhases < 0).astype(np.int16)
    
    codeInIntCode = codeInBinary.reshape((-1, 8)).dot(1 << np.arange(8 - 1, -1, -1))
    #print(codeInIntCode)
    sec = []
    for i in codeInIntCode:
        sec.append(i)
    for j in sec:
        if(j!=0):
            print("File đã được giấu tin")
        else:
            print("File chưa được giấu tin")
    # if(bytes(sec).decode('utf-8')==""):
    #     print("File đã được giấu")
   
    
if __name__ == "__main__":
    path_Audio_Decode = "C:/CuoiKyGiauTin/output2.wav"
    decode(path_Audio_Decode)