# 自動申請Windows管理員權限
import ctypes
import sys
import time
import pyautogui
import pygetwindow as gw
from datetime import datetime
from pynput import keyboard

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 非管理員自動重啟程序申請權限
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# ====================== 配置區 ======================
TARGET_WINDOW_TITLE = "MkMallow Pick & Mix"  # 軟體窗口標題
COOLDOWN_TIME = 3                              # 按鈕冷卻時間(秒)
KEY_REPEAT_INTERVAL = 0.3                      # 攔截手動連按空格
POPUP_CONFIRM_X, POPUP_CONFIRM_Y = 950, 567    # 彈窗打印按鈕固定座標
WAIT_WINDOW_ACTIVE = 1.0                       # 窗口激活等待時長
WAIT_POPUP_LOAD = 3                          # Ctrl+P後等待彈窗打開的時間
# ====================================================

last_trigger_time = 0
last_space_press = 0

def auto_print():
    global last_trigger_time
    current_time = time.time()

    # 冷卻防連點判斷
    if current_time - last_trigger_time < COOLDOWN_TIME:
        remain = round(COOLDOWN_TIME - (current_time - last_trigger_time), 1)
        print(f"⏳ 冷卻中，剩餘 {remain} 秒，暫不可重複觸發")
        return

    print("\n" + "="*25)
    print(f"🟢 {datetime.now().strftime('%H:%M:%S')} USB按鈕觸發打印流程")

    # 查找目標軟體窗口
    target_win = None
    for win in gw.getAllWindows():
        if win.title and TARGET_WINDOW_TITLE.lower() in win.title.lower():
            target_win = win
            break
    if not target_win:
        print("❌ 錯誤：未找到軟體窗口【MkMallow Pick & Mix】，請先打開程序！")
        return

    try:
        # 激活主窗口
        if target_win.isMinimized:
            target_win.restore()
        target_win.activate()
        time.sleep(WAIT_WINDOW_ACTIVE)

        # 步驟1：Ctrl+P快捷鍵喚起打印彈窗（取代點擊右上角按鈕）
        pyautogui.hotkey("ctrl", "p")
        print("🖨️ 已發送 Ctrl+P，正在喚起打印彈窗...")
        time.sleep(WAIT_POPUP_LOAD)


    except Exception as err:
        print(f"❌ 程序執行異常：{str(err)}")
        return

    last_trigger_time = current_time
    print("="*25 + "\n")

# 按鍵監聽：只響應USB按鈕空格，屏蔽手按鍵盤空格
def on_press(key):
    global last_space_press
    now = time.time()

    # ESC鍵一鍵退出程序
    if key == keyboard.Key.esc:
        print("\n🛑 程序即將停止運行")
        return False

    # 只監聽空格鍵
    if key != keyboard.Key.space:
        return

    # 短時間連續按空格 = 人手鍵盤操作，直接忽略
    if now - last_space_press < KEY_REPEAT_INTERVAL:
        last_space_press = now
        return

    last_space_press = now
    auto_print()

# 程序入口
if __name__ == "__main__":
    print("="*45)
    print("        Ctrl+P快捷鍵版 自動打印腳本 已啟動")
    print(f"📍 彈窗確認座標：X={POPUP_CONFIRM_X}  Y={POPUP_CONFIRM_Y}")
    print("💡 僅USB外接按鈕可觸發，手按鍵盤空格不會執行打印")
    print("🛑 按下鍵盤【ESC】可隨時關閉程序")
    print("="*45 + "\n")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # 保持後台運行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 手動終止程序，按鍵監聽已關閉")
        listener.stop()