import os
import sys
import threading
import time
import random
import keyboard
import pyautogui
import cv2
import numpy as np
import winsound

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

from PyQt5.QtCore import Qt, QRectF, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFrame,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
)

# ============= ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ =============
bot_overlay = None

# ============= БОТ ШВЕЙКИ =============
sewing_running = False
sewing_active = False
sewing_templates = {}
sewing_timer_seconds = 0
sewing_timer_active = False


def load_sewing_templates():
    global sewing_templates
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    sewing_templates = {}

    for i in range(1, 21):
        img_path = os.path.join(icons_dir, f"{i}.png")
        if not os.path.exists(img_path):
            img_path = os.path.join(icons_dir, f"{i}.jpg")

        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                sewing_templates[i] = img
                print(f"✓ Загружен шаблон {i}")
            else:
                return False
        else:
            print(f"❌ Файл {i}.png/jpg не найден")
            return False

    print(f"✅ Загружено {len(sewing_templates)} шаблонов")
    return True


def find_number_fast(number):
    template = sewing_templates.get(number)
    if template is None:
        return None

    search_x, search_y = 750, 311
    search_w, search_h = 1144 - 750, 798 - 311

    try:
        screenshot = pyautogui.screenshot(region=(search_x, search_y, search_w, search_h))
        screen_np = np.array(screenshot)
        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= 0.7:
            h, w = template.shape
            cx = search_x + max_loc[0] + w // 2 + 7
            cy = search_y + max_loc[1] + h // 2 + 8
            return (cx, cy)
        return None
    except Exception:
        return None


def check_red_dot_fast(x, y):
    try:
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                pixel = pyautogui.pixel(x + dx, y + dy)
                if pixel[0] > 200 and pixel[1] < 100 and pixel[2] < 100:
                    return True
        return False
    except Exception:
        return False


def play_sound():
    """
    Проигрывает sound.mp3 из папки icons или iconc.
    Используется Windows MCI, чтобы mp3 играл без доп. библиотек.
    """
    base_dir = os.path.dirname(__file__)
    possible_paths = [
        os.path.join(base_dir, "icons", "sound.mp3"),
        os.path.join(base_dir, "iconc", "sound.mp3"),
        os.path.join(base_dir, "icons", "sound.wav"),
        os.path.join(base_dir, "iconc", "sound.wav"),
    ]

    sound_path = None
    for path in possible_paths:
        if os.path.exists(path):
            sound_path = path
            break

    if not sound_path:
        print("❌ sound.mp3 не найден в icons или iconc")
        return

    try:
        # WAV через winsound
        if sound_path.lower().endswith(".wav"):
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return

        # MP3 через Windows MCI
        import ctypes
        alias = "keyrusher_sound"
        ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
        ctypes.windll.winmm.mciSendStringW(f'open "{sound_path}" type mpegvideo alias {alias}', None, 0, None)
        ctypes.windll.winmm.mciSendStringW(f'play {alias} from 0', None, 0, None)
    except Exception as e:
        print(f"❌ Не удалось проиграть звук: {e}")


def update_overlay_status(status, color):
    global bot_overlay
    if bot_overlay:
        bot_overlay.update_status(status, color)


def update_overlay_stats(text):
    global bot_overlay
    if bot_overlay:
        bot_overlay.update_stats(text)


def sewing_timer_loop():
    global sewing_timer_seconds, sewing_timer_active, sewing_active, sewing_running

    sewing_timer_seconds = 0
    sewing_timer_active = True

    while sewing_timer_active and sewing_running:
        time.sleep(1)
        sewing_timer_seconds += 1

        mins = sewing_timer_seconds // 60
        secs = sewing_timer_seconds % 60
        update_overlay_stats(f"таймер: {mins:02d}:{secs:02d}")

        if sewing_timer_seconds >= 85:
            # 01:25 — сразу сдавать работу
            update_overlay_status("сдавайте работу!", "#ffaa00")
            update_overlay_stats("01:25 | сдавай сейчас")
            play_sound()

            sewing_timer_seconds = 0
            sewing_active = False

            # ждём новую сессию через E
            while sewing_running and not sewing_active:
                if keyboard.is_pressed('e'):
                    sewing_active = True
                    update_overlay_status("работаю", "#16ec55")
                    update_overlay_stats("таймер: 00:00")
                    print("✅ Новая сессия!")
                    time.sleep(0.5)
                    break
                time.sleep(0.05)

    sewing_timer_active = False


