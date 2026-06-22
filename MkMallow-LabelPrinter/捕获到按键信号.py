import pyautogui
import time

print("⏳ 15秒內，把滑鼠移到「打印」按鈕上...")
time.sleep(15)
# 獲取當前滑鼠位置
current_pos = pyautogui.position()
print(f"✅ 抓到了！你的座標是：X={current_pos.x}, Y={current_pos.y}")