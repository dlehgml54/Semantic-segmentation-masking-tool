import cv2
import os
from PIL import ImageFont, ImageDraw,Image
import numpy as np

def draw_region(origin_img,range_pos):
    global fill
    region_img = origin_img.copy()
    if fill:
        value = -1
    else:
        value = 2

    for pos in range_pos:
        cv2.rectangle(region_img, (pos[0], pos[1]), (pos[2], pos[3]), (0, 0, 255), value)
    return region_img

def save(origin_img, range_pos, local_img, img_name, crack_list, colors):
    before_img_path = './before img/'
    fin_img_path = './after img/'
    fin_gt_path = './GT/'
    masking_path = './masking/'

    os.remove(before_img_path + img_name)

    save_img = np.zeros_like(origin_img)
    range_img = np.zeros_like(origin_img)

    for pos in range_pos:
        cv2.rectangle(range_img, (pos[0], pos[1]), (pos[2], pos[3]), (0,0,255),-1)

    mask_red = cv2.inRange(range_img,colors[0],colors[0])

    for i in range(1, len(crack_list)):
        mask = cv2.inRange(local_img, colors[i], colors[i])
        mask_red = cv2.bitwise_xor(mask_red,cv2.bitwise_and(mask_red,mask))
        save_img += cv2.bitwise_and(local_img,local_img,mask=mask)

    save_img += cv2.bitwise_and(range_img, range_img, mask=mask_red)

    gt_img_mask = cv2.bitwise_and(origin_img,origin_img,mask=cv2.inRange(save_img,(0,0,0),(0,0,0))) + save_img

    cv2.imwrite(fin_img_path+img_name,origin_img)
    cv2.imwrite(fin_gt_path+img_name,save_img)
    cv2.imwrite(masking_path+img_name,gt_img_mask)

def line_display(img,linewidth,erase,fake_color,erase_img):
    h,w = img.shape[:-1]
    cv2.rectangle(img,(w-33,0),(w,33),(0,0,0),-1)
    if erase == True:
        img[:33,-33:,:] = erase_img
    else:
        cv2.circle(img,(w-16,16),linewidth,fake_color,-1)
    cv2.imshow('draw segmentation',img)

def Range_Segment(event, x, y, flags, param):
    global click, x1, y1, range_pos, b, backup_img, fill

    if event == cv2.EVENT_LBUTTONDOWN:  # 마우스를 누른 상태
        x1, y1 = x, y
        click = True
        if len(backup_img) == 10:
            backup_img.pop(0)
        backup_img.append([0,param.copy(),range_pos.copy()])

    elif event == cv2.EVENT_MOUSEMOVE and click == True:  # 마우스 이동
        temp = param.copy()
        cv2.rectangle(temp, (x1, y1), (x, y), (0,0,255),thickness=2)
        cv2.imshow('draw segmentation', temp)

    elif event == cv2.EVENT_LBUTTONUP:
        if(x1>x):
            x,x1 = x1,x
        if(y1>y):
            y,y1 = y1,y
        range_pos.append((x1, y1, x, y))
        if fill:
            thickness = -1
        else:
            thickness = 2
        cv2.rectangle(param, (x1, y1), (x, y), (0,0,255),thickness=thickness)
        click = False
        cv2.imshow('draw segmentation', param)


def Line_Segment(event, x, y, flags, param):
    #parm 는 img,line_width,color
    global old_x, old_y, line_width, backup_img

    if event == cv2.EVENT_LBUTTONDOWN:
        old_x,old_y = x,y
        if len(backup_img) == 10:
            backup_img.pop(0)
        backup_img.append([1, param[0].copy(),None])

    elif event == cv2.EVENT_MOUSEMOVE:
        if flags & cv2.EVENT_FLAG_LBUTTON:
            cv2.line(param[0], (old_x,old_y),(x,y),param[2],param[1], cv2.LINE_4)
            old_x, old_y = x, y

    cv2.imshow('draw segmentation', param[0])

def Erase_region(event, x, y, flags, param):
    global click, range_pos
    e_pos_idx = []
    if event == cv2.EVENT_LBUTTONDOWN:
        for idx,pos in enumerate(range_pos):
            if pos[0] <= x <= pos[2] and pos[1] <= y <= pos[3]:
                e_pos_idx.append(idx)

        if len(backup_img) == 10:
            backup_img.pop(0)
        backup_img.append([0, param[0].copy(), range_pos.copy()])

        for idx in e_pos_idx[::-1]:
            pos = range_pos.pop(idx)
            param[0][pos[1]:pos[3] + 1, pos[0]:pos[2] + 1] = param[1][pos[1]:pos[3] + 1, pos[0]:pos[2] + 1]
            param[0][:,:] = param[1][:, :]

        for pos in range_pos:
            cv2.rectangle(param[0], (pos[0], pos[1]), (pos[2], pos[3]), (0,0,255),thickness=2)

    cv2.imshow('draw segmentation', param[0])