def sewing_bot_loop():
    global sewing_running, sewing_active, sewing_timer_active

    if not sewing_running:
        return

    print("\n" + "=" * 50)
    print("🎮 ШВЕЙКА БОТ")
    print("=" * 50)

    if not sewing_templates:
        if not load_sewing_templates():
            sewing_running = False
            return

    while sewing_running:
        update_overlay_status("жду e", "#ff6666")
        update_overlay_stats("нажми e для старта")

        sewing_active = False
        while sewing_running and not sewing_active:
            if keyboard.is_pressed('e'):
                sewing_active = True
                print("✅ Старт!")
                time.sleep(0.3)
                break
            time.sleep(0.05)

        if not sewing_running:
            break

        update_overlay_status("работаю", "#16ec55")

        timer_thread = threading.Thread(target=sewing_timer_loop, daemon=True)
        timer_thread.start()

        positions = {}
        for number in range(1, 21):
            if not sewing_running or not sewing_active:
                break
            pos = find_number_fast(number)
            positions[number] = pos

        for number in range(1, 21):
            if not sewing_running or not sewing_active:
                break

            pos = positions.get(number)
            if pos is None:
                continue

            x, y = pos
            for _ in range(15):
                if not sewing_running or not sewing_active:
                    break
                pyautogui.moveTo(x, y, duration=0)
                pyautogui.click()
                if check_red_dot_fast(x, y):
                    break
                time.sleep(0.05)

        while sewing_running and sewing_active:
            time.sleep(0.1)


def start_sewing_bot():
    global sewing_running, sewing_active, sewing_timer_active
    if sewing_running:
        return
    if not sewing_templates:
        load_sewing_templates()
    sewing_running = True
    sewing_active = False
    sewing_timer_active = False
    threading.Thread(target=sewing_bot_loop, daemon=True).start()
    print("🎮 Швейка запущена")


def stop_sewing_bot():
    global sewing_running, sewing_active, sewing_timer_active
    sewing_running = False
    sewing_active = False
    sewing_timer_active = False
    print("🎮 Швейка остановлена")


# ============= БОТ ТОКАРЯ =============
lathe_running = False
lathe_template = None
lathe_timer_seconds = 0


def load_lathe_template():
    """
    Таргет токаря берётся из папки icons:
    palka.jpg / palka.png / stvol.jpg / stvol.png
    """
    global lathe_template
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    for name in ["palka.jpg", "palka.png", "stvol.jpg", "stvol.png"]:
        path = os.path.join(icons_dir, name)
        if os.path.exists(path):
            lathe_template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if lathe_template is not None:
                print(f"✅ Загружен таргет токаря: {name}")
                return True

    print("❌ Не найден таргет токаря: icons/palka.jpg или icons/palka.png")
    return False


