from codecs import utf_8_decode, utf_8_encode
from ctypes import sizeof
import os.path
from math import atan2, floor
import numpy as np
from scipy.io import wavfile
import array

list_bit =[]
stringToEncode = "h"

def d_2_b(x, size=8):
    """
    Convert decimal to byte list
    :param x:    decimal
    :param size: the size of byte list
    :return: e.g. [0, 0, 1, ...]
    """
    s = np.sign(x)
    v = size * [None]
    for i in range(0, size):
        v[size-i-1] = abs(x) % 2
        x = int(floor(abs(x)/2.0))
    return s * v

def encode(pathToAudio,stringToEncode):
  rate,audioData1 = wavfile.read(pathToAudio)
  
  #stringToEncode = stringToEncode.ljust(100, '~')
  for c in stringToEncode.encode('utf-8'):
   list_bit.append(d_2_b(c))
  print(list_bit)
  textLength = 8 * len(list_bit)
  chunkSize = int(2 * 2 ** np.ceil(np.log2(2 * textLength)))
  print(chunkSize)
  #print(chunkSize)
  numberOfChunks = int(np.ceil(audioData1.shape[0] / chunkSize))
  audioData = audioData1.copy()
  #Breaking the Audio into chunks
  if len(audioData1.shape) == 1:
      audioData.resize(numberOfChunks * chunkSize, refcheck=False)
      audioData = audioData[np.newaxis]
  else:
      audioData.resize((numberOfChunks * chunkSize, audioData.shape[1]), refcheck=False)
      audioData = audioData.T

  chunks = audioData[0].reshape((numberOfChunks, chunkSize))

  #Applying DFT on audio chunks
  chunks = np.fft.fft(chunks)
  magnitudes = np.abs(chunks)
  phases = np.angle(chunks)
  
  phaseDiff = np.diff(phases, axis=0) 
  
  # Convert message to encode into binary
  
  textInBinary = np.ravel(list_bit)
  
  # Convert message in binary to phase differences
  textInPi = textInBinary.copy()
  
  # for i in textInPi:
  #  print(type(i))
  textInPi[textInPi == 0] = -1
  textInPi = textInPi * -np.pi / 2
  
  midChunk = chunkSize // 2

  
  # Phase conversion+
  
  phases[0, midChunk - textLength: midChunk] = textInPi
  phases[0, midChunk + 1: midChunk + 1 + textLength] = -textInPi[::-1]
  
  
  # Compute the phase matrix
  for i in range(1, len(phases)):
      phases[i] = phases[i - 1] + phaseDiff[i - 1]
      
  # Apply Inverse fourier trnasform after applying phase difference 
  chunks = (magnitudes * np.exp(1j * phases))
  chunks = np.fft.ifft(chunks).real
  # Combining all block of audio again
  audioData[0] = chunks.ravel().astype(np.int16)    

  dir = os.path.dirname(pathToAudio)
  wavfile.write(dir + "/out.wav", rate, audioData.T)
  return dir + "/out.wav" 

def decode(audioLocation):
    rate, audioData = wavfile.read(audioLocation)
    audioData = audioData.copy()

    
    textLength = 8*len(list_bit)
    blockLength = 2 * int(2 ** np.ceil(np.log2(2 * textLength)))
    blockMid = blockLength // 2
    if len(audioData.shape) == 1:
        code = audioData[:blockLength]
    else:
        code = audioData[:blockLength, 0]
    codePhases = np.angle(np.fft.fft(code))[blockMid - textLength:blockMid]
    codeInBinary = (codePhases < 0).astype(np.int16)
    print(codeInBinary)
    
    
    codeInIntCode = codeInBinary.reshape((-1, 8)).dot(1 << np.arange(8 - 1, -1, -1))
    print(codeInIntCode)
    
    sec = []
    for i in codeInIntCode:
        sec.append(i)
    print(bytes(sec).decode('utf-8'))
if __name__ == "__main__":
    path_Audio = "C:/CuoiKyGiauTin/output2.wav"
    encode(path_Audio,stringToEncode)
