import ctypes
from ctypes import wintypes


user32 = ctypes.WinDLL('user32')
imm32 = ctypes.WinDLL('imm32')
kernel32 = ctypes.WinDLL('kernel32')

# 调用GetUserDefaultLangID函数
def get_user_default_lang_id():
    lang_id = kernel32.GetUserDefaultLangID()
    return lang_id

def get_keyboard_layout_name():
    # 定义一个长度为10的字节缓冲区
    buffer = ctypes.create_string_buffer(10)

    # 获取键盘布局名称
    result = user32.GetKeyboardLayoutNameA(buffer)

    if result:
        # 打印缓冲区内容
        print(f"Keyboard Layout Name: {buffer.value.decode('utf-8')}")
    else:
        print("Failed to get keyboard layout name.")


def activate_keyboard_layout(layout_id):
    # 激活指定的键盘布局
    result = user32.ActivateKeyboardLayout(layout_id, 0)
    return result

def load_keyboard_layout(layout_id):
    # 加载指定的键盘布局
    result = user32.LoadKeyboardLayoutW(layout_id, 0)

    return result

# get_keyboard_layout_name()

exit()

# 定义 LAYOUTORTIPPROFILE 结构体
class LAYOUTORTIPPROFILE(ctypes.Structure):
    _fields_ = [
        ("dwProfileType", wintypes.DWORD),        # InputProcessor or HKL
        ("langid", wintypes.LANGID),              # language id
        ("clsid", ctypes.c_byte * 16),            # CLSID of tip
        ("guidProfile", ctypes.c_byte * 16),      # profile description
        ("catid", ctypes.c_byte * 16),            # category of tip
        ("dwSubstituteLayout", wintypes.DWORD),   # substitute hkl
        ("dwFlags", wintypes.DWORD),               # Flags
        ("szId", wintypes.WCHAR * 260)            # KLID or TIP profile string
    ]

# 加载 input.dll
input_dll = ctypes.WinDLL('input.dll')

# 准备参数
pszUserReg = None  # 用户注册表路径，可以为 None
pszSystemReg = None  # 系统注册表路径，可以为 None
pszSoftwareReg = None  # 软件注册表路径，可以为 None

# 创建 LAYOUTORTIPPROFILE 实例
layout_or_tip_profile = LAYOUTORTIPPROFILE()
buffer_length = ctypes.sizeof(layout_or_tip_profile)

# 调用 EnumEnabledLayoutOrTip
result = input_dll.EnumEnabledLayoutOrTip(
    pszUserReg,
    pszSystemReg,
    pszSoftwareReg,
    ctypes.c_void_p(), 
    0
)

print(result)

print(f'{pszUserReg=}')
print(f'{pszSystemReg=}')
print(f'{pszSoftwareReg=}')


buffer_size = ctypes.sizeof(LAYOUTORTIPPROFILE) * result
layout_or_tip_profiles = (LAYOUTORTIPPROFILE * result)()

# 调用 EnumEnabledLayoutOrTip，第四个参数为缓冲区的指针，第五个参数为缓冲区大小
result = input_dll.EnumEnabledLayoutOrTip(
    pszUserReg,
    pszSystemReg,
    pszSoftwareReg,
    ctypes.byref(layout_or_tip_profiles),  # 缓冲区的指针
    buffer_size
)


# 检查返回值
if result:
    print("Enumeration succeeded.")
    for i in range(result):
        profile = layout_or_tip_profiles[i]
        print(f"Profile {i}:")
        print(f"  Profile Type: {profile.dwProfileType}")
        print(f"  Language ID: {profile.langid}")
        # print(f"  CLS ID: {profile.clsid}")

        # clsid_hex = ''.join(f'{b:02x}' for b in profile.clsid)
        # print(f"  CLSID: {clsid_hex}")

        # guidProfile_hex = ''.join(f'{b:02x}' for b in profile.guidProfile)
        # print(f"  Guid Profile: {guidProfile_hex}")

        # catid_hex = ''.join(f'{b:02x}' for b in profile.catid)
        # print(f"  CATID: {catid_hex}")

        print(f"  Substitute Layout: {profile.dwSubstituteLayout}")
        print(f"  Flags: {profile.dwFlags}")

        # szid_hex = ''.join(f'{b:02x}' for b in profile.szId)
        print(f"  szId: {profile.szId}")


        # valid_id = ''.join(chr(c) for c in profile.szId if c != 0)
        # print(f"  Profile ID: {valid_id}")
else:
    print("Enumeration failed.")


lang_id = get_user_default_lang_id()
print(f"User Default Language ID: {lang_id:#06x}")



# # 检查返回值
# if result:
#     print("Enumeration succeeded.")
#     print(f"Profile Type: {layout_or_tip_profile.dwProfileType}")
#     print(f"Language ID: {layout_or_tip_profile.langid}")
    
#     # 输出有效的字符串，直到第一个 NULL 字符
#     profile_id = layout_or_tip_profile.szId[:]
#     valid_id = ''.join(chr(c) for c in profile_id if c != 0)
#     print(f"Profile ID: {valid_id}")
# else:
#     print("Enumeration failed.")
