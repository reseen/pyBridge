import time
import ctypes
from ctypes import wintypes


# 加载所需的系统库
user32 = ctypes.windll.user32
imm32 = ctypes.windll.imm32


# 定义 SendMessage 函数参数表
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = ctypes.c_long


# 输入法状态消息
WM_IME_CONTROL = 0x0283


def get_keyboard_layout_id(hwnd=None):
    '''
    获取键盘布局ID
    '''

    if hwnd is None:
        hwnd = user32.GetForegroundWindow()             # 获取当前活动窗口句柄
    
    tid = user32.GetWindowThreadProcessId(hwnd, None)   # 获取窗口线程ID        
    return user32.GetKeyboardLayout(tid) & 0xFFFF       # 获取键盘布局ID


def send_ime_control(hwnd=None, command=0, data=0):
    '''
    获取中英文输入法状态值
    '''

    if hwnd is None:
        hwnd = user32.GetForegroundWindow()             
    
    hIme = imm32.ImmGetDefaultIMEWnd(hwnd)              # 获取默认 IME 窗口句柄

    if hIme:
        return user32.SendMessageW(hIme, WM_IME_CONTROL, command, data)
    
    return None


def get_im_state():
    '''
    获取当前输入法状态 0:英文 1:中文
    '''

    keyboard_layout_id = get_keyboard_layout_id() & 0xFFFF

    print(f'keyboard_layout_id = {keyboard_layout_id:04X}')
    if keyboard_layout_id == 0x0409:                    # 美式键盘，，英文输入法状态
        return 0
    
    hwnd = user32.GetForegroundWindow()                 # 获取当前活动窗口句柄 
    ime_control_val = send_ime_control(hwnd, 5)
    print(f'ime_control_val(5) = {ime_control_val:04X}')
    if ime_control_val == 0:                            # 键盘已关闭，英文输入法状态
        return 0
    
    ime_control_val = send_ime_control(hwnd, 1)
    print(f'ime_control_val(1) = {ime_control_val:04X}')
    if ime_control_val == 0:                            # 英文输入法状态
        return 0

    return 1                                            # 中文输入法状态
    


if __name__ == "__main__":

    for i in range(100):

        im_state = get_im_state()
        print(f"当前输入状态为：{'中文' if im_state else '英文'}")

        time.sleep(0.5)