def find_palka_fast():
    """
    Аналог AHK:
    ImageSearch, x, y, 659, 700, 1251, 900, *90 palka.jpg
    Потом мышь двигается в x+22, y+62.
    """
    if lathe_template is None:
        return None

    search_x, search_y = 659, 700
    search_w, search_h = 1251 - 659, 900 - 700

    try:
        screenshot = pyautogui.screenshot(region=(search_x, search_y, search_w, search_h))
        screen_np = np.array(screenshot)
        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(screen_gray, lathe_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # *90 в AHK примерно жёстче, но для OpenCV 0.65-0.75 обычно норм.
        if max_val >= 0.65:
            x = search_x + max_loc[0] + 22
            y = search_y + max_loc[1] + 62
            return (x, y)

        return None
    except Exception:
        return None


def lathe_color_exists():
    """
    Аналог AHK:
    PixelSearch, OutputX, OutputY, 1230, 713, 1257, 915, 0xC28251, 30, Fast RGB

    В AHK цикл заканчивался, когда ErrorLevel = 1,
    то есть когда цвет 0xC28251 НЕ найден.
    """
    target = (0xC2, 0x82, 0x51)  # RGB: 194,130,81
    tolerance = 30

    try:
        screenshot = pyautogui.screenshot(region=(1230, 713, 1257 - 1230, 915 - 713))
        img = np.array(screenshot)

        r = img[:, :, 0].astype(np.int16)
        g = img[:, :, 1].astype(np.int16)
        b = img[:, :, 2].astype(np.int16)

        mask = (
            (np.abs(r - target[0]) <= tolerance) &
            (np.abs(g - target[1]) <= tolerance) &
            (np.abs(b - target[2]) <= tolerance)
        )

        return bool(np.any(mask))
    except Exception:
        return True


def lathe_timer_loop():
    """
    Для токаря: на 00:50 сразу показываем 'можно сдавать' и проигрываем sound.mp3.
    """
    global lathe_running, lathe_timer_seconds

    lathe_timer_seconds = 0

    while lathe_running:
        time.sleep(1)
        lathe_timer_seconds += 1

        update_overlay_stats(f"таймер: {lathe_timer_seconds:02d} сек")

        if lathe_timer_seconds >= 50:
            update_overlay_status("можно сдавать", "#ffaa00")
            update_overlay_stats("00:50 | сдавай сейчас")
            play_sound()
            return


def lathe_bot_loop():
    global lathe_running, lathe_timer_seconds

    if not lathe_running:
        return

    print("\n" + "=" * 50)
    print("🔧 ТОКАРЬ БОТ")
    print("=" * 50)

    if lathe_template is None:
        if not load_lathe_template():
            lathe_running = False
            return

    update_overlay_status("запуск", "#ffaa00")
    update_overlay_stats("жму E...")

    # Аналог F3 в AHK: Send {e}
    keyboard.press_and_release("e")
    time.sleep(0.5)

    update_overlay_status("работаю", "#16ec55")
    threading.Thread(target=lathe_timer_loop, daemon=True).start()

    while lathe_running:
        # Если цвет 0xC28251 пропал — работа завершена.
        if not lathe_color_exists():
            update_overlay_status("готово", "#00ff00")
            update_overlay_stats("цвет пропал | новая точка")
            print("✅ Токарь: работа завершена")
            break

        palka = find_palka_fast()
        if palka:
            x, y = palka
            pyautogui.moveTo(x, y, duration=0)

        time.sleep(0.01)

    lathe_running = False


def start_lathe_bot():
    global lathe_running
    if lathe_running:
        return
    lathe_running = True
    threading.Thread(target=lathe_bot_loop, daemon=True).start()
    print("🔧 Токарь запущен")


def stop_lathe_bot():
    global lathe_running
    lathe_running = False
    print("🔧 Токарь остановлен")


# ============= ОСТАЛЬНЫЕ БОТЫ =============
smoothie_running = False
smoothie_count = 0
max_smoothies = 48
earned_money = 0


def make_smoothie_loop():
    global smoothie_running, smoothie_count, earned_money
    clicks = [(1080, 289, "right"), (1166, 287, "right"), (815, 582, "right"), (816, 672, "left")]

    while smoothie_running and smoothie_count < max_smoothies:
        for x, y, btn in clicks:
            if not smoothie_running:
                return
            pyautogui.moveTo(x + random.randint(-4, 4), y + random.randint(-4, 4), duration=0.05)
            if btn == "left":
                pyautogui.click()
            else:
                pyautogui.rightClick()
            time.sleep(0.1)

        smoothie_count += 1
        earned_money += 50
        update_overlay_stats(f"{smoothie_count}/{max_smoothies} | {earned_money}$")
        time.sleep(5)


def start_smoothie_bot():
    global smoothie_running, smoothie_count, earned_money
    if smoothie_running:
        return
    smoothie_count = 0
    earned_money = 0
    smoothie_running = True
    threading.Thread(target=make_smoothie_loop, daemon=True).start()
    print("🍹 Смузи бот запущен")


def stop_smoothie_bot():
    global smoothie_running
    smoothie_running = False
    print("🍹 Смузи бот остановлен")


port_running = False
box_count = 0


def port_bot_loop():
    global port_running, box_count
    keyboard.press('w')
    keyboard.press('shift')

    while port_running:
        try:
            found = False
            for x in range(966, 969):
                for y in range(487, 490):
                    pixel = pyautogui.pixel(x, y)
                    if (
                        abs(pixel[0] - 126) <= 30 and
                        abs(pixel[1] - 211) <= 30 and
                        abs(pixel[2] - 33) <= 30
                    ):
                        found = True
                        break
                if found:
                    break

            if found:
                keyboard.press_and_release('e')
                box_count += 1
                print(f"📦 Ящик #{box_count}")
                update_overlay_stats(f"ящиков: {box_count}")
                time.sleep(0.5)
        except Exception:
            pass
        time.sleep(0.1)

    keyboard.release('w')
    keyboard.release('shift')


def start_port_bot():
    global port_running
    if port_running:
        return
    port_running = True
    threading.Thread(target=port_bot_loop, daemon=True).start()
    print("📦 Порт бот запущен")


def stop_port_bot():
    global port_running
    port_running = False


afk_running = False


def afk_bot_loop():
    global afk_running
    keyboard.press('a')
    time.sleep(0.05)
    keyboard.press('d')
    while afk_running:
        time.sleep(0.5)
    keyboard.release('a')
    keyboard.release('d')


def start_afk_bot():
    global afk_running
    if afk_running:
        return
    afk_running = True
    threading.Thread(target=afk_bot_loop, daemon=True).start()
    print("💤 Анти-АФК бот запущен")


def stop_afk_bot():
    global afk_running
    afk_running = False
    print("💤 Анти-АФК бот остановлен")


wheel_running = False
wheel_count = 0


def wheel_bot_loop():
    global wheel_running, wheel_count
    clicks = [(1287, 273), (551, 329), (766, 655), (947, 894), (60, 59)]

    while wheel_running:
        try:
            keyboard.press_and_release('f10')
            time.sleep(1)
            for x, y in clicks:
                if not wheel_running:
                    break
                pyautogui.moveTo(x, y, duration=0.1)
                pyautogui.click()
                time.sleep(0.3)
            wheel_count += 1
            print(f"🎰 Колесо #{wheel_count}")
            update_overlay_stats(f"прокруток: {wheel_count}")
            time.sleep(3)
        except Exception:
            time.sleep(1)


def start_wheel_bot():
    global wheel_running, wheel_count
    if wheel_running:
        return
    wheel_count = 0
    wheel_running = True
    threading.Thread(target=wheel_bot_loop, daemon=True).start()
    print("🎰 Колесо бот запущен")


def stop_wheel_bot():
    global wheel_running
    wheel_running = False
    print("🎰 Колесо бот остановлен")


# ============= РАБОЧИЙ ОВЕРЛЕЙ =============
class SimpleOverlay(QWidget):
    status_signal = pyqtSignal(str, str)
    stats_signal = pyqtSignal(str)

    def __init__(self, bot_name):
        super().__init__()

        self.status_signal.connect(self._apply_status)
        self.stats_signal.connect(self._apply_stats)

        self.dragging = False
        self.drag_pos = QPoint()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(245, 92)
        self.move(50, 50)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 20, 30, 225);
                border: 2px solid #16ec55;
                border-radius: 14px;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(5)

        self.name_label = QLabel(f"🤖 {bot_name}")
        self.name_label.setStyleSheet(
            "color: #16ec55; font-size: 12px; font-weight: bold; background: transparent; border: none;"
        )

        self.status_label = QLabel("ЖДУ E")
        self.status_label.setStyleSheet(
            "color: #ff6666; font-size: 15px; font-weight: bold; background: transparent; border: none;"
        )

        self.stats_label = QLabel("Нажми E для старта")
        self.stats_label.setStyleSheet(
            "color: #aaaaaa; font-size: 11px; background: transparent; border: none;"
        )

        layout.addWidget(self.name_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.stats_label)

        root.addWidget(panel)

        self.show()
        self.raise_()

        print(f"✅ Оверлей создан для {bot_name}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        event.accept()

    def update_status(self, text, color):
        self.status_signal.emit(text, color)

    def update_stats(self, text):
        self.stats_signal.emit(text)

    def _apply_status(self, text, color):
        self.status_label.setText(text.upper())
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 15px; font-weight: bold; background: transparent; border: none;"
        )

    def _apply_stats(self, text):
        self.stats_label.setText(text)


