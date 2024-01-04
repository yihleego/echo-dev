import time
from ctypes import Structure, windll, sizeof, byref
from ctypes.wintypes import HWND, DWORD, UINT, POINT, RECT

SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_NORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3
SW_MAXIMIZE = 3
SW_SHOWNOACTIVATE = 4
SW_SHOW = 5
SW_MINIMIZE = 6
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_RESTORE = 9
SW_SHOWDEFAULT = 10
SW_FORCEMINIMIZE = 11

DELETE = 0x00010000
READ_CONTROL = 0x00020000
SYNCHRONIZE = 0x00100000
WRITE_DAC = 0x00040000
WRITE_OWNER = 0x00080000

STANDARD_RIGHTS_REQUIRED = 983040
STANDARD_RIGHTS_READ = READ_CONTROL
STANDARD_RIGHTS_WRITE = READ_CONTROL
STANDARD_RIGHTS_EXECUTE = READ_CONTROL
STANDARD_RIGHTS_ALL = 2031616
SPECIFIC_RIGHTS_ALL = 65535
ACCESS_SYSTEM_SECURITY = 16777216
MAXIMUM_ALLOWED = 33554432
GENERIC_READ = -2147483648
GENERIC_WRITE = 1073741824
GENERIC_EXECUTE = 536870912
GENERIC_ALL = 268435456

PROCESS_TERMINATE = 0x0001
PROCESS_CREATE_THREAD = 0x0002
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_DUP_HANDLE = 0x0040
PROCESS_CREATE_PROCESS = 0x0080
PROCESS_SET_QUOTA = 0x0100
PROCESS_SET_INFORMATION = 0x0200
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_SUSPEND_RESUME = 0x0800
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_SET_LIMITED_INFORMATION = 0x2000
PROCESS_ALL_ACCESS = STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFFF


class WINDOWPLACEMENT(Structure):
    _fields_ = [
        ('length', UINT),
        ('flags', UINT),
        ('showCmd', UINT),
        ('ptMinPosition', POINT),
        ('ptMaxPosition', POINT),
        ('rcNormalPosition', RECT),
    ]


def find_window(class_name: str = None, window_name: str = None) -> HWND:
    return windll.user32.FindWindowW(class_name, window_name)


def find_window_ex(parent: int = None, child_after: int = None, class_name: str = None, window_name: str = None) -> HWND:
    return windll.user32.FindWindowExW(parent, child_after, class_name, window_name)


def set_foreground(handle: int, process_id: int = None) -> bool:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow
    res = windll.user32.SetForegroundWindow(handle)
    if process_id:
        wait_thread_idle(process_id, handle)
    return bool(res)


def get_window_rect(handle: int) -> RECT:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowrect
    rect = RECT()
    windll.user32.GetWindowRect(handle, byref(rect))
    return rect


def move_window(handle: int, process_id: int = None, x: int = None, y: int = None, width: int = None, height: int = None, repaint=True):
    if x is None or y is None or width is None or height is None:
        rect = get_window_rect(handle)
        if x is None:
            x = rect[0]
        if y is None:
            y = rect[1]
        if width is None:
            width = rect[2] - rect[0]
        if height is None:
            height = rect[3] - rect[1]
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-movewindow
    res = windll.user32.MoveWindow(handle, x, y, width, height, repaint)
    if process_id:
        wait_thread_idle(process_id, handle)
    time.sleep(0)
    if not res:
        return False
    else:
        return True


def show_window(handle: int, cmd: int) -> bool:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow
    res = windll.user32.ShowWindow(handle, cmd)
    return bool(res)


def get_window_placement(handle: int) -> WINDOWPLACEMENT:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowplacement
    wp = WINDOWPLACEMENT()
    wp.length = sizeof(wp)
    windll.user32.GetWindowPlacement(handle, byref(wp))
    return wp


def get_process_id_from_handle(handle: int) -> int:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowthreadprocessid
    process_id = DWORD(0)
    handle = HWND(handle) if isinstance(handle, int) else handle
    windll.user32.GetWindowThreadProcessId(handle, byref(process_id))
    return process_id.value


def get_process_name_by_process_id(process_id):
    import psutil
    try:
        process = psutil.Process(process_id)
        return process.name()
    except psutil.NoSuchProcess as e:
        return f"Process with PID {process_id} not found"
    except psutil.AccessDenied as e:
        return f"Access denied to process with PID {process_id}"


def wait_thread_idle(process_id: int, handle: int):
    # https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess
    process = windll.kernel32.OpenProcess(0x0400, 0, process_id)
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-ishungappwindow
    if windll.user32.IsHungAppWindow(handle):
        raise RuntimeError(f'Window (hwnd={handle}) is not responding!')
    # https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle
    windll.kernel32.CloseHandle(process)


def screenshot(handle: int, filename: str) -> str:
    # https://stackoverflow.com/questions/19695214/screenshot-of-inactive-window-printwindow-win32gui
    import win32gui
    import win32ui
    from PIL import Image

    rect = win32gui.GetWindowRect(handle)
    w, h = rect[2] - rect[0], rect[3] - rect[1]

    window_dc = win32gui.GetWindowDC(handle)
    created_dc = win32ui.CreateDCFromHandle(window_dc)
    compatible_dc = created_dc.CreateCompatibleDC()

    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(created_dc, w, h)

    compatible_dc.SelectObject(bitmap)

    res = windll.user32.PrintWindow(handle, compatible_dc.GetSafeHdc(), 2)
    if not res:
        raise Exception()

    bitmap_info = bitmap.GetInfo()
    buffer = bitmap.GetBitmapBits(True)

    image = Image.frombuffer('RGB', (bitmap_info['bmWidth'], bitmap_info['bmHeight']), buffer, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(bitmap.GetHandle())
    compatible_dc.DeleteDC()
    created_dc.DeleteDC()
    win32gui.ReleaseDC(handle, window_dc)

    image.save(filename)
    return filename
