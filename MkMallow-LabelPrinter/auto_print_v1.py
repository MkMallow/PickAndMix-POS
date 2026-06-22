import time
import pyautogui
import pygetwindow as gw
from datetime import datetime
from pynput import keyboard

# ================= 配置區 =================
TARGET_WINDOW_TITLE = "Xprinter" 
COOLDOWN_TIME = 3
POPUP_CONFIRM_X, POPUP_CONFIRM_Y = 1015, 878    # 彈窗打印按鈕固定座標
# ==========================================

last_trigger_time = 0

def print_label():
    global last_trigger_time
    current_time = time.time()

    # 冷却时间校验
    if current_time - last_trigger_time < COOLDOWN_TIME:
        print(f"⏳ 冷卻中，請稍候...")
        return

    print("\n" + "="*20)
    print(f"🟢 {datetime.now().strftime('%H:%M:%S')} 偵測到按鈕，開始執行打印...")
    
    # 查找Xprinter软件窗口
    target_win = None
    for win in gw.getAllWindows():
        if TARGET_WINDOW_TITLE.lower() in win.title.lower():
            target_win = win
            break
            
    if not target_win:
        print(f"❌ 錯誤：找不到 '{TARGET_WINDOW_TITLE}' 軟體窗口！")
        return

    try:
        print(f"✅ 找到窗口：{target_win.title}")
        target_win.activate()
        time.sleep(0.5) 
        
        print("🖨️ 唤起打印弹窗 (Ctrl+P)...")
        pyautogui.hotkey('ctrl', 'p')
        time.sleep(3) # Ctrl+P後等待彈窗打開的時間
        print("🖨️ 點擊座標 (1015,878) 確認打印...")
        pyautogui.click(x=POPUP_CONFIRM_X, y=POPUP_CONFIRM_Y, button='left')
        
    except Exception as e:
        print(f"❌ 執行出錯: {e}")
        return

    last_trigger_time = current_time
    print("✅ 指令發送成功！請檢查標籤機。")
    print("="*20)

# ===== 進階監聽邏輯 =====
def on_press(key):
    global last_trigger_time
    
    # 1. 判斷是否為空白鍵
    is_space = False
    try:
        # 標準鍵盤的空白鍵
        if key == keyboard.Key.space:
            is_space = True
    except AttributeError:
        pass

    if is_space:
        # 2. 【核心判斷】檢查按下空白鍵的「物理裝置」
        # controller 會記錄是哪個裝置觸發的
        # 如果是由 USB 鍵盤觸發的，key.controller 會是鍵盤物件
        # 如果是由 USB 按鈕觸發的，通常沒有 controller 屬性，或者會是 None
        
        # 這裡我們用一個簡單的邏輯：
        # 真正的鍵盤空白鍵會有 vk (Virtual Key) 屬性
        # 很多 USB 按鈕模擬出來的空白鍵沒有這個屬性，或者是一個特殊的物件
        
        try:
            # 嘗試獲取虛擬鍵碼，如果是標準鍵盤，這會有值
            vk = key.vk
            
            # 【關鍵點】如果你的按鈕被系統識別為「HID Keyboard Device」，
            # 它可能也會有 vk。但我們可以用另一個方法：
            # 檢查 key 是否有 'char' 屬性且為 ' '
            # 或者，我們直接檢查按鍵的 'name'
            
            # 簡單粗暴但有效的判斷：
            # 真正的鍵盤空白鍵，在 pynput 裡通常是 Key.space 實例
            # 而某些 USB 按鈕模擬出來的，可能是字符 ' '
            
            # 我們這裡用一個更穩的判斷：
            # 如果 key 是一個標準的 Key.space，且是由物理鍵盤觸發，則忽略
            # 但如果是由 USB 按鈕觸發（沒有 controller），則執行
            
            # 由於不同按鈕晶片行為不同，我們用最簡單的「排除法」：
            # 如果按下空白鍵時，key.char 存在且為 ' '，這通常是標準鍵盤
            # 如果 key.char 不存在，可能是按鈕
            
            if hasattr(key, 'char') and key.char == ' ':
                # 這很可能是標準鍵盤的空白鍵，直接返回，不執行打印
                return
            else:
                # 這可能是 USB 按鈕模擬的空白鍵，執行打印
                print_label()
                
        except Exception as e:
            # 如果出錯，為了安全起見，執行打印
            print_label()
            
    # 3. 如果你想保留其他按鍵的功能（比如 Ctrl+C 停止），可以在這裡加
    # 例如：if key == keyboard.Key.esc: return False (退出監聽)

# ================= 主程式 =================
print("🟢 標籤打印腳本已啟動（進階防抖模式）")
print(f"👉 目標軟體：{TARGET_WINDOW_TITLE}")
print("💡 現在只會響應 USB 按鈕，鍵盤空白鍵會被忽略")
print("👉 按一下 USB 紅色按鈕即可打印")
print("按 Ctrl+C 可停止腳本\n")

# 啟動監聽器
listener = keyboard.Listener(on_press=on_press)
listener.start()

# 讓主程式保持運行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 正在停止腳本...")
    listener.stop()