# ============= GUI =============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")
os.makedirs(ICONS_DIR, exist_ok=True)


def get_icon_path(filename: str) -> str:
    return os.path.join(ICONS_DIR, filename)


def make_rounded_pixmap(source_path: str, width: int, height: int, radius: int) -> QPixmap:
    result = QPixmap(width, height)
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)

    if not os.path.exists(source_path):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#242941"))
        painter.drawRoundedRect(0, 0, width, height, radius, radius)
        painter.setPen(QColor("#8e97bb"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.drawText(result.rect(), Qt.AlignCenter, "NO\nIMG")
        painter.end()
        return result

    original = QPixmap(source_path)
    if original.isNull():
        painter.end()
        return result

    scaled = original.scaled(width, height, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x = max(0, (scaled.width() - width) // 2)
    y = max(0, (scaled.height() - height) // 2)
    cropped = scaled.copy(x, y, width, height)

    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, width, height), radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, cropped)
    painter.end()
    return result


MODULES = [
    ("Реконнект", "reconnect.png"),
    ("Анти-Афк", "anti_afk.png"),
    ("Шахта", "career.png"),
    ("Стройка", "build.png"),
    ("Швейка", "demorgan.png"),
    ("Токарка", "lathe.png"),
    ("Порт", "port.png"),
    ("EMS", "ems.png"),
    ("Ферма", "farmer.png"),
    ("Смузи", "smoothie.png"),
    ("Рагу", "stew.png"),
    ("Салат", "salad.png"),
    ("Такси", "taxi.png"),
    ("Еспандер", "expander.png"),
    ("Качалка", "gym.png"),
    ("Helper", "helper.png"),
    ("Рулетка", "wheel.png"),
]


class CustomTitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(52)
        self.setStyleSheet("""
            QFrame {
                background-color: #171b2d;
                border-bottom: 1px solid #2b3147;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(0)

        logo_label = QLabel("🤖")
        logo_label.setStyleSheet("font-size: 18px; background: transparent;")
        layout.addWidget(logo_label)

        title_label = QLabel("KeyRusher Launcher")
        title_label.setStyleSheet("color: #f5f6fb; font-size: 14px; font-weight: 700; background: transparent; margin-left: 8px;")
        layout.addWidget(title_label)

        layout.addStretch()

        modules_label = QLabel(f"{len(MODULES)} модулей")
        modules_label.setStyleSheet("color: #7ca6ff; font-size: 11px; font-weight: 600; background: transparent; margin-right: 16px;")
        layout.addWidget(modules_label)

        self.min_btn = QLabel("─")
        self.min_btn.setFixedSize(32, 32)
        self.min_btn.setAlignment(Qt.AlignCenter)
        self.min_btn.setStyleSheet("""
            QLabel {
                background-color: #2a3048;
                color: #a8b3e0;
                border-radius: 8px;
                font-size: 18px;
                font-weight: 600;
            }
            QLabel:hover {
                background-color: #3a4060;
                color: white;
            }
        """)
        self.min_btn.mousePressEvent = self.minimize_window
        layout.addWidget(self.min_btn)

        self.close_btn = QLabel("✕")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setAlignment(Qt.AlignCenter)
        self.close_btn.setStyleSheet("""
            QLabel {
                background-color: #2a3048;
                color: #ff8a8a;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                margin-left: 8px;
            }
            QLabel:hover {
                background-color: #d55255;
                color: white;
            }
        """)
        self.close_btn.mousePressEvent = self.close_window
        layout.addWidget(self.close_btn)

    def minimize_window(self, event):
        self.parent.showMinimized()

    def close_window(self, event):
        self.parent.stop_current_bot()
        self.parent.close()


class InfoCard(QFrame):
    def __init__(self, title: str, value: str, accent: str):
        super().__init__()
        self.title_label = QLabel(title)
        self.value_label = QLabel(value)
        self.setMinimumHeight(74)
        self.setStyleSheet("background: transparent; border: 1px solid #2a3048; border-radius: 16px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(7)
        self.title_label.setStyleSheet("color: #7f8aad; font-size: 11px; font-weight: 700; background: transparent;")
        self.value_label.setStyleSheet(f"color: {accent}; font-size: 16px; font-weight: 800; background: transparent;")
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, text: str):
        self.value_label.setText(text)


class IconTile(QFrame):
    def __init__(self, title: str, image_name: str, owner):
        super().__init__(owner)
        self.owner = owner
        self.title = title
        self.image_name = image_name
        self.active = False
        self.setFixedSize(128, 154)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")

        self.visual_x = 11
        self.visual_y = 4
        self.visual_w = 96
        self.visual_h = 96
        self.icon_x = 16
        self.icon_y = 9
        self.icon_w = 86
        self.icon_h = 86

        self.icon_label = QLabel(self)
        self.icon_label.setGeometry(self.icon_x, self.icon_y, self.icon_w, self.icon_h)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")

        self.title_label = QLabel(title, self)
        self.title_label.setGeometry(2, 106, 124, 34)
        self.title_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("color: white; font-size: 10px; font-weight: 800; background: transparent;")

        self.dot_label = QLabel(self)
        self.dot_label.setGeometry(90, 7, 15, 15)

        self.reload_icon()
        self.update_state_styles()

    def reload_icon(self):
        path = get_icon_path(self.image_name)
        pix = make_rounded_pixmap(path, self.icon_w, self.icon_h, 19)
        self.icon_label.setPixmap(pix)

    def set_active(self, active: bool):
        self.active = active
        self.update_state_styles()
        self.update()

    def update_state_styles(self):
        if self.active:
            self.dot_label.setStyleSheet("QLabel { background-color: #16ec55; border-radius: 7px; }")
        else:
            self.dot_label.setStyleSheet("QLabel { background-color: #ececf2; border-radius: 7px; }")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.owner.select_module(self)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.active:
            pen = QPen(QColor("#16ec55"), 4)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.visual_x, self.visual_y, self.visual_w, self.visual_h, 23, 23)

        painter.end()


class LauncherWindow(QWidget):
    start_signal = pyqtSignal()
    stop_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.tiles = []
        self.current_module = None
        self.bot_running = False
        self.dragging = False
        self.drag_pos = None
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()

        self.start_signal.connect(self.start_current_bot)
        self.stop_signal.connect(self.stop_current_bot)

        self.setup_hotkeys()

    def setup_hotkeys(self):
        keyboard.add_hotkey('f7', lambda: self.start_signal.emit())
        keyboard.add_hotkey('f9', lambda: self.stop_signal.emit())

        print("\n" + "=" * 50)
        print("🎮 УПРАВЛЕНИЕ:")
        print("   Выбери модуль в интерфейсе")
        print("   F7 - Запустить бота")
        print("   F9 - Остановить бота")
        print("=" * 50 + "\n")

    def ask_question(self, title, question, callback_yes):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.buttonClicked.connect(lambda btn: self.on_question_answer(btn, callback_yes))
        msg.show()

    def on_question_answer(self, button, callback_yes):
        if button.text() == "&Yes":
            callback_yes()

    def start_current_bot(self):
        global bot_overlay

        if self.current_module is None:
            print("⚠️ Сначала выбери модуль в интерфейсе!")
            return

        if self.bot_running:
            print("⚠️ Бот уже запущен!")
            return

        module_name = self.current_module.title
        print(f"\n🚀 Запуск {module_name}...")

        if bot_overlay:
            try:
                bot_overlay.close()
            except Exception:
                pass

        bot_overlay = SimpleOverlay(module_name)

        started = True

        if module_name == "Рулетка":
            start_wheel_bot()
            self.ask_question("Анти-АФК", "Запустить анти-АФК вместе с колесом?", start_afk_bot)
        elif module_name == "Анти-Афк":
            start_afk_bot()
            self.ask_question("Колесо удачи", "Запустить колесо вместе с анти-АФК?", start_wheel_bot)
        elif module_name == "Швейка":
            start_sewing_bot()
        elif module_name == "Токарка":
            start_lathe_bot()
        elif module_name == "Смузи":
            start_smoothie_bot()
        elif module_name == "Порт":
            start_port_bot()
        else:
            print(f"⚠️ Модуль {module_name} в разработке")
            started = False

        if not started:
            try:
                bot_overlay.close()
            except Exception:
                pass
            bot_overlay = None
            return

        self.bot_running = True
        self.status_card.set_value("Работает")
        self.module_card.set_value(module_name)

    def stop_current_bot(self):
        global bot_overlay

        if not self.bot_running:
            print("⚠️ Бот не запущен")
            return

        module_name = self.current_module.title if self.current_module else "Неизвестно"
        print(f"\n⏹ Остановка {module_name}...")

        if module_name == "Порт":
            stop_port_bot()
        elif module_name == "Смузи":
            stop_smoothie_bot()
        elif module_name == "Анти-Афк":
            stop_afk_bot()
            stop_wheel_bot()
        elif module_name == "Рулетка":
            stop_wheel_bot()
            stop_afk_bot()
        elif module_name == "Швейка":
            stop_sewing_bot()
        elif module_name == "Токарка":
            stop_lathe_bot()

        self.bot_running = False

        if bot_overlay:
            try:
                bot_overlay.close()
                bot_overlay = None
            except Exception:
                pass

        self.status_card.set_value("Готов")
        if self.current_module:
            self.module_card.set_value(self.current_module.title)
        else:
            self.module_card.set_value("Не выбран")

    def init_ui(self):
        self.setWindowTitle("KeyRusher Launcher")
        self.setFixedSize(820, 860)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        content = QFrame()
        content.setStyleSheet("background-color: #121524;")
        main_layout.addWidget(content)

        self.build_body(content)

    def build_body(self, parent):
        main = QVBoxLayout(parent)
        main.setContentsMargins(24, 14, 24, 18)
        main.setSpacing(14)

        banner = QFrame()
        banner.setFixedHeight(62)
        banner.setStyleSheet("background-color: #1b2031; border: 1px solid #33405d; border-radius: 18px;")
        banner_layout = QHBoxLayout(banner)
        banner_text = QLabel("🎮 Нажми на иконку для выбора модуля → F7 запуск | F9 остановка")
        banner_text.setAlignment(Qt.AlignCenter)
        banner_text.setStyleSheet("color: white; font-size: 13px; font-weight: 800; background: transparent;")
        banner_layout.addWidget(banner_text)
        main.addWidget(banner)

        grid_wrap = QFrame()
        grid_wrap.setStyleSheet("background: transparent;")
        grid_wrap_layout = QHBoxLayout(grid_wrap)
        grid_wrap_layout.setContentsMargins(0, 8, 0, 0)
        grid_wrap_layout.addStretch()

        grid_container = QWidget()
        grid = QGridLayout(grid_container)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)

        row, col = 0, 0
        for title, icon in MODULES:
            tile = IconTile(title, icon, self)
            self.tiles.append(tile)
            grid.addWidget(tile, row, col, alignment=Qt.AlignTop | Qt.AlignHCenter)
            col += 1
            if col >= 5:
                col = 0
                row += 1

        grid_wrap_layout.addWidget(grid_container)
        grid_wrap_layout.addStretch()
        main.addWidget(grid_wrap, 1)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(14)

        self.status_card = InfoCard("Статус", "Готов", "#73df8d")
        self.module_card = InfoCard("Активный модуль", "Не выбран", "#7ca6ff")

        bottom_row.addWidget(self.status_card)
        bottom_row.addWidget(self.module_card)
        main.addLayout(bottom_row)

    def select_module(self, tile):
        if self.bot_running:
            print("⚠️ Сначала останови бота (F9)!")
            return

        if self.current_module == tile:
            return

        if self.current_module:
            self.current_module.set_active(False)

        tile.set_active(True)
        self.current_module = tile
        self.status_card.set_value("Выбран")
        self.module_card.set_value(tile.title)
        print(f"📌 Выбран модуль: {tile.title}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.dragging = True
            self.drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def closeEvent(self, event):
        self.stop_current_bot()
        try:
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        event.accept()


if __name__ == "__main__":
    print("Загрузка...")
    load_sewing_templates()
    load_lathe_template()

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec_())
