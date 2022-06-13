from cmath import phase
from tkinter import filedialog, scrolledtext
from tkinter import *
from tkinter import ttk
import tkinter as tk
from turtle import width
from main import *
from codecs import utf_8_decode, utf_8_encode
from ctypes import sizeof
import os.path
from math import atan2, floor
import numpy as np
from scipy.io import wavfile
import array

list_bit =[]
stringToEncode = "đặng thùy dương"


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
    
    textLength = 8 * len(list_bit)
    chunkSize = int(2 * 2 ** np.ceil(np.log2(2 * textLength)))
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
    wavfile.write(dir + "/output.wav", rate, audioData.T)
    return dir + "/output.wav" 

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
    #print(codeInBinary)
    
    
    codeInIntCode = codeInBinary.reshape((-1, 8)).dot(1 << np.arange(8 - 1, -1, -1))
    sec = []
    for i in codeInIntCode:
        sec.append(i)
    return(bytes(sec).decode('utf-8'))

 
#Vẽ giao diện
class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        self.master.title("Giấu tin trong âm thanh bằng mã hóa pha")
        self.pack(fill=BOTH, expand=1)
        self.drawEncoding()
        self.drawDecoding()
    def drawEncoding(self):
         # encode Label
        self.encodeVar = StringVar()
        self.encodelabel = Label(root, textvariable=self.encodeVar,font=(None,20))
        self.encodelabel.place(x=150, y=10)
        self.encodeVar.set("Mã hóa")

        # Chọn file cần giấu
        self.selectFileButton = Button(self, text="Chọn file chứa", command=self.selectFile)
        self.selectFileButton.place(x=10, y=60)
        self.var = StringVar()
        self.label = Label(root, textvariable=self.var, relief=RAISED)
        self.label.place(x=150, y=60)

        # Văn bản cần giấu
        self.mess = StringVar()
        self.messlabel = Label(root,textvariable=self.mess)
        self.messlabel.place(x=10,y=100)
        self.mess.set("Nhập văn bản cần giấu")
        self.entryText = Entry(root)
        self.entryText.place(x=150, y=100)
        self.entryText.insert(0, "")
    
        # Nút mã hóa
        self.encodeButton = Button(self, text="Mã hóa", command=self.encode)
        self.encodeButton.place(x=150, y=140)

        # Thông tin mã hóa
        self.infVar = StringVar()
        self.inflabel = Label(root, textvariable=self.infVar,font=(None,12))
        self.inflabel.place(x=100, y=180)
        self.infVar.set("Thông tin mã hóa")

        # encoded  location label
        self.placeFileOut = StringVar()
        self.placeFileOutLabel = Label(root, textvariable=self.placeFileOut)
        self.placeFileOutLabel.place(x=10, y=220)
        self.placeFileOut.set("File sau khi mã hóa")
        self.enocdedLocation = StringVar()
        self.locationOfEncodeFile = Label(root, textvariable=self.enocdedLocation)
        self.locationOfEncodeFile.place(x=150, y=220)
        
        
        self.lengthMess = StringVar()
        self.lengthMessLabel = Label(root, textvariable=self.lengthMess)
        self.lengthMessLabel.place(x=10, y=260)
        self.lengthMess.set("Độ dài byte của message")
        self.lengthMessInf = StringVar()
        self.locationOflengthMessInf = Label(root, textvariable=self.lengthMessInf)
        self.locationOflengthMessInf.place(x=150, y=260)
        
        self.listInBit = StringVar()
        self.listInBitLabel = Label(root, textvariable=self.listInBit)
        self.listInBitLabel.place(x=10, y=300)
        self.listInBit.set("Biến đổi bit của message")
        self.bitMess = StringVar()
        self.bitMesslabel = Label(root, textvariable=self.bitMess)
        self.bitMesslabel.place(x=150, y=300)
        
    def client_exit(self):
        exit()

    def selectFile(self):
        # file selection
        root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                   filetypes=(("jpeg files", "*.wav"), ("all files", "*.*")))
        self.fileSelected = root.filename
        self.var.set(root.filename)
    def selectFileDecode(self):
        root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                   filetypes=(("jpeg files", "*.wav"), ("all files", "*.*")))
        self.fileSelcetedForDecode = root.filename
        self.decodeFileVar.set(root.filename)
    def encode(self): 
        stringToEncode = self.entryText.get()
        result = encode(self.fileSelected,stringToEncode)
        self.enocdedLocation.set(result)
        self.lengthMessInf.set(len(list_bit))
        self.bitMess.set(str(list_bit))
    def drawDecoding(self):
    
        self.decodeVar = StringVar()
        self.decodelabel = Label(root, textvariable=self.decodeVar,font=(None,20))
        self.decodelabel.place(x=700, y=10)
        self.decodeVar.set("Giải mã ")
        # File cần giải mã
        self.selectFileDecodeButton = Button(self, text="Chọn file cần giải mã ", command=self.selectFileDecode)
        self.selectFileDecodeButton.place(x=600, y=60)
        self.decodeFileVar = StringVar()
        self.decodeFileLabel = Label(root, textvariable=self.decodeFileVar, relief=RAISED)
        self.decodeFileLabel.place(x=750, y=60)

        self.decodeButton = Button(self, text="Giải mã", command=self.decode)
        self.decodeButton.place(x=700, y=140)
        #
        # decoded text label
        self.result = StringVar()
        self.resultlable = Label(root,textvariable=self.result)
        self.resultlable.place(x=600,y=100)
        self.result.set("Kết quả giải nén")
        self.decodedString = StringVar()
        self.decodedStringlabel = Label(root, textvariable=self.decodedString, font=(None, 15))
        self.decodedStringlabel.place(x=750, y=100)
    def decode(self):
        result_mess = decode(self.fileSelcetedForDecode)
        self.decodedString.set(result_mess)

root = Tk()
root.geometry("1000x500")
app = Window(root)
root.mainloop()