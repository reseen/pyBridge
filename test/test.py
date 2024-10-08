import win32gui
import win32api
import win32con
import ctypes


class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [('dwData', ctypes.c_ulonglong),
                ('cbData', ctypes.c_ulong),
                ('lpData', ctypes.c_void_p)]
    

def send_data_to_window(window_name, message):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        data = message.encode('utf-8')

        cds = COPYDATASTRUCT()
        cds.dwData = 100  # 自定义数据
        cds.cbData = len(data)

        # 创建缓冲区并将指针赋值给 lpData
        buffer = ctypes.create_string_buffer(data)
        cds.lpData = ctypes.cast(buffer, ctypes.c_void_p)  # 转换为 c_void_p

        print(f'{cds.lpData=:016X}')
        print(f'{cds.cbData=}')
        print(f'{cds.dwData=}')

        # 发送消息
        lparam_address = ctypes.cast(ctypes.byref(cds), ctypes.c_void_p).value
        result = win32api.SendMessage(hwnd, win32con.WM_COPYDATA, 0, lparam_address)
        print(f'Message sent, result: {result}')
    else:
        print(f"Window '{window_name}' not found.")



if __name__ == '__main__':
    send_data_to_window('pyBridge', 'get im state')