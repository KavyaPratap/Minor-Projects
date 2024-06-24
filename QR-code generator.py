import pyqrcode
from tkinter import *
from PIL import ImageTk,Image

root=Tk()
#backend--

def generate():
    link_name=name_entry.get()
    link=link_entry.get()
    
    file_name=link_name + ".png" #creating a .png file
    url=pyqrcode.create(link)           #creating qr of url
    url.png(file_name,scale=8)          #determining size of qr, with scale attribute   
    image=ImageTk.PhotoImage(Image.open(file_name)) #opening image into tkinter window
    image_label=Label(image=image)  #adding image lable
    image_label.image=image             
    canvas.create_window(200,450,window=image_label)#packing onto gui



#frontend--
root.title("QR Code Generator")

canvas=Canvas(root,width="400",height="600")
canvas.pack()
app_label=Label(root,text="QR Code Generator", fg="Black",bg="aqua",font=("algerian",28))
canvas.create_window(200,50,window=app_label)#instead of pack or grid, in canvas we use this

name_label=Label(root,text="Link Name-")
link_label=Label(root,text="Link-")
canvas.create_window(200,100,window=name_label)
canvas.create_window(200,160,window=link_label)

name_entry=Entry(root)
link_entry=Entry(root)
canvas.create_window(200,130,window=name_entry)
canvas.create_window(200,180,window=link_entry)

button=Button(root,text="Generate",command=generate)
canvas.create_window(200,230,window=button)



root.mainloop()
