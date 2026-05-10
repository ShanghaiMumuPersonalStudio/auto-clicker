import tkinter as tk
from tkinter import ttk
import threading
import time
import keyboard
import pyautogui
import win32api
import win32con

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("自动连点器")
        self.root.geometry("520x400")  # 增大窗口大小
        self.root.resizable(False, False)
        
        # 设置窗口图标和样式
        self.root.configure(bg="#f0f0f0")
        
        self.status = False
        self.hotkey = "F6"
        self.repeat_times = 0
        self.click_interval = 0
        self.click_type = "点击"
        self.position_mode = "实时获取鼠标位置"
        self.click_position = "未设置"
        
        self.create_ui()
        self.setup_hotkey()
    
    def create_ui(self):
        # 配置样式
        style = ttk.Style()
        style.configure('TButton', padding=6, font=('Arial', 10))
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TRadiobutton', font=('Arial', 10))
        
        # 顶部按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=15, padx=25, fill="x")
        ttk.Button(button_frame, text="热键设置", command=self.open_hotkey_settings, width=15).pack(side="left", padx=15)
        ttk.Button(button_frame, text="关于", command=self.open_about_window, width=15).pack(side="right", padx=15)
        
        # 主内容区域
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # 第一行：显示热键
        row1 = ttk.Frame(main_frame)
        row1.pack(pady=12, fill="x")
        ttk.Label(row1, text="启动/停止热键:", width=16, font=('Arial', 11)).pack(side="left")
        self.hotkey_label = ttk.Label(row1, text=self.hotkey, font=("Arial", 14, "bold"), foreground="#0066cc")
        self.hotkey_label.pack(side="left", padx=10)
        
        # 第二行：重复次数
        row2 = ttk.Frame(main_frame)
        row2.pack(pady=12, fill="x")
        ttk.Label(row2, text="重复次数:", width=16, font=('Arial', 11)).pack(side="left")
        self.repeat_var = tk.StringVar(value="0")
        ttk.Entry(row2, textvariable=self.repeat_var, width=12, font=('Arial', 11)).pack(side="left", padx=10)
        ttk.Label(row2, text="(0=无限)", font=('Arial', 9, 'italic')).pack(side="left")
        
        # 第三行：每次点击间隔毫秒数
        row3 = ttk.Frame(main_frame)
        row3.pack(pady=12, fill="x")
        ttk.Label(row3, text="点击间隔:", width=16, font=('Arial', 11)).pack(side="left")
        self.interval_var = tk.StringVar(value="0")
        ttk.Entry(row3, textvariable=self.interval_var, width=12, font=('Arial', 11)).pack(side="left", padx=10)
        ttk.Label(row3, text="毫秒", font=('Arial', 11)).pack(side="left")
        
        # 第四行：点击类型选项
        row4 = ttk.Frame(main_frame)
        row4.pack(pady=12, fill="x")
        ttk.Label(row4, text="点击类型:", width=16, font=('Arial', 11)).pack(side="left")
        self.click_type_var = tk.StringVar(value="点击")
        click_type_frame = ttk.Frame(row4)
        click_type_frame.pack(side="left")
        ttk.Radiobutton(click_type_frame, text="拖动", variable=self.click_type_var, value="拖动", width=8).pack(side="left", padx=8)
        ttk.Radiobutton(click_type_frame, text="点击", variable=self.click_type_var, value="点击", width=8).pack(side="left", padx=8)
        ttk.Radiobutton(click_type_frame, text="双击", variable=self.click_type_var, value="双击", width=8).pack(side="left", padx=8)
        
        # 第五行：位置获取方式
        row5 = ttk.Frame(main_frame)
        row5.pack(pady=12, fill="x")
        ttk.Label(row5, text="位置获取:", width=16, font=('Arial', 11)).pack(side="left")
        self.position_var = tk.StringVar(value="实时获取鼠标位置")
        position_frame = ttk.Frame(row5)
        position_frame.pack(side="left")
        ttk.Radiobutton(position_frame, text="点击确认位置", variable=self.position_var, value="通过点击确认点击位置", width=14).pack(side="left", padx=5)
        ttk.Radiobutton(position_frame, text="实时获取位置", variable=self.position_var, value="实时获取鼠标位置", width=14).pack(side="left", padx=5)
        
        # 第六行：状态显示
        row6 = ttk.Frame(main_frame)
        row6.pack(pady=12, fill="x")
        ttk.Label(row6, text="当前状态:", width=16, font=('Arial', 11)).pack(side="left")
        self.status_label = ttk.Label(row6, text="停止", font=("Arial", 14, "bold"), foreground="#cc3333")
        self.status_label.pack(side="left")
        
        # 第七行：点击位置显示
        row7 = ttk.Frame(main_frame)
        row7.pack(pady=12, fill="x")
        ttk.Label(row7, text="点击位置:", width=16, font=('Arial', 11)).pack(side="left")
        self.position_label = ttk.Label(row7, text=self.click_position, font=('Arial', 10))
        self.position_label.pack(side="left")
    
    def open_hotkey_settings(self):
        # 热键设置窗口
        hotkey_window = tk.Toplevel(self.root)
        hotkey_window.title("热键设置")
        hotkey_window.geometry("400x200")
        hotkey_window.resizable(False, False)
        
        ttk.Label(hotkey_window, text="当前热键: " + self.hotkey).pack(pady=20)
        
        # 提示用户点击热键
        status_label = ttk.Label(hotkey_window, text="请点击想要设置的热键...")
        status_label.pack(pady=20)
        
        # 捕获用户按键
        def on_key_press(event):
            # 获取按下的键
            new_hotkey = event.keysym
            if new_hotkey:
                # 移除旧热键
                keyboard.remove_hotkey(self.hotkey)
                # 设置新热键
                self.hotkey = new_hotkey
                keyboard.add_hotkey(self.hotkey, self.toggle_status)
                # 更新热键标签
                self.hotkey_label.config(text=self.hotkey)
                # 更新状态提示
                status_label.config(text=f"热键已设置为: {new_hotkey}")
                # 2秒后关闭窗口
                hotkey_window.after(2000, hotkey_window.destroy)
        
        # 绑定按键事件
        hotkey_window.bind("<KeyPress>", on_key_press)
        
        # 提示信息
        ttk.Label(hotkey_window, text="按任意键设置为新热键").pack(pady=10)
        ttk.Label(hotkey_window, text="点击窗口外部可取消").pack(pady=5)
    
    def open_about_window(self):
        # 关于窗口
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        
        ttk.Label(about_window, text="自动连点器 v2.0", font=("Arial", 14)).pack(pady=20)
        ttk.Label(about_window, text="制作团队:", font=("Arial", 12)).pack(pady=10, anchor="w", padx=20)
        ttk.Label(about_window, text="上海木木个人工作室").pack(pady=2, anchor="w", padx=40)
        ttk.Label(about_window, text="获取本软件:", font=("Arial", 12)).pack(pady=10, anchor="w", padx=20)
        # 添加GitHub链接按钮
        def open_github():
            import os
            # 使用系统命令打开链接，让系统转到指定地址
            os.system(f'start https://github.com/ShanghaiMumuPersonalStudio/auto-clicker')
        ttk.Button(about_window, text="访问GitHub仓库", command=open_github).pack(pady=10, padx=40, anchor="w")
        ttk.Label(about_window, text="遵循GPL v3开源协议").pack(pady=2, anchor="w", padx=40)
    
    def setup_hotkey(self):
        keyboard.add_hotkey(self.hotkey, self.toggle_status)
    
    def toggle_status(self):
        self.status = not self.status
        if self.status:
            self.status_label.config(text="正在点击", foreground="green")
            # 启动点击线程
            threading.Thread(target=self.click_loop, daemon=True).start()
        else:
            self.status_label.config(text="停止", foreground="red")
    
    def click_loop(self):
        # 避免热键未松开的情况
        time.sleep(0.1)
        
        repeat_times = int(self.repeat_var.get())
        click_interval_ms = int(self.interval_var.get())
        click_type = self.click_type_var.get()
        position_mode = self.position_var.get()
        
        # 如果选择通过点击确认位置，先获取点击位置
        target_position = None
        if position_mode == "通过点击确认点击位置":
            self.position_label.config(text="请点击目标位置...")
            
            # 获取屏幕尺寸
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # 创建全屏十字架窗口
            cross_window = tk.Toplevel(self.root)
            cross_window.overrideredirect(True)  # 无边框
            cross_window.attributes('-alpha', 0.5)  # 半透明
            cross_window.attributes('-topmost', True)  # 置顶
            cross_window.geometry(f"{screen_width}x{screen_height}+0+0")
            cross_window.attributes('-transparentcolor', 'white')  # 设置白色为透明
            
            # 创建十字架
            canvas = tk.Canvas(cross_window, width=screen_width, height=screen_height, bg='white', highlightthickness=0)
            canvas.pack()
            
            # 实时更新十字架位置
            mouse_clicked = False
            
            def update_cross():
                if not mouse_clicked:
                    x, y = pyautogui.position()
                    canvas.delete('all')
                    # 水平线（扩展到全屏）
                    canvas.create_line(0, y, screen_width, y, width=2, fill='red')
                    # 垂直线（扩展到全屏）
                    canvas.create_line(x, 0, x, screen_height, width=2, fill='red')
                    # 中心点
                    canvas.create_oval(x-5, y-5, x+5, y+5, fill='red')
                    cross_window.after(10, update_cross)  # 每10毫秒更新一次
            
            # 启动更新
            update_cross()
            
            # 鼠标点击事件
            def on_cross_click(event):
                nonlocal mouse_clicked, target_position
                target_position = (event.x_root, event.y_root)
                mouse_clicked = True
                cross_window.destroy()
            
            # 绑定点击事件
            cross_window.bind('<Button-1>', on_cross_click)
            
            # 等待用户点击或取消
            while self.status and not mouse_clicked:
                if keyboard.is_pressed('esc'):
                    cross_window.destroy()
                    break
                # 禁用热键检查
                time.sleep(0.01)
            
            if mouse_clicked:
                self.click_position = f"({target_position[0]}, {target_position[1]})"
                self.position_label.config(text=self.click_position)
        
        # 检查是否获取到目标位置（如果需要）
        if position_mode == "通过点击确认点击位置" and target_position is None:
            self.status = False
            self.status_label.config(text="停止", foreground="red")
            return
        
        count = 0
        # 主循环
        while self.status:
            # 获取点击位置
            if position_mode == "实时获取鼠标位置":
                current_position = pyautogui.position()
                # 减少UI更新频率，提高速度
                if count % 10 == 0:  # 每10次更新一次UI
                    self.click_position = f"({current_position.x}, {current_position.y})"
                    self.position_label.config(text=self.click_position)
            else:
                current_position = target_position
            
            # 执行点击操作
            if click_type == "拖动":
                # 使用win32api进行拖动操作
                win32api.SetCursorPos(current_position)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(1)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            elif click_type == "点击":
                # 使用win32api进行点击操作，速度更快
                win32api.SetCursorPos(current_position)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            elif click_type == "双击":
                # 使用win32api进行双击操作，速度更快
                win32api.SetCursorPos(current_position)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            # 增加计数
            count += 1
            
            # 检查是否达到重复次数
            if repeat_times > 0 and count >= repeat_times:
                self.status = False
                self.status_label.config(text="停止", foreground="red")
                break
            
            # 等待间隔（毫秒转秒）
            if click_interval_ms > 0:
                time.sleep(click_interval_ms / 1000)
            else:
                # 即使无间隔，也添加微小延迟以避免CPU占用过高
                time.sleep(0.001)
        
        # 循环结束后更新状态
        if self.status:
            self.status = False
            self.status_label.config(text="停止", foreground="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()