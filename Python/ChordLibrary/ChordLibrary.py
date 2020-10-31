from tkinter import *
from PIL import Image, ImageTk

root = Tk()
root.configure(bg="black")

root.title('Guitar Chord Library')

# Images
amaj = ImageTk.PhotoImage(Image.open('amaj.png'))

amin = ImageTk.PhotoImage(Image.open('amin.png'))

bmaj = ImageTk.PhotoImage(Image.open('bmaj.png'))

bmin = ImageTk.PhotoImage(Image.open('bmin.png'))

cmaj = ImageTk.PhotoImage(Image.open('cmaj.png'))

cmin = ImageTk.PhotoImage(Image.open('cmin.png'))

dmaj = ImageTk.PhotoImage(Image.open('dmaj.png'))

dmin = ImageTk.PhotoImage(Image.open('dmin.png'))

emaj = ImageTk.PhotoImage(Image.open('emaj.png'))

emin = ImageTk.PhotoImage(Image.open('emin.png'))

fmaj = ImageTk.PhotoImage(Image.open('fmaj.png'))

fmin = ImageTk.PhotoImage(Image.open('fmin.png'))

gmaj = ImageTk.PhotoImage(Image.open('gmaj.png'))

gmin = ImageTk.PhotoImage(Image.open('gmin.png'))

chordList = [amaj, amin, bmaj, bmin, cmaj, cmin, dmaj, dmin, emaj, emin, fmaj, fmin, gmaj, gmin]

myLabel = Label(image=amaj)
myLabel.grid(row=0, column=0, columnspan=3)

def next(imgNumber):
    global myLabel
    global buttonNext
    global buttonBack

    myLabel.grid_forget()
    myLabel = Label(image=chordList[imgNumber-1])
    buttonNext = Button(root, text='→', command=lambda: next(imgNumber+1))
    buttonBack = Button(root, text="←", command=lambda: back(imgNumber-1))

    if imgNumber == 14:
        buttonNext = Button(root, text="→", state=DISABLED)

    myLabel.grid(row=0, column=0, columnspan=3)
    buttonBack.grid(row=3, column=0)
    buttonNext.grid(row=3, column=2)

def back(imgNumber):
    global myLabel
    global buttonNext
    global buttonBack

    myLabel.grid_forget()
    myLabel = Label(image=chordList[imgNumber-1])
    buttonNext = Button(root, text='→', command=lambda: next(imgNumber+1))
    buttonBack = Button(root, text="←", command=lambda: back(imgNumber-1))

    if imgNumber == 1:
        buttonBack = Button(root, text="←", state=DISABLED)

    myLabel.grid(row=0, column=0, columnspan=3)
    buttonBack.grid(row=3, column=0)
    buttonNext.grid(row=3, column=2)


buttonBack = Button(root, text="←", command=back)
buttonNext = Button(root, text="→", command=lambda: next(2))

buttonBack.grid(row=3, column=0)
buttonNext.grid(row=3, column=2)

root.mainloop()