def Erase_local(event, x, y, flags, param):
    global click

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(backup_img) == 10:
            backup_img.pop(0)
        backup_img.append([1,param[0].copy(),None])

    if event == cv2.EVENT_MOUSEMOVE:
        if flags & cv2.EVENT_FLAG_LBUTTON:
            click = True
            param[0][y - 8:y + 9, x - 8:x + 9] = param[1][y - 8:y + 9, x - 8:x + 9]
            cv2.imshow('draw segmentation', param[0])

    if event == cv2.EVENT_LBUTTONUP:
            click = False

def segment(crack_list):
    # ===== 기본 설정 ===== #
    before_img_path = './before img/'

    fake_colors = [(0, 0, 254), (0, 254, 0), (254, 0, 0),(254, 255, 0),(254, 0, 255),(0, 165, 254), (254,164,164), (163,164,0),(164,164,254),(206,41,194)]
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0),(255, 255, 0),(255, 0, 255),(0, 165, 255), (255,164,164), (164,164,0),(164,164,255),(207,41,194)]

    line_width = 4
    fake_color = fake_colors[0]
    color = colors[0]
    erase_img = cv2.imread('./.hide/erase.png',1)

    global x1, y1, click, range_pos, backup_img, fill
    x1, y1, click,range_pos,backup_img,fill = 0, 0, False,[],[],False


    img_name = os.listdir('./before img/')[0]
    height = 1000
    origin_img = cv2.imread(before_img_path+img_name)
    padding = int((1920 * origin_img.shape[0]) / height - origin_img.shape[1])
    # pad = np.zeros((1200, padding, 3))
    # print(pad.shape,origin_img.shape)
    # origin_img = np.concatenate([pad,origin_img],axis=1)
    origin_img = np.pad(origin_img,((0,0),(int(padding//2),int(padding//2)),(0,0)))
    origin_img = cv2.resize(origin_img, (1920,height), fx=height/origin_img.shape[0])
    range_img = origin_img.copy()
    local_img = origin_img.copy()


    mode = 'range'

    cv2.imshow('draw segmentation', range_img)
    line_display(range_img, line_width, False, fake_color, erase_img)
    cv2.setMouseCallback('draw segmentation', Range_Segment, param=range_img)

    while True:
        input_key = cv2.waitKey()
        if input_key == ord(f"{1}"):
            fake_color = fake_colors[0]
            mode = 'range'
            range_img = draw_region(origin_img, range_pos)
            cv2.imshow('draw segmentation',range_img)
            cv2.setMouseCallback('draw segmentation',Range_Segment,param=range_img)

        for i in range(2,len(crack_list)+1):
            if input_key == ord(f"{str(i)[-1]}"):
                mode = 'local'
                color = colors[i-1]
                fake_color = fake_colors[i-1]
                cv2.imshow('draw segmentation', local_img)
                cv2.setMouseCallback('draw segmentation',Line_Segment,param=[local_img,line_width,color])

        if input_key == ord("e") or input_key == ord("E"):
            if mode == 'range':
                cv2.setMouseCallback('draw segmentation', Erase_region, param=[range_img,origin_img])
            elif mode == 'local':
                cv2.setMouseCallback('draw segmentation', Erase_local, param=[local_img,origin_img])
            erase = True
        else:
            erase = False

        if input_key == ord("+"):
            if line_width < 15:
                line_width += 1
                cv2.setMouseCallback('draw segmentation',Line_Segment,param=[local_img,line_width,color])

        elif input_key == ord("-"):
            if line_width > 2:
                line_width -= 1
                cv2.setMouseCallback('draw segmentation',Line_Segment,param=[local_img,line_width,color])

        elif input_key == ord("v"):
            fill = not fill
            fake_color = fake_colors[0]
            mode = 'range'
            range_img = draw_region(origin_img, range_pos)
            cv2.imshow('draw segmentation',range_img)
            cv2.setMouseCallback('draw segmentation',Range_Segment,param=range_img)

        elif input_key == ord("z"):
            if len(backup_img) != 0:
                is_local, img, range_pos_temp = backup_img.pop(-1)
                if is_local:
                    local_img = img.copy()
                    cv2.imshow('draw segmentation', local_img)
                    fake_color = fake_colors[1]
                    color = colors[1]
                    cv2.setMouseCallback('draw segmentation',Line_Segment,param=[local_img,line_width,color])
                    mode = 'local'
                else:
                    range_pos = range_pos_temp
                    range_img = draw_region(origin_img,range_pos)
                    cv2.imshow('draw segmentation', range_img)
                    cv2.setMouseCallback('draw segmentation',Range_Segment,param=range_img)
                    mode = 'range'
                    fake_color = fake_colors[0]
            erase = False

        elif input_key == 27: # esc
            break

        elif input_key == ord("s") or input_key == ord("S"):
            save(origin_img, range_pos, local_img, img_name, crack_list, colors)
            break

        if mode == 'range':
            line_display(range_img,line_width,erase,fake_color,erase_img)
        elif mode == 'local':
            line_display(local_img,line_width,erase,fake_color,erase_img)

    cv2.destroyAllWindows()