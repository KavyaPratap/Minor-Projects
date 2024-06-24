from tkinter import *
from tkinter import filedialog
from pytube import YouTube
from moviepy.editor import *
import shutil#it allows us to move a specific file from one path to another

root=Tk()
root.title("Video Downloader")

def select_path():
    path=filedialog.askdirectory()
    path_lable.config(text=path)

def download_button_func():
    video_path=entry_url.get()
    file_path=path_lable.cget("text")#This function gets the value of a property on a previously created function
    print("Downloading")
    mp4=YouTube(video_path).streams.get_highest_resolution().download()
    videoclip=VideoFileClip(mp4)
    audio_file=videoclip.audio
    audio_file.write_audiofile("audio.mp3")
    videoclip.close()
    shutil.move(mp4,file_path)
    print("Download complete")



canvas=Canvas(root,width=400,height=300,bg="#d0efff")
canvas.pack()
#app label

app_label=Label(root,text="Video Downloader", fg="blue",font=("algerian",28),bg="#b4eaff",highlightbackground="#7dffe0")
canvas.create_window(200,50,window=app_label)

#entry for video url
url_label=Label(root,text="Enter Url:",bg="#b4eaff",highlightbackground="#7dffe0",)
canvas.create_window(200,75,window=url_label)
entry_url=Entry(root)
canvas.create_window(200,100,window=entry_url)

#path to download video
path_lable=Label(root,text="Select Path to Download ",bg="#b4eaff",highlightbackground="#7dffe0")
path_button=Button(root,text="Select",bg="#b4eaff",highlightbackground="#7dffe0",command=select_path)
canvas.create_window(200,150,window=path_lable)
canvas.create_window(200,175,window=path_button)

#download button

download_button=Button(root,text="Download",bg="#b4eaff",highlightbackground="#7dffe0",command=download_button_func)
canvas.create_window(200,250,window=download_button)



root.mainloop()
