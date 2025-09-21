import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

LRESULT = ctypes.c_longlong
HHOOK = wintypes.HANDLE

user32.SetWindowsHookExW.argtypes = [wintypes.INT, wintypes.LPVOID, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = HHOOK

user32.CallNextHookEx.argtypes = [HHOOK, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = LRESULT

user32.UnhookWindowsHookEx.argtypes = [HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL

user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND,
                                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                ctypes.c_uint]
user32.SetWindowPos.restype = wintypes.BOOL

user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = ctypes.c_long

user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
user32.SetWindowLongW.restype = ctypes.c_long

user32.SetLayeredWindowAttributes.argtypes = [wintypes.HWND, wintypes.COLORREF, wintypes.BYTE, wintypes.DWORD]
user32.SetLayeredWindowAttributes.restype = wintypes.BOOL

kernel32.GetCurrentThreadId.restype = wintypes.DWORD

MB_OK = 0x00000000
MB_OKCANCEL = 0x00000001
MB_YESNO = 0x00000004
MB_YESNOCANCEL = 0x00000003

MB_ICONERROR = 0x00000010
MB_ICONINFO = 0x00000040
MB_ICONWARNING = 0x00000030
MB_ICONQUESTION = 0x00000020

SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_NOMOVE = 0x0002
SWP_FRAMECHANGED = 0x0020

WH_CBT = 5
HCBT_ACTIVATE = 5

IDOK = 1
IDCANCEL = 2
IDYES = 6
IDNO = 7


def msgboxPLUS(
    title, text,
    icon="error", buttons="ok",
    x=None, y=None,
    opacity=1.0,
    topmost=False,
    disable_close=False,
    disable_minimize=False,
    disable_maximize=False
):
    """
    Show a native Windows MessageBox with advanced options.

    Parameters:
        title (str): Window title
        text (str): Message text
        icon (str): "error", "info", "warning", "question"
        buttons (str): "ok", "okcancel", "yesno", "yesnocancel"
        x (int): X coordinate (optional)
        y (int): Y coordinate (optional)
        opacity (float): 0.0 = fully transparent, 1.0 = fully opaque
        topmost (bool): Keep window always on top
        disable_close (bool): Remove the close button (X)
        disable_minimize (bool): Remove minimize button
        disable_maximize (bool): Remove maximize button

    Returns:
        str: "ok", "cancel", "yes", "no"
    """

    icons = {
        "error": MB_ICONERROR,
        "info": MB_ICONINFO,
        "warning": MB_ICONWARNING,
        "question": MB_ICONQUESTION
    }

    buttons_map = {
        "ok": MB_OK,
        "okcancel": MB_OKCANCEL,
        "yesno": MB_YESNO,
        "yesnocancel": MB_YESNOCANCEL
    }

    style = icons.get(icon, MB_ICONERROR) | buttons_map.get(buttons, MB_OK)

    def hook_proc(nCode, wParam, lParam):
        if nCode == HCBT_ACTIVATE:
            hWnd = wParam

            if x is not None and y is not None:
                user32.SetWindowPos(hWnd, None, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER)

            if topmost:
                HWND_TOPMOST = -1
                user32.SetWindowPos(hWnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)

            if opacity < 1.0:
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x00080000
                LWA_ALPHA = 0x00000002

                ex_style = user32.GetWindowLongW(hWnd, GWL_EXSTYLE)
                user32.SetWindowLongW(hWnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)
                user32.SetLayeredWindowAttributes(hWnd, 0, int(opacity * 255), LWA_ALPHA)

            if disable_close or disable_minimize or disable_maximize:
                GWL_STYLE = -16
                WS_SYSMENU = 0x00080000
                WS_MINIMIZEBOX = 0x00020000
                WS_MAXIMIZEBOX = 0x00010000

                style_val = user32.GetWindowLongW(hWnd, GWL_STYLE)
                if disable_close:
                    style_val &= ~WS_SYSMENU
                if disable_minimize:
                    style_val &= ~WS_MINIMIZEBOX
                if disable_maximize:
                    style_val &= ~WS_MAXIMIZEBOX

                user32.SetWindowLongW(hWnd, GWL_STYLE, style_val)
                user32.SetWindowPos(hWnd, None, 0, 0, 0, 0,
                                    SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER)

            user32.UnhookWindowsHookEx(hook_proc.hook)

        return user32.CallNextHookEx(hook_proc.hook, nCode, wParam, lParam)

    HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
    cb_func = HOOKPROC(hook_proc)

    hook_proc.hook = user32.SetWindowsHookExW(WH_CBT, cb_func, None, kernel32.GetCurrentThreadId())

    result = user32.MessageBoxW(0, text, title, style)

    mapping = {
        IDOK: "ok",
        IDCANCEL: "cancel",
        IDYES: "yes",
        IDNO: "no"
    }

    return mapping.get(result, str(result))


if __name__ == "__main__":
    answer = msgboxPLUS(
        "Custom MessageBox",
        "Do you want to continue?",
        icon="question",
        buttons="yesnocancel",
        x=600, y=100,
        opacity=0.8,
        topmost=True,
        disable_close=True,
        disable_minimize=True,
        disable_maximize=True
    )
    print("User answer:", answer)
