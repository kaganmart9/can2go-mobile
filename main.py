# main.py

import threading  # subprocessler için
import asyncio  # asenkron işlemler için


from kivy.core.window import Window
from kivy.metrics import dp  # DPI
from kivy.uix.image import Image  # logo için
from kivy.uix.floatlayout import FloatLayout  #şuan yok ama güncellemeler için gerekli olabilir

from kivymd.app import MDApp  # Material Design
from kivymd.uix.screenmanager import MDScreenManager  # Ekranlar arası geçiş
from kivymd.uix.tab import MDTabs  # Sekme menüsü
from kivymd.uix.screen import MDScreen  # Temel ekranlar

from screens.dashboard import DashboardScreen  # Dashboard
from screens.errors import ErrorScreen       # Error
from screens.logs import LogsScreen        # Logs
from screens.login import LoginScreen      # Login
from screens.settings import SettingsScreen  # Settings

from utils.bluetooth_manager import BluetoothManager  # BLE işlemleri için


class MainApp(MDApp):
    title = "CAN2Go Mobile"  # Uygulama ismi
    icon = "assets/logo.png"  # Uygulama logosu

    def build(self):
        Window.set_title(self.title)  # Pencere başlığını ayarlama
        Window.set_icon(self.icon)  # Pencere logosunu ayarlama

        # BLE kullanımı için gerekli alanlar
        self.esp32_address = None  # ESP32 adresi
        self.char_uuid = "abcd1234-5678-90ab-cdef-1234567890ab"  # BLE UUID
        self.bt_manager = BluetoothManager()  # BLE manager
        self.screen_manager = MDScreenManager()  # Ekran manager

        # 1️⃣ Login ekranını oluştur ve yöneticine ekle
        self.login_screen = LoginScreen(login_success_callback=self.show_main_tabs)
        self.login_screen.name = "login"
        self.screen_manager.add_widget(self.login_screen)

        # 2️⃣ Ana sekmeli ekranı hazırla ve ekle
        self.tabs_screen = self.build_main_tabs()
        self.tabs_screen.name = "main_tabs"
        self.screen_manager.add_widget(self.tabs_screen)

        # Önce login ekranını göster
        self.screen_manager.current = "login"
        return self.screen_manager

    def build_main_tabs(self):
        tabs_screen = MDScreen()  # Sekme ekranı konteyneri

        # ◆ MDTabs yapılandırması: Tam ekran sekmeler
        self.tabs = MDTabs(
            tab_hint_x=False,
            tab_bar_height=dp(48),
            tab_indicator_height=dp(3),
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )

        # Sekme içeriklerini örnekle
        self.dashboard = DashboardScreen(); self.dashboard.title = "Dashboard"
        self.errors    = ErrorScreen();    self.errors.title    = "Errors"
        self.logs      = LogsScreen();     self.logs.title      = "Logs"
        # Ayarlar sekmesi, BLE bağlantı callback'i ile
        self.settings  = SettingsScreen(connect_callback=self.on_bluetooth_connect)
        self.settings.title = "Settings"

        # Tüm sekmeleri MDTabs'e ekle
        for screen in (self.dashboard, self.errors, self.logs, self.settings):
            self.tabs.add_widget(screen)

        tabs_screen.add_widget(self.tabs)  # Sekmeleri ekrana yerleştir

        # ◇ Sol-alt köşeye yarı şeffaf logo ekle
        logo = Image(
            source=self.icon,
            size_hint=(None, None),
            size=(dp(60), dp(60)),
            pos_hint={"x": 0, "y": 0},
            opacity=0.6
        )
        tabs_screen.add_widget(logo)

        return tabs_screen

    def show_main_tabs(self):
        # Login sonrası ana sekmeli ekrana geçiş
        self.screen_manager.current = "main_tabs"

    def on_bluetooth_connect(self, address: str):
        # BLE adresi atama
        self.esp32_address = address

        # Gelen verileri tüm ekranlara ileten dispatch fonksiyonu
        def dispatch(data: bytes):
            self.dashboard.on_new_data(data)
            self.errors.on_new_data(data)
            self.logs.on_new_data(data)

        # BLE dinleme işlemini arka planda çalışan bir thread'e taşı
        def ble_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def runner():
                # Belirlenen adrese bağlan ve dinleme başlat
                await self.bt_manager.connect_and_listen_fixed_address(
                    self.esp32_address,
                    self.char_uuid,
                    dispatch
                )

            loop.run_until_complete(runner())  # Bağlan ve dinleme
            try:
                loop.run_forever()  # Sürekli dinle
            finally:
                # Uygulama kapanırken bağlantıyı kes
                loop.run_until_complete(self.bt_manager.disconnect())
                loop.close()

        # Thread'i başlat (daemon=True, ana thread kapanınca duracak)
        threading.Thread(target=ble_thread, daemon=True).start()

    def on_stop(self):
        # Uygulama kapanırken BLE bağlantısını temizle
        if getattr(self.bt_manager, "connected", False):
            try:
                asyncio.run(self.bt_manager.disconnect())
            except Exception as e:
                print(f"[on_stop ERROR] {e}")
        return super().on_stop()


if __name__ == "__main__":
    MainApp().run()  # Uygulamayı başlat
