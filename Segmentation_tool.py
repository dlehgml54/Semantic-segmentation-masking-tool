import os
import tkinter
from tkinter.messagebox import askyesno, Message, showinfo

import shutil
from PIL import ImageTk

from painting import *

before_img_path = './before img/'
fin_img_path = './after img/'
fin_gt_path = './GT/'
masking_path = './masking/'

os.mkdir(before_img_path,exist_ok=True)
os.mkdir(fin_img_path,exist_ok=True)
os.mkdir(fin_gt_path,exist_ok=True)
os.mkdir(masking_path,exist_ok=True)

window = tkinter.Tk()
window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('./.hide/Icon.png')))
window.title("Rail Segmentation Tool (AIVS)")
window.resizable(False, False)

crack_kinds = []

with open('config.txt', 'r', encoding='UTF-8') as f:
    for line in f.readlines():
        if '\n' in line:
            line = line[:-1]
        if '번' in line:
            line = line.split(':')[1]
            if line[0] == ' ':
                line = line[1:]
            if line != '':
                crack_kinds.append(line)
        if '항상 위' in line:
            if 'rue' in line:
                window.wm_attributes("-topmost", 1)

# len(crack_kinds) * 30
# 기본 크기?

window.geometry(f"330x{332 + len(crack_kinds) * 30}+100+100")

FONT_SIZE = 10

def revert_command():
    f_name = os.listdir(fin_gt_path)
    if len(f_name) == 0:
        showinfo(title='복구 모드', message='복구 가능한 파일이 존재하지 않습니다.')
    else:
        f_name = f_name[-1]
        double_check = askyesno(title="복구 모드", message=f'[{f_name}] 를 복구합니다.')
        if double_check:
            shutil.move(fin_img_path + f_name,before_img_path+f_name)
            os.remove(fin_gt_path+f_name)
            os.remove(masking_path+f_name)
            state.config(text=f"{len(os.listdir('./after img'))} / {len(os.listdir('./before img/')) + len(os.listdir('./after img'))}")

def next_command():
    if len(os.listdir(before_img_path)) == 0:
        showinfo(title='알림', message='작업 가능한 파일이 존재하지 않습니다.')
    else:
        segment(crack_kinds)
        state.config(text=f"{len(os.listdir('./after img'))} / {len(os.listdir('./before img/')) + len(os.listdir('./after img'))}")

total_count = len(os.listdir('./before img/')) + len(os.listdir('./after img'))
count = len(os.listdir('./after img'))

# 항상위 = True

frame1 = tkinter.Frame(width=330, height=110, relief='solid')
frame2 = tkinter.Frame(width=320, height=len(crack_kinds)*30 + 180, relief='solid', bd=2)
frame3 = tkinter.Frame(width=330, height=35, relief='solid')

logo = tkinter.PhotoImage(file='./.hide/Logo_gary_small.png')
logo_label = tkinter.Label(frame3, image=logo, relief='flat')
revert = tkinter.Button(frame1,text='복구',command=revert_command,width=5,font=FONT_SIZE)
next = tkinter.Button(frame1,text='다음',command=next_command,width=5,font=FONT_SIZE)
state = tkinter.Label(frame1, text=f"{count} / {total_count}", width=10, height=1,relief="solid",font=(FONT_SIZE,15))

revert_label = tkinter.Label(window, text="", width=60, height=1,relief="solid",font=FONT_SIZE)

explain = tkinter.Label(window, text='<단축키>', width=8, height=1,font=(FONT_SIZE,13,"bold"))


fg_list = ['red','Lime','blue','cyan','magenta2','orange','skyblue3','darkslategray4','lightpink1','darkorchid2']

for i,crack_kind in enumerate(crack_kinds):
    if i == 0:
        crack_label = tkinter.Label(frame2, text=f'{str(i + 1)[-1]} : {crack_kind} (v : 시각화)', fg=fg_list[i], font=(FONT_SIZE, 15, "bold"))
    else:
        crack_label = tkinter.Label(frame2,text=f'{str(i+1)[-1]} : {crack_kind}',fg=fg_list[i],font=(FONT_SIZE,15,"bold"))
    crack_label.place(x=20,y=15+i*30)
    if i+1 == len(crack_kinds):
        crack_label = tkinter.Label(frame2, text='z : 되돌리기', font=(FONT_SIZE, 15, "bold"))
        crack_label.place(x=20, y=15 + (i + 1) * 30)
        crack_label = tkinter.Label(frame2, text='e : 지우개', font=(FONT_SIZE, 15, "bold"))
        crack_label.place(x=20, y=15 + (i+2) * 30)
        crack_label = tkinter.Label(frame2, text='+/- : 굵기 조절', font=(FONT_SIZE, 15, "bold"))
        crack_label.place(x=20, y=15 + (i+3) * 30)
        crack_label = tkinter.Label(frame2, text='s : 저장 및 종료', font=(FONT_SIZE, 15, "bold"))
        crack_label.place(x=20, y=15 + (i+4) * 30)
        crack_label = tkinter.Label(frame2, text='esc : 저장 취소 및 종료', font=(FONT_SIZE, 15, "bold"))
        crack_label.place(x=20, y=15 + (i+5) * 30)

frame1.pack()
frame2.pack()
frame3.pack()

revert.place(x=109,y=55)
next.place(x=171,y=55)
state.place(x=110,y=20)
logo_label.place(x=115,y=2)
explain.place(x=125, y=99)

window.mainloop()