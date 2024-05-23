import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# 假设这些导入模块存在且有效
from badminton_booking import book_badminton
from pingpong_booking import book_pingpong
from gym_booking import book_gym
from utils import init_driver, login

# 时间表
time_table = {1: "8:00-9:00", 2: "9:00-10:00", 3: "10:00-11:00", 4: "11:00-12:00", 5: "12:00-13:00", 6: "13:00-14:00", 7: "14:00-15:00", 8: "15:00-16:00", 9: "16:00-17:00", 10: "17:00-18:00", 11: "18:00-19:00", 12: "19:00-20:00", 13: "20:00-21:00"}
def gui_app():
    # 主窗口初始化
    # 初始场馆选项
    gym_choices = {'松园体育馆': 1, '竹园体育馆': 2, '星湖体育馆': 3, '卓尔体育馆': 4, '风雨体育馆': 5}
    time_choices = time_table
    # 更新场馆选项的函数
    def update_gym_choices(event):
        nonlocal gym_choices, time_choices  # 使用nonlocal声明，以便可以修改外部函数的变量
        activity = activity_var.get()
        if activity == '羽毛球':
            gym_choices = {'松园体育馆': 1, '竹园体育馆': 2, '星湖体育馆': 3, '卓尔体育馆': 4, '风雨体育馆': 5}
            time_choices = time_table
        elif activity == '乒乓球':
            gym_choices = {'松园体育馆': 1, '竹园体育馆': 2, '风雨体育馆': 3, '杏林体育馆': 4}
            time_choices = time_table
        elif activity == '健身房':
            gym_choices = {'松园体育馆': 1, '宋卿体育馆': 2, '杏林体育馆': 3}
            time_choices = {1: "16:00-18:00", 2: "19:00-21:00"}
        else:
            gym_choices = {}
        gym_dropdown['values'] = list(gym_choices.keys())
        gym_dropdown.current(0)
        time_list.delete(0, tk.END)
        for time in time_choices.values():
            time_list.insert(tk.END, time)

    # 提交按钮的回调函数
    def on_submit():
        username = username_entry.get()
        password = password_entry.get()
        activity = activity_dropdown.get()
        activity_ch = activity_choices[activity_dropdown.get()]  # 项目序号
        gym = gym_choices[gym_dropdown.get()]
        fav_time = [int(time) + 1 for time in time_list.curselection()]
        accept = accept_var.get()

        if not username or not password or not fav_time:
            messagebox.showerror("错误", "请完整填写所有字段！")
            return
        driver = init_driver()
        if not login(driver, username, password, activity_ch):
            messagebox.showerror("错误", "登录失败！请检查账号密码是否正确")
            driver.quit()
            return
        booking_result = False
        if activity == '羽毛球':
            booking_result = book_badminton(driver, gym, fav_time, accept, activity_ch)
        elif activity == '乒乓球':
            booking_result = book_pingpong(driver, gym, fav_time, accept, activity_ch)
        elif activity == '健身房':
            booking_result = book_gym(driver, gym, fav_time, accept, activity_ch)

        if booking_result:
            messagebox.showinfo("成功", "预约成功！如有版本问题请自行维护或Email至argc_xiang@whu.edu.cn")
        else:
            messagebox.showerror("失败", "预约失败！如有版本问题请自行维护或Email至argc_xiang@whu.edu.cn")

        window.destroy()

    def show_custom_prompt():
        prompt_window = tk.Toplevel(window)
        prompt_window.title("提示信息")
        prompt_window.geometry("800x400")

        # 设置字体大小
        font_setting = ('Georgia', 12)

        tk.Label(prompt_window, text="请仔细阅读以下提示信息：", font=font_setting).pack(pady=10)
        tk.Label(prompt_window, text="1. 此脚本为作者测试使用，请勿用于盈利或其他非正规用途。\n"
                                     "2. 此脚本为半自动化脚本，在提交订单前需要用户在2s之内完成滑动验证码的检验，否则会预约失败。\n"
                                     "3. 如有任何问题，请Email至argc_xiang@whu.edu.cn。",
                 font=font_setting, justify=tk.LEFT).pack(pady=10)

        def on_continue():
            prompt_window.destroy()  # 关闭提示窗口，继续显示主窗口

        def on_exit():
            window.destroy()  # 关闭主窗口，退出程序

        tk.Button(prompt_window, text="继续", command=on_continue, font=font_setting).pack(side=tk.LEFT, padx=20,
                                                                                           pady=20)
        tk.Button(prompt_window, text="退出", command=on_exit, font=font_setting).pack(side=tk.RIGHT, padx=20, pady=20)

        # 使提示窗口始终在主窗口上方
        prompt_window.transient(window)
        prompt_window.grab_set()
        window.wait_window(prompt_window)

    def toggle_password():
        if password_entry.cget('show') == '':
            password_entry.config(show='*')
            toggle_btn.config(text='显示密码')
        else:
            password_entry.config(show='')
            toggle_btn.config(text='隐藏密码')

    def init_time_list():
        for time in time_table.values():
            time_list.insert(tk.END, time)

    window = tk.Tk()
    window.title("体育场馆预约系统")
    window.geometry("500x350")
    show_custom_prompt()
    # 字体设置
    font_setting = ('Georgia', 11)
    # UI组件
    tk.Label(window, text="账号", font=font_setting).grid(row=0, column=0)
    username_entry = tk.Entry(window, font=font_setting, width=25)
    username_entry.grid(row=0, column=1)

    tk.Label(window, text="密码", font=font_setting).grid(row=1, column=0)
    password_entry = tk.Entry(window, font=font_setting, show="*", width=25)
    password_entry.grid(row=1, column=1)
    # 添加“显示密码”按钮
    toggle_btn = tk.Button(window, text='显示密码', command=toggle_password, font=font_setting, width=10)
    toggle_btn.grid(row=1, column=2)

    tk.Label(window, text="运动", font=font_setting).grid(row=2, column=0)
    activity_var = tk.StringVar()
    activity_choices = {'羽毛球': 1, '乒乓球': 2, '健身房': 3}
    activity_dropdown = ttk.Combobox(window, textvariable=activity_var, values=list(activity_choices.keys()), font=font_setting, width=23)
    activity_dropdown.grid(row=2, column=1)
    activity_dropdown.bind('<<ComboboxSelected>>', update_gym_choices)

    tk.Label(window, text="场馆", font=font_setting).grid(row=3, column=0)
    gym_var = tk.StringVar()
    gym_dropdown = ttk.Combobox(window, textvariable=gym_var, values=list(gym_choices.keys()), font=font_setting, width=23)
    gym_dropdown.grid(row=3, column=1)

    tk.Label(window, text="时间", font=font_setting).grid(row=4, column=0)
    time_list = tk.Listbox(window, font=font_setting, selectmode=tk.MULTIPLE, exportselection=0, width=23, height=6)
    init_time_list()
    time_list.grid(row=4, column=1)

    tk.Label(window, text="是否接受不完全预约", font=font_setting).grid(row=5, column=0)
    accept_var = tk.IntVar()
    tk.Radiobutton(window, text="是", variable=accept_var, value=1, font=font_setting).grid(row=5, column=1)
    tk.Radiobutton(window, text="否", variable=accept_var, value=2, font=font_setting).grid(row=5, column=2)

    submit_btn = tk.Button(window, text="提交预约", command=on_submit, font=font_setting, width=10)
    submit_btn.grid(row=6, column=1)

    window.mainloop()

if __name__ == '__main__':
    gui_app()
