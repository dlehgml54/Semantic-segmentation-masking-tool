import tkinter
from tkinter.messagebox import askyesno, Message, showinfo
import os
import shutil
from PIL import ImageTk

from painting import *

GT_path = './GT/'
after_path = './after img/'
before_path = './before img/'
masking_path = './masking/'

window = tkinter.Tk()
window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('./.hide/Icon.png')))
window.title("Recover Tool (AIVS)")
window.resizable(False, False)
window.geometry(f"330x{180+ len(os.listdir(GT_path)) + 50}+100+100")
FONT_SIZE = 12


list_frame = tkinter.Frame(width=120, height=80, relief='solid')

scrolbar = tkinter.Scrollbar(list_frame, orient='vertical')
scrolbar.pack(side='right', fill='both')

listbox = tkinter.Listbox(list_frame, selectmode='extended', height=10, font=FONT_SIZE, yscrollcommand=scrolbar.set)
for idx, i in enumerate(os.listdir('./GT')):
    listbox.insert(idx, i)

listbox.pack(side='left', fill='both')



def btncmd():
    if len(os.listdir(GT_path)) == 0:
        showinfo(title='알림', message='작업 가능한 파일이 존재하지 않습니다.')
    else:
        recover_file = os.listdir(GT_path)[listbox.curselection()[0]]
        shutil.move(after_path+recover_file, before_path)
        listbox.delete(listbox.curselection()[0])
        os.remove(GT_path+recover_file)
        os.remove(masking_path+recover_file)
        return listbox.curselection()

btn_frame = tkinter.Frame(width=330, height=50)
btn = tkinter.Button(btn_frame,text= '복구', font=FONT_SIZE,command=btncmd)


list_frame.pack()
btn_frame.place(x=0,y=230)
btn_frame.pack()

btn.place(x=150,y=8)



window.mainloop()