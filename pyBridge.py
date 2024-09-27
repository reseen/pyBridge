import os
import datetime
import ctypes

import win32api
import win32gui
import win32con

# 常量定义
ID_TRAYICON = 1001
ID_SHOW_HIDE = 1002
ID_CLEAR = 1003
ID_EXIT = 1004
NIM_ADD = 0x00000000
NIM_DELETE = 0x00000002
NIM_MODIFY = 0x00000001
NIF_ICON = 0x00000002
NIF_MESSAGE = 0x00000001
NIF_TIP = 0x00000004


class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [('dwData', ctypes.c_ulonglong),
                ('cbData', ctypes.c_ulong),
                ('lpData', ctypes.c_void_p)]
    
class MainWindow:
    def __init__(self):
        self.hwnd = None
        self.icon = None
        self.edit_box_hwnd = None
        self.last_result = 0
        self.create_window()

    def create_window(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = 'pyBridge'
        wc.hInstance = win32api.GetModuleHandle(None)

        # 使用自定义图标
        icon_path = os.path.join(os.path.dirname(__file__), 'python.ico')
        wc.hIcon = win32gui.LoadImage(0, icon_path, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE)
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)  # 使用默认光标

        # 注册窗口类
        win32gui.RegisterClass(wc)

        # 创建窗口
        self.hwnd = win32gui.CreateWindow(
            wc.lpszClassName,
            'pyBridge',
            win32con.WS_OVERLAPPEDWINDOW,
            0, 0, 800, 480,
            0, 0, wc.hInstance, None
        )

        # 设置窗口图标
        win32api.SetClassLong(self.hwnd, win32con.GCL_HICON, wc.hIcon)

        # 使用自定义图标
        self.icon = win32gui.LoadImage(0, icon_path, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE)
        self.create_tray_icon()

        # 添加文本框
        self.create_edit_box()

        # 强制重绘窗口以显示文本框内容
        win32gui.InvalidateRect(self.hwnd, None, True)

    def create_edit_box(self):
        # 创建多行只读文本框，填满整个窗口
        self.edit_box_hwnd = win32gui.CreateWindowEx(
            0,
            'EDIT',
            '',  # 默认内容为空
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.ES_READONLY | win32con.ES_MULTILINE | win32con.WS_VSCROLL | win32con.WS_HSCROLL,
            0, 0, 800, 480,
            self.hwnd, None, win32api.GetModuleHandle(None), None
        )

    def create_tray_icon(self):
        nid = (self.hwnd, ID_TRAYICON, NIF_ICON | NIF_MESSAGE | NIF_TIP,
               win32con.WM_USER + 1, self.icon, 'pyBridge')
        win32gui.Shell_NotifyIcon(NIM_ADD, nid)

    def show_context_menu(self):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, ID_SHOW_HIDE, '显示/隐藏')
        win32gui.AppendMenu(menu, win32con.MF_STRING, ID_CLEAR, '清空')
        win32gui.AppendMenu(menu, win32con.MF_STRING, ID_EXIT, '退出')

        x, y = win32api.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu, win32con.TPM_BOTTOMALIGN | win32con.TPM_RIGHTALIGN, x, y, 0, self.hwnd, None)

    def append_text(self, text=''):
        if len(text) > 0:
            now = datetime.datetime.now().strftime('%H:%M:%S %f')[:-3]
            text = f'{now} {text}\r\n'
        else:
            text = '\r\n'
        # 先选择文本框末尾
        length = win32gui.SendMessage(self.edit_box_hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
        win32gui.SendMessage(self.edit_box_hwnd, win32con.EM_SETSEL, length, length)

        # 追加文本
        win32gui.SendMessage(self.edit_box_hwnd, win32con.EM_REPLACESEL, True, text)

        # 将光标移动到文本框末尾
        win32gui.SendMessage(self.edit_box_hwnd, win32con.EM_SETSEL, length + len(text), length + len(text))

    def wnd_proc(self, hwnd, msg, wparam, lparam):

        def show_window_center():
            # 计算居中位置
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            window_width = 800
            window_height = 480
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2

            win32gui.SetWindowPos(self.hwnd, None, x, y, window_width, window_height, win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.hwnd)

        def clear_window_edit():
            # 清空文本框内容
            win32gui.SendMessage(self.edit_box_hwnd, win32con.WM_SETTEXT, 0, '')

        if msg == win32con.WM_DESTROY:
            win32gui.Shell_NotifyIcon(NIM_DELETE, (self.hwnd, ID_TRAYICON))
            win32gui.PostQuitMessage(0)

        elif msg == win32con.WM_USER + 1:
            if lparam == win32con.WM_LBUTTONDBLCLK:
                show_window_center()

            elif lparam == win32con.WM_RBUTTONDOWN:
                self.show_context_menu()

        elif msg == win32con.WM_COMMAND:
            if wparam == ID_SHOW_HIDE:
                if win32gui.IsWindowVisible(self.hwnd):
                    win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)
                else:
                    show_window_center()

            elif wparam == ID_CLEAR:
                clear_window_edit

            elif wparam == ID_EXIT:
                win32gui.Shell_NotifyIcon(NIM_DELETE, (self.hwnd, ID_TRAYICON))
                win32gui.PostQuitMessage(0)

        elif msg == win32con.WM_PAINT or msg == win32con.WM_SIZE:
            if msg == win32con.WM_SIZE:
                # 获取新的客户区尺寸
                width = win32api.LOWORD(lparam)
                height = win32api.HIWORD(lparam)
                # 调整文本框大小
                win32gui.SetWindowPos(self.edit_box_hwnd, None, 0, 0, width, height, win32con.SWP_NOZORDER)

            win32gui.InvalidateRect(self.hwnd, None, True)

        if msg == win32con.WM_COPYDATA:
            cds = ctypes.cast(lparam, ctypes.POINTER(COPYDATASTRUCT)).contents
            try:
                msg_id  = cds.dwData
                msg_str = ctypes.string_at(cds.lpData, cds.cbData).decode('utf-8')

            except Exception as e:
                self.last_result = -9999
                self.append_text(f'recv msg error: {e}')

            try:
                self.append_text(f'recv msg: id = {msg_id}, str = {msg_str}')
                if msg_id != 0:
                    self.last_result = proc_copydata_message(msg_id, msg_str)
                    self.append_text(f'proc msg: res = {self.last_result}')
                else:
                    self.append_text(f'last msg: res = {self.last_result}')

            except Exception as e:
                self.last_result = -9998
                self.append_text(f'proc msg error: {e}')

            self.append_text('')
            return self.last_result

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


def proc_copydata_message(msg_id, msg_str):
    print(f'proc_copydata_message {msg_id=}, {msg_str=}')
    return msg_id


if __name__ == '__main__':
    MainWindow()
    win32gui.PumpMessages()
