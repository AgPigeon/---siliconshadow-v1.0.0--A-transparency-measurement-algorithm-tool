from tkinter import *
from tkinter import messagebox,ttk
from PIL import Image, ImageTk
import math,winsound
from typing import Any

class Compute(Frame):
    """
    传入root根容器到Compute实例，调用mainloop即可运行
    Pass the root container to the Compute instance, and call mainloop to run it

    tips:
    ①由于python重采样可能会导致图片画质有所下降，建议标注测量点后再使用本工具
    ②建议标注测量点的内框大小最小为4×4避免选点点击到边框或边框渐变色出现偶然误差

    ① Due to the potential degradation in image quality caused by Python resampling,
       it is recommended to use this tool after marking the measurement points.
    ② It is recommended that the minimum size of the inner box for marking measurement points be 4×4
       to avoid accidental errors caused by selecting points that touch the border or the border gradient

    """
    def __init__(self,master=None):
        """
        初始化所有子框架方法与绝大多数数据属性
        Initialize all sub framework methods and the vast majority of data properties
        :param master:默认导入根容器root Default import root container
        """
        super().__init__(master)
        self.master=master
        self.pack(fill=BOTH,expand=True)

        # other-significant-count-var
        """
        In the functions create: (* means notType like StringVar())
            *self.pic_path / self.grp_num / self.pairs_num /
            *self.pick_state / self.Stat_Data =>list / self.Stat_Pt
        """
        self.zh_cn_text={'F111':"缩放倍率",'F112':"左键点击取色，右键拖拽滑动，滚轮上下缩放",'F20':"图片路径:   ",'F21':"加载图像",
                         'F31':"第{grp_num}组 - 第{pairs_num}对",
                        'F32':"     当前组/对计算权重=",'F33':"     下次点击选点是:",'F34':"基准原色点",'F35':"色散参考点",'F36':"背景干扰点",
                        'F41':"当前数据组",'F42':"请加载图像后，创建初始第一组",'F51':" 创建新一组 ",'F52':" 撤销上轮操作 ",
                         'F53':" 计 算 ",'F54':"蜂鸣提示音",'F55':"异常灰度过滤",'O1':"坐标在图像外",
                         'C1': "第{i}组: 基准原色点给定的光学权重错误，值应该在0到1之间，或数据组为空",
                         'C2': "第{i}组: 本组无有效的点.\n 可用色散-背景点对数:0，原生色散-背景点对数:{lssd2}，原始选点数:{lssd1} (所有三类点) ",
                         'C3': "第{i}组: 基准原色点给定数据计算灰度值异常, 线性值应在0到255之间",
                         'C4': "第{i}组: 基准原色点异常灰度值:{Gr}",
                         'C5': "第{i}组透明度值:{grp_t} (注意！已筛选异常(亮度)值点对数:{gs_wrong}) \n 可用色散-背景点对数:{grp_ad}，原生色散-背景点对数:{lssd2}，原始总选点数:{lssd1} ",
                         'C6': "\n总加权透明度:{gen_t}"
                         } # lssd2=len(self.Stat_Data[i]) - 2) // 2 , lssd1=len(self.Stat_Data[i]) - 1 ， grp_ad=(group_adopted[i + 1] - 1) // 2
        self.eng_text={'F111':"Zoom magnification",
                       'F112':"Left-click to select color, right-click to drag and slide, scroll up and down to zoom",
                        'F20':"Image path:   ",'F21':"Load image",'F31':"Group {grp_num} - Pair {pairs_num}",
                       'F32':"  Current group/pair calculation weight is  ",
                        'F33':"  Next click to select point is  ",'F34':"ROCP",'F35':"DSP",'F36':"BIP",
                        'F41':"Current data of group",'F42':"Please load the image and create the initial first group",
                        'F51':"Create a new group",'F52':"Undo previous select",'F53':"Calculate",'F54':"Beep-sound",
                       'F55':"Abnormal grayscale filtering",'O1':"Coordinates outside the image",
                       'C1': "Group {i}: ROCP data optical-weight wrong , should be between 0 and 1, or the data set is empty",
                       'C2': "Group {i}: There is no suitable data set available.\n Effective DSP-BIP-pair:0 , Native DSP-BIP-Pair:{lssd2}, Origin all point:{lssd1} (ROCP+DSP+BIP) ",
                       'C3': "Group {i}: ROCP grayscale data wrong , should be between 0 and 1",
                       'C4': "Group {i} ROCP grayscale data wrong:{Gr}",
                       'C5': "Group {i} transparency:{grp_t}  (Special:filter GS Pair:{gs_wrong}) \n Effective DSP-BIP-pair:{grp_ad} , Native DSP-BIP-Pair:{lssd2}, Origin all point:{lssd1} (ROCP+DSP+BIP) ",
                       'C6': "\nGlobal Transparency:{gen_t}"
                       }#ROCP:Reference original color point ; DSP:Dispersion reference point ; BIP:Background interference points

        self.MIN_VAL=0.3
        self.MAX_VAL=4.5
        self.AMP_SENSITIVITY=1.2
        self.RDC_SENSITIVITY=0.8

        self.bee_beep = IntVar(value=1)
        self.Abnormal_grayscale_filter = IntVar(value=1)
        self.language_var = StringVar()
        self.language_var.set(value="zh")
        self.frame_text = self.zh_cn_text if self.language_var.get()=='zh' else self.eng_text

        self.grp_num = 0
        self.pairs_num = 0
        self.Stat_Data = [] #[[group1],[group2],……] =>    [[(Rg1,Gg1,Bg1),(Rg11……),(Rg12,……),……,pair_num],[……],……]
        self.Stat_Pt = -1
        #self.text_box = Text()

        #MVC部分的变量 MVC-part in variables
        #self.pic_path*
        self.orig_pic = Image.new('RGB',(480,480),'gray') #sentinel value
        self.pic_w , self.pic_h =  self.orig_pic.size #sentinel value

        self.scale = 1.0        #warning!!-scale time
        self.ofx, self.ofy = 0, 0
        self.tk_show_pic= None  #

        #MVC子框架实例 MVC-sub-frame instance
        self.fpic_show = Frame(self,height=720) #1 ,bg='#a0a3bc'
        self.fpath = Frame(self,height=80)  #2 self.pic_path
        self.fgr_pair = Frame(self,bg='',height=80)  #3 self.grp_num / self.pairs_num / *self.pick_state
        self.fot_disp = Frame(self,height=250)  #4 self.STAT_DATA /self.STAT_PT
        self.fbotm_groove = Frame(self,height=80)   #5

        #MVC子框架布局 MVC-sub-frame layout
        self.fpic_show.grid(sticky='',row=0,column=0)
        self.fpath.grid(sticky='',row=1,column=0,padx=5,pady=5)
        self.fgr_pair.grid(sticky='',row=2,column=0,padx=5,pady=5)
        self.fot_disp.grid(sticky='',row=3,column=0,padx=5,pady=5)
        self.fbotm_groove.grid(sticky='',row=4,column=0,padx=5,pady=5)

        self.grid_columnconfigure(0,weight=1)   #total
        self.fpic_show.grid_columnconfigure(0,weight=1)
        self.fpath.grid_columnconfigure(0,weight=1)
        self.fgr_pair.grid_columnconfigure(0,weight=1)
        self.fot_disp.grid_columnconfigure(0,weight=1)
        self.fbotm_groove.grid_columnconfigure(0,weight=1)

        #MVC子框架对应的方法 MVC-sub-frame correspond to function
        self.fpic_demonstrate()
        self.fpic_update() #first demonstrate
        self.fpath_io()
        self.fgr_pair_info()
        self.frame_realtime_data_disp()
        self.frame_bottom_groove()

        #MVC-画布对应的鼠标event MVC-canvas corresponding to the mouse event
        self.canvas_main.bind('<Button-1>',self.on_click_rgb)
        self.canvas_main.bind('<ButtonPress-3>', self.on_drag_start)
        self.canvas_main.bind('<B3-Motion>',self.on_dragging)
        self.canvas_main.bind('<MouseWheel>', self.mousewheel)

    #MVC-sub-frame function
    def fpic_demonstrate(self):
        """
        第一层Frame，主要为canvas设置与可视化实现的子框架
        The 1st layer Frame, is mainly a sub framework for canvas settings and visualization implementation
        :return:None
        """
        self.canvas_main=Canvas(self.fpic_show,bg='gray',width=640)
        self.canvas_main.pack(side='top',fill='both',expand=True)

        self.fctrl=ttk.Frame(self.fpic_show)
        self.fctrl.pack(side='bottom',fill='x',padx=5,pady=5)

        self.F111=Label(self.fctrl,text=self.frame_text['F111'])
        self.F111.pack(side='left')

        self.scale_var=DoubleVar()
        self.scale_var.set(1.0)     #zoom times

        self.scale_slider = Scale(self.fctrl,from_=self.MIN_VAL,to=self.MAX_VAL,orient='horizontal',
                                  variable=self.scale_var,command=self.scale_aiming)
        self.scale_slider.pack(side='left',fill='x',expand=True,padx=5)

        self.info_zoom = Label(self.fctrl,text=self.frame_text['F112'])
        self.info_zoom.pack(side='bottom',pady=2,padx=10)


        self.xyrgb = Label(self.fctrl,text='')
        self.xyrgb.pack(side="right",pady=2)

    def fpic_update(self):
        """
        第一层Frame的核心函数，实时计算当前宽度和高度，通过LANCZOS算法对图片重采样并调整大小，
        清空canvas，然后粘贴计算后的图片以实现缩放拖动实时显示
        The auxiliary CORE FUNCTION of First Frame：
        On-time compute current width and height, LANCZOS resamping and resizing the picture,
        clean the canvas then paste the picture that after computed,
        to achieve real-time display through zooming and dragging
        :return:None
        """
        cur_w = int(self.pic_w * self.scale)
        cur_h = int(self.pic_h * self.scale)

        scaled_pic = self.orig_pic.resize((cur_w,cur_h),Image.Resampling.LANCZOS)
            #tip
        self.tk_show_pic = ImageTk.PhotoImage(scaled_pic)   #ImageTk

        self.canvas_main.delete('all')
        self.canvas_main.create_image(self.ofx,self.ofy,anchor='nw',image=self.tk_show_pic)
        self.canvas_main.config(scrollregion=(0,0,cur_w,cur_h))

    def fpath_io(self): #self.fpath
        """
        第二层Frame，为输入图片路径的可视化子框架
        The 2nd layer Frame is a visual sub-frame for the input path of picture
        :return:None
        """
        self.F20=Label(self.fpath,text=self.frame_text['F20'])
        self.F20.pack(side='left')
        self.pic_path = StringVar()
        self.pic_path.set('Input_your_path with the format.png') #默认输入图片提示 input the path info
        Entry(self.fpath,textvariable=self.pic_path,width=75).pack(side='left')
        self.F21=Button(self.fpath,text=self.frame_text['F21'],command=self.getOriginalpic)
        self.F21.pack(side='left')

    def fgr_pair_info(self):
        """
        第三层Frame，为围绕数据采集参数的可视化提示
        The 3rd layer Frame, is a visual prompt around the data collection parameters
        :return:None
        """
        temp_F31 = self.frame_text['F31']
        self.fgp_info_num=StringVar()
        self.fgp_info_num.set(temp_F31.format(grp_num=self.grp_num,pairs_num=self.pairs_num))
        (Entry(self.fgr_pair,textvariable=self.fgp_info_num,width=18,state='readonly')
         .pack(side='left'))


        self.F32=Label(self.fgr_pair,text=self.frame_text['F32'])
        self.F32.pack(side='left') #Current Groups OW=

        self.grp_ow=StringVar()
        self.grp_ow.set('1')
        (Entry(self.fgr_pair,textvariable=self.grp_ow,width=3)
         .pack(side='left'))

        self.F33=Label(self.fgr_pair, text=self.frame_text['F33'])
        self.F33.pack(side='left')

        def prevent_click(_):
            """防止点击的“只读”函数 Prevent clicking on 'read-only' functions"""
            return "break"

        self.pick_state=IntVar()
        self.pick_state.set(-1)
        self.r1=Radiobutton(self.fgr_pair,text=self.frame_text['F34'],value=-1,variable=self.pick_state)
        self.r1.pack(side='left')
        self.r1.bind('<Button-1>',prevent_click)
        self.r2=Radiobutton(self.fgr_pair, text=self.frame_text['F35'], value=0, variable=self.pick_state)
        self.r2.pack(side='left')
        self.r2.bind('<Button-1>',prevent_click)
        self.r3=Radiobutton(self.fgr_pair, text=self.frame_text['F36'], value=1, variable=self.pick_state)
        self.r3.pack(side='left')
        self.r3.bind('<Button-1>',prevent_click)

    def frame_realtime_data_disp(self,RD_ONLY = True):
        """
        第四层Frame，为围绕数据(self.Stat_Data)的可视化子框架
        The 4th layer Frame, is a visual sub-frame around the data (self.Stat_Data)
        :param RD_ONLY: 只读测试参数，用于复制数据集并测试 Read only test parameters, used for copying datasets to test
        :return:None
        """
        self.F41=Label(self.fot_disp,text=self.frame_text['F41'],anchor='w')
        self.F41.pack(side='top')

        def prevent_click(_):
            """防止点击的“只读”函数 Prevent clicking on 'read-only' functions"""
            return "break"

        self.text_box = Text(self.fot_disp,width=96,height=14,state='normal')
        self.text_box.pack(side='top')
        self.text_box.insert(INSERT,chars=self.frame_text['F42'])   #original-disp

        if RD_ONLY:
            self.text_box.bind('<Button-1>',prevent_click)

    def frame_bottom_groove(self):
        """
        第五层Frame，主要为底部的设置操作栏
        The 5th layer Frame mainly consists of the bottom setting operation bar
        :return:None
        """
        self.F51=Button(self.fbotm_groove,text=self.frame_text['F51'],command=self.groupAdding)
        self.F51.pack(side='left',expand=True)

        self.F52=Button(self.fbotm_groove,text=self.frame_text['F52'], command=self.redoLast)
        self.F52.pack(side='left',expand=True)

        self.F53=Button(self.fbotm_groove,text=self.frame_text['F53'], command=self.totalCalculation)
        self.F53.pack(side='left',expand=True,fill='both')

        # (Button(self.fbotm_groove, text='  SHOW THE VAR  ', command=self.SHOWTHEVARTEST)
        #  .pack(side='left', expand=True, fill='both'))

        self.F54=Checkbutton(self.fbotm_groove,text=self.frame_text['F54'],variable=self.bee_beep,onvalue=1,offvalue=0)
        self.F54.pack(side='left', expand=True, fill='both')

        self.F55=Checkbutton(self.fbotm_groove,text=self.frame_text['F55'],variable=self.Abnormal_grayscale_filter,onvalue=1,offvalue=0)
        self.F55.pack(side='left', expand=True, fill='both')

        (Radiobutton(self.fbotm_groove,text='中文',value="zh",variable=self.language_var,command=self.Vslat_textConfig_update)
         .pack(side='left', expand=True, fill='both'))

        (Radiobutton(self.fbotm_groove,text="English", value="en", variable=self.language_var,command=self.Vslat_textConfig_update)
         .pack(side='left', expand=True, fill='both'))

    #MVC correspond to function
    def getOriginalpic(self):
        """
        从指定路径加载图片，转换为RGB模式，更新图片尺寸并刷新画布显示
        Load image from path, convert to RGB mode, update image dimensions and refresh canvas display
        :return:None
        """
        try:
            self.orig_pic = Image.open(self.pic_path.get()).convert('RGB')
            self.pic_w,self.pic_h = self.orig_pic.size #=>tuple
            self.fpic_update()  #!!!Loading on canvas immediately when receive commit button command

        except: #
            messagebox.showinfo(title='错误 Wrong',message='文件不存在/文件模式错误/文件格式错误 \n File does not exist / File mode error / File format error')

    def zooming(self,cx,cy,delta):
        """
        以鼠标位置为中心进行缩放，更新缩放倍数与偏移量，并刷新画布
        Zoom around the mouse position, update scale factor and offsets, then refresh canvas
        :param cx: 鼠标在画布上的X坐标 (Canvas X coordinate)
        :param cy: 鼠标在画布上的Y坐标 (Canvas Y coordinate)
        :param delta: 缩放方向，正数放大，负数缩小 (Zoom direction: positive for zoom in, negative for zoom out)
        :return: None
        """
        orx = (cx - self.ofx) / self.scale
        ory = (cy - self.ofy) / self.scale

        new_scale = self.scale * (self.AMP_SENSITIVITY if delta > 0 else self.RDC_SENSITIVITY)
        new_scale = max(self.MIN_VAL , min(self.MAX_VAL , new_scale))

        new_ofx = cx - orx * new_scale
        new_ofy = cy - ory * new_scale

        self.scale,self.ofx,self.ofy = new_scale, new_ofx, new_ofy
        self.scale_var.set(self.scale)

        self.fpic_update()

    def on_click_rgb(self,event):
        """
        点击事件，获取坐标与输入数据列表RGB Click on the event to obtain coordinates and input data list RGB
        :param event: 鼠标动作事件（左键点击）
        :return:None
        """
        orx = (event.x - self.ofx) / self.scale
        ory = (event.y - self.ofy) / self.scale

        if 0 <= orx < self.pic_w and 0<= ory < self.pic_h:
            #Group adding
            r,g,b = self.orig_pic.getpixel((int(orx),int(ory)))
                #tip
            self.xyrgb.config(text=f'({int(orx)},{int(ory)})      RGB:{r},{g},{b}')   #MVC-part

            point_weight = self.grp_ow.get()
            if self.Stat_Pt >= 0 and (not self.Stat_Data[self.Stat_Pt] and self.grp_num > 0):
                #SPECIAL first adding
                self.Stat_Data[self.Stat_Pt].append((r,g,b,point_weight))
                if self.bee_beep.get():         #Group-first-add-beep
                    winsound.Beep(1000, 150)

                self.VslatPick_state_update()  # Group-first-pick_state-update
                self.VslatTest_box_update() #Group-first-Test_box-update

            elif self.grp_num > 0:
                #Pair adding
                self.Stat_Data[self.Stat_Pt].append((r,g,b,point_weight))

                self.pairAdding()   #self.VslatFgp_info_update()
                self.VslatPick_state_update()   # Group-pick_state-update
                self.VslatTest_box_update()     #Group--Test_box-update

        else:
            self.xyrgb.config(text=self.frame_text['O1'])

    def on_drag_start(self,event):
        """
        鼠标右键按下：记录拖拽起始位置和当前偏移量
        Right-button press: record drag start position and current offsets
        :param event: 鼠标事件对象 (Mouse event object)
        :return: None
        """
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.drag_start_ofx = self.ofx
        self.drag_start_ofy = self.ofy

    def on_dragging(self,event):
        """
        鼠标右键拖拽移动：根据鼠标位移更新偏移量并刷新画布
        Right-button drag move: update offsets based on mouse displacement and refresh canvas
        :param event: 鼠标事件对象 (Mouse event object)
        :return: None
        """
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.ofx = self.drag_start_ofx + dx # ofx_new = (event_end - event_start) + ofx_old
        self.ofy = self.drag_start_ofy + dy
        self.fpic_update()

    def mousewheel(self,event):
        """
        缩放放大/缩小的正负方向确认 Confirmation of positive and negative directions for zooming in/out
        :param event: 鼠标动作事件（滚轮） Mouse Action Events (Roller)
        :return:None
        """
        delta = event.delta if hasattr(event,'delta') else event.num
        if delta>0:
            self.zooming(event.x,event.y,1)
        else:
            self.zooming(event.x,event.y,-1)

    def scale_aiming(self,event=None):
        """

        :param event:
        :return:None
        """
        new_scale = self.scale_var.get()

        if new_scale <= 0:  # 防止任何非法值并恢复上一次有效值
            self.scale_var.set(self.scale)
            return

        cx = self.canvas_main.winfo_width() // 2
        cy = self.canvas_main.winfo_height() // 2
        orx = (cx-self.ofx) / self.scale
        ory = (cy-self.ofy) / self.scale

        self.ofx = cx - orx * new_scale
        self.ofy = cy - ory * new_scale

        self.scale = new_scale
        self.fpic_update()

    #other function
    def groupAdding(self):
        """
        组数增加(包含提示音+逻辑触发+可视化)
        Increase in the number of groups (including prompt sound, logical trigger, and visualization)
        :return:None
        """
        if self.bee_beep.get():
            winsound.Beep(500, 100)
        self.Stat_Data.append([f'Group {self.grp_num+1}'])
        self.Stat_Pt += 1

        self.grp_num += 1
        self.pairs_num = 0

        self.VslatFgp_info_update()
        self.VslatTest_box_update()
        self.pick_state.set(-1) #   eval self.VslatPick_state_update()

    def groupReducing(self):
        """
        组数减少(包含提示音+逻辑检查+可视化）
        Reduce the number of groups (including prompt sound, logic check, and visualization)
        return:None
        """
        if self.bee_beep.get():
            winsound.Beep(700, 100)
            winsound.Beep(2000, 100)

        if self.grp_num>0:
            self.grp_num-=1
            self.Stat_Pt-=1

        self.pairGroupCheck()
        self.VslatFgp_info_update()
        self.VslatPick_state_update()

    def pairAdding(self):
        """
        点对的数量增加（包含提示音+逻辑触发+可视化）
        The number of point pairs has increased (including prompt sound, logical trigger, and visualization)
        :return:None
        """
        if self.bee_beep.get():
            winsound.Beep(1000, 100)

        if (len(self.Stat_Data[self.Stat_Pt])-2)//2 > self.pairs_num:
            self.pairs_num += 1
        self.VslatFgp_info_update()
        self.VslatPick_state_update()

    def pairReducing(self):
        """
        点对的数量减少（包含提示音+逻辑检查+可视化）
        The number of point pairs has decreased (including prompt sound, logic check and visualization)
        :return:None
        """
        if self.bee_beep.get():
            winsound.Beep(700, 50)
            winsound.Beep(2000, 50)

        if len(self.Stat_Data[self.Stat_Pt]) % 2 == 1 and self.pairs_num>0:
            self.pairs_num-=1

        self.VslatFgp_info_update()
        self.VslatPick_state_update()

    def pairGroupCheck(self):
        """
        撤销触发的组回退组内对数检查更新
        Revoke triggered group rollback that check to update intra group pairs num
        :return:None
        """
        if self.Stat_Pt>-1:
            self.pairs_num = max(0,(len(self.Stat_Data[self.Stat_Pt]) - 2) // 2)
        else:
            self.pairs_num = 0

    def redoLast(self):
        """
        撤销上一轮操作（数据+可视化撤回）
        Revoke the previous round of operations (data+visual recall)
        :return:None
        """
        if self.Stat_Data:
            if len(self.Stat_Data[self.Stat_Pt])>1:
                self.Stat_Data[self.Stat_Pt].pop()
                self.pairReducing()
            elif len(self.Stat_Data[self.Stat_Pt])==1:
                self.Stat_Data.pop()
                self.groupReducing()
        else:
            pass
        self.VslatTest_box_update()

    def totalCalculation(self):
        """
        总计算函数集合体:包含数据去尾（数据末不足以构成数据对）、数据筛选（不合适的 组/对 光学权重、数据计算与最终可视化
        Total calculation function set - Including data tail removal (insufficient data to form data pairs),
        data filtering (inappropriate optical weights for groups/pairs),
        data calculation, and final visualization

        temp_data 数据格式参考如下注释 The data format is referenced in the following annotations
        [['Group 1', (128, 128, 128, '1'), (128, 128, 128, '1'), (128, 128, 128, '1')],
        ['Group 2', (128, 128, 128, '1'), (128, 128, 128, '1'), (128, 128, 128, '1'), (128, 128, 128, '1')
        ,(128, 128, 128, '1'), (128, 128, 128, '1'), (128, 128, 128, '1'), (128, 128, 128, '1'), (128, 128, 128, '1')],
        ['Group 3', (128, 128, 128, '1'), (128, 128, 128, '1'), (128, 128, 128, '1'), (128, 128, 128, '1')]]

        temp_data为原生坐标点数据（仅光学权重筛选），
        leach_data为基于前者筛选“异常亮度”的点数据（如选点正好相反错误，应该选稍亮的“色散参考点”选成了稍暗的“背景干扰点”，导致透明度为负的情况）
        temp_data represents native coordinate point data (filtered by OW only)
        leach_data is a point data union-list filtered based on the former "abnormal brightness"
        (such as the error of selecting the opposite point,
         where a slightly brighter "DSP" was mistakenly selected as a slightly darker "BIP",
         resulting in a negative transparency => DSP is BIP , BIP is DSP)

        :return:None
        """

        temp_data : list[Any] = []
        for i in range(len(self.Stat_Data)):
            temp_data.append([f'Group {i+1}'])
            if len(self.Stat_Data[i]) < 2 or float(self.Stat_Data[i][1][3]) <= 0 or float(self.Stat_Data[i][1][3]) > 1: # GrpOW/Length filter illegal data groups
                continue

            #光学权重筛选 PairsOW filter
            front_check = 0
            for j in range(1,len(self.Stat_Data[i])-len(self.Stat_Data[i])%2):   #数据末端筛选（不足以构成完整一对数据时）   #Length filter:End of data filtering (when insufficient to form a complete pair of data)
                if front_check:
                    front_check = 0
                    continue
                if float(self.Stat_Data[i][j][3]) > 1 or float(self.Stat_Data[i][j][3]) <= 0:
                    if j%2==0:  #数据对的首位权重异常 front-data illegal in pair
                        front_check=1
                    else:   #数据对的末位权重异常 rear-data illegal in pair
                        temp_data[i].pop()
                    continue
                temp_data[i].append(self.Stat_Data[i][j])

        res = []        #结果显示集 Visualization result set
        gen_t = 0.0     #总体透明度 general transparency

        leach_data : list[Any] = []
        gs_wrong = [0]*len(temp_data)

        for i in range(len(temp_data)):
            # Effective DSP-BIP-pair :After screening for residual pairs and illegal OW
            # Native DSP-BIP-Pair    :Only through residual pairs screening (tail removal)
            # Origin all point       :All data points entered through effective mouse clicks
            # 有效对-经过残对+非法权重筛选 ；原生对-仅经过残对去尾筛选 ； 原始点：所有鼠标点击输入的有效数据点

            leach_data.append([f'Group{i+1}'])
            if len(temp_data[i]) <= 1:  # ROCP data optical-weight wrong
                leach_data[i].append(101)   #Type101 error info
            elif len(temp_data[i]) == 2:  # Filter more DSP-BIP points only left grp-name and ROCP
                leach_data[i].append(102)   #Type102 error info
            else:
                rr, rg, rb, gow = temp_data[i][1]  # ROCP's RGB and Group optical-weight
                rr, rg, rb = self.mathNormalization(rr), self.mathNormalization(rg), self.mathNormalization(rb)
                rr, rg, rb = self.mathCorrectGammaValue(rr), self.mathCorrectGammaValue(rg), self.mathCorrectGammaValue(rb)
                rr, rg, rb = self.mathLinearization(rr), self.mathLinearization(rg), self.mathLinearization(rb)
                Gr = self.mathBrightnessFormula(rr, rg, rb)
                # 基准原色点灰度处理 Grayscale processing of ROCP
                # 基准原色点灰度异常过滤 Grayscale anomaly filtering of ROCP
                if self.Abnormal_grayscale_filter.get() == 1 and (Gr > 255 or Gr < 0):  #StringVar() should have get()!
                    leach_data[i].append(103)      #Type103 error info 基准原色点给定数据计算灰度(亮度)值异常
                    continue
                else:
                    leach_data[i].append((Gr,float(gow),0))

                for j in range(2, len(temp_data[i]), 2):
                    dr, dg, db, dpsow = temp_data[i][j]
                    br, bg, bb, bpsow = temp_data[i][j + 1]
                    psow = (float(dpsow) + float(bpsow)) / 2 #pairs ow

                    #归一化 => 逆伽马矫正 => 线性化 => Rec.709标准计算灰度(亮度)/过滤 => 相对灰度做商得到相对透明度/过滤 => 数据统计
                    # Normalization , RGB-MAX=255
                    dr, dg, db = self.mathNormalization(dr), self.mathNormalization(dg), self.mathNormalization(db)
                    br, bg, bb = self.mathNormalization(br), self.mathNormalization(bg), self.mathNormalization(bb)
                    # CorrectGammaValue
                    dr, dg, db = self.mathCorrectGammaValue(dr), self.mathCorrectGammaValue(dg), self.mathCorrectGammaValue(db)
                    br, bg, bb = self.mathCorrectGammaValue(br), self.mathCorrectGammaValue(bg), self.mathCorrectGammaValue(bb)
                    # Linearization , RGB-MAX=255
                    dr, dg, db = self.mathLinearization(dr), self.mathLinearization(dg), self.mathLinearization(db)
                    br, bg, bb = self.mathLinearization(br), self.mathLinearization(bg), self.mathLinearization(bb)
                    # Rec.709 Grayscale(Brightness) calculation
                    Gd = self.mathBrightnessFormula(dr, dg, db)
                    Gb = self.mathBrightnessFormula(br, bg, bb)
                    if self.Abnormal_grayscale_filter.get() == 1 and (Gd > 255 or Gd < 0 or Gb > 255 or Gb < 0):
                        gs_wrong[i] += 1
                        continue
                    # Calculate Transparency
                    alpha = self.mathTransparencyFormula(Gr, Gd, Gb)

                    if self.Abnormal_grayscale_filter.get() == 1 and (alpha > 1 or alpha < 0):
                        gs_wrong[i] += 1
                        continue
                    leach_data[i].append((alpha,psow,j))

        total_gow = 0.0  # 总组间权重和 Sum of total intergroup OW
        total_pow = []  # 各组内对间权重和 Sum of OW between data pairs within each group
        for i in range(len(leach_data)):
            total_pow_add = 0
            if isinstance(leach_data[i][1],tuple):   #[ ['Group1',101],['Group2',(Gr,gow,0),(a,psow,front_idx)] , []   ]
                total_gow += leach_data[i][1][1]
                for j in range(2,len(leach_data[i])): #[ ['Group1',(Gr, gow, 0),(a,psow)]  ,     []   ]
                    total_pow_add += leach_data[i][j][1]
            total_pow.append(total_pow_add)

        gen_t=0.0
        for i in range(len(leach_data)):
            if isinstance(leach_data[i][1],tuple):
                grp_t=0.0
                for j in range(2,len(leach_data[i])):
                    grp_t += leach_data[i][j][0] * ( leach_data[i][j][1] / total_pow[i])
                gen_t += grp_t * (leach_data[i][1][1] / total_gow)
                res.append(self.frame_text['C5'].format(i=i+1, grp_t=grp_t, gs_wrong=gs_wrong[i],
                                                        grp_ad=(len(self.Stat_Data[i]) - 2) // 2 - gs_wrong[i],
                                                        lssd2=(len(self.Stat_Data[i]) - 2) // 2,
                                                        lssd1=(len(self.Stat_Data[i]) - 1)))
            elif leach_data[i][1]==101:
                res.append(self.frame_text['C1'].format(i=i + 1))
            elif leach_data[i][1]==102:
                res.append(self.frame_text['C2'].format(i=i + 1, lssd2=(len(self.Stat_Data[i]) - 2) // 2,
                                                        lssd1=(len(self.Stat_Data[i]) - 1)))
            elif leach_data[i][1]==103:
                res.append(self.frame_text['C3'].format(i=i+1)) # 基准原色点给定数据计算灰度值异常

        res.append(self.frame_text['C6'].format(gen_t=gen_t))
        msg = '\n'.join(res)
        print(msg)
        print(temp_data)

        messagebox.showinfo(title='Result 结果',message=msg)

    def mathNormalization(self,color_channel,MAX=255):
        """
        单通道归一化 Convert linear single channel color values to normalized single channel color values
        :param color_channel: 单通道(R/G/B) single channel(R/G/B)
        :param MAX: 8bitRGB is 255
        :return: color_channel / MAX => float
        """
        return color_channel / MAX

    def mathLinearization(self,color_channel,MAX=255):
        """
        单通道线性化 Convert normalized single channel color values to linear single channel color values
        :param color_channel:  单通道(R/G/B) single channel(R/G/B)
        :param MAX: 8bitRGB is 255
        :return:  color_channel * MAX => float
        """
        return color_channel * MAX

    def mathCorrectGammaValue(self,nml_channel,CABV=0.04045,GCO=2.4):
        """
        计算单通道逆伽马处理得到的处理单通道值
        Segmented function to restore non-linear signals (such as sRGB) used for storage/display
         to linear light intensity values that conform to physical lighting laws
         like the ratio of physical light intensity or grayscale value
        :param nml_channel: 归一化单通道值 Normalization single channel
        :param CABV:分段函数连续近似边界值 Piecewise function continuous approximate boundary value
        :param GCO:伽马曲线偏移值 Gamma curve offset(Gamma value)
        :return: math.pow((nml_channel+0.055)/1.055,GCO) or nml_channel / 12.92 => float
        """
        if nml_channel >= CABV:
            return math.pow((nml_channel+0.055)/1.055,GCO)  #Gamma curve offset(Gamma value)
        else:
            return nml_channel / 12.92  #linear approximation

    def mathBrightnessFormula(self,r,g,b,rw=0.2126,gw=0.7152,bw=0.0722):
        """
        计算Rec.709标准亮度权重下的RGB通道混合亮度/灰度（线性0-255）
        After calculating the normalized single channel values and inverse gamma processing,
        and re-linearizing the three single channel values, they are converted into
         color brightness grayscale values based on Rec.709 standard weights(value should between 0 and 255)
        :param r:逆伽马R通道值 Reverse gamma R-channel value
        :param g:逆伽马G通道值 Reverse gamma G-channel value
        :param b:逆伽马B通道值 Reverse gamma B-channel value
        :param rw:Rec.709标准的R通道权重 R channel weights for Rec.709 standard
        :param gw:Rec.709标准的G通道权重 G channel weights for Rec.709 standard
        :param bw:Rec.709标准的B通道权重 B channel weights for Rec.709 standard
        :return:rw*r + gw*g + bw*b =>float (有效值域 Effective range[0,255])
        """
        return rw*r + gw*g + bw*b

    def mathTransparencyFormula(self,R,D,B):
        """
        通过（色散参考点-背景干扰点）÷（基准原色点-背景干扰点）得到在背景干扰点下的相对亮度即透明度
        Subtracting grayscale to obtain relative grayscale, and then dividing to obtain brightness value
        R means ROCP : Reference original color point 基准原色点 ;
        D means DRP : Dispersion reference point 色散参考点 ;
        B means BIP :Background interference points 背景干扰点

        :return:(D-B)/(R-B) : 透明度/transparency =>float (有效值域 Effective range[0,1])
         Tips:当基准原色点与背景干扰点在灰度亮度相同时，姑且认为混合通道下灰度无法衡量该对即不可分 (R-B=0)
            When the ROCP and BIP have the same grayscale brightness, it can be assumed that
            the grayscale in the mixed channel cannot measure the pair and cannot be separated
        """
        return (D - B) / (R - B) if R - B != 0 else 0.0

    def VslatFgp_info_update(self):
        """
        更新组数-点对数的可视化函数
        The visualization function of updating the grps-pairs number
        :return:None
        """
        temp_F31 = self.frame_text['F31']
        self.fgp_info_num.set(temp_F31.format(grp_num=self.grp_num,pairs_num=self.pairs_num))

    def VslatPick_state_update(self):
        """
        更新提示当前选点类型的可视化函数（基准原色点+色散参考点+背景干扰点）
        The visualization function of updating current selection type prompt(ROCP+DRP+BIP)
        :return:None
        """
        if self.Stat_Pt >= 0:
            if len(self.Stat_Data[self.Stat_Pt])>1:
                self.pick_state.set(len(self.Stat_Data[self.Stat_Pt]) % 2)
            else:
                self.pick_state.set(-1)

    def VslatTest_box_update(self):
        """
        即时数据刷新显示    Real-time data(self.Stat) refresh display
        :return:None
        """
        self.text_box.delete('1.0', END)
        if self.Stat_Pt > -1:
            self.text_box.insert(INSERT,f'{self.Stat_Data}')
        else:
            self.text_box.insert(INSERT,self.frame_text['F42'])

    def Vslat_textConfig_update(self):
        """
        即时语言刷新  Real-time language text switching
        :return:None
        """
        self.frame_text = self.zh_cn_text if self.language_var.get() == 'zh' else self.eng_text

        self.F111.config(text=self.frame_text['F111'])
        self.info_zoom.config(text=self.frame_text['F112'])

        self.F20.config(text=self.frame_text['F20'])
        self.F21.config(text=self.frame_text['F21'])

        temp_F31 = self.frame_text['F31']
        self.fgp_info_num.set(temp_F31.format(grp_num=self.grp_num, pairs_num=self.pairs_num))
        self.F32.config(text=self.frame_text['F32'])
        self.F33.config(text=self.frame_text['F33'])
        self.r1.config(text=self.frame_text['F34'])
        self.r2.config(text=self.frame_text['F35'])
        self.r3.config(text=self.frame_text['F36'])

        self.F41.config(text=self.frame_text['F41'])
        # self.text_box ORIGIN TIPS F42
        if self.Stat_Pt == -1:
            self.text_box.delete(1.0,END)
            self.text_box.insert(INSERT,chars=self.frame_text['F42'])

        self.F51.config(text=self.frame_text['F51'])
        self.F52.config(text=self.frame_text['F52'])
        self.F53.config(text=self.frame_text['F53'])
        self.F54.config(text=self.frame_text['F54'])
        self.F55.config(text=self.frame_text['F55'])

        self.xyrgb.config(text=self.frame_text['O1'])

    def SHOWTHEVARTEST(self):
        """
        终端临时数据监控函数，有对应未pack组件在frame_bottom_groove中
        Temporary data monitoring function in terminal, with corresponding un-pack components in frame-bottom_groove
        :return:None
        """
        print("Stat_Pt | grp_num | pairs_num | Stat_Data")

        print(self.Stat_Pt, self.grp_num, self.pairs_num, self.Stat_Data)

        print("pick_state:", self.pick_state.get())  # f'{len(self.Stat_Data[self.Stat_Pt]) % 2}

        self.VslatTest_box_update()

    def Placeholder_function(self):
        """
        测试组件占位函数
        Testing component occupancy function
        :return:None
        """
        pass

if __name__=='__main__':
    root=Tk()
    root.title('硅影Silicon shadow v1.0.0')
    root.geometry("854x720+350+50")

    general = Compute(root)
    general.mainloop()

    # print(Compute.__dict__)