# screens/settings.py

from kivy.metrics import dp  # DPI bağımsız boşluklar için
from kivy.clock import Clock  # Ana UI thread'e geri bildirim yapmak için
from kivymd.uix.boxlayout import MDBoxLayout  # Dikey düzen kutusu
from kivymd.uix.tab import MDTabsBase  # Sekme temel sınıfı
from kivymd.uix.button import MDRaisedButton  # Yükseltilmiş Material buton
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget  # Cihaz listesi ve ikon bileşenleri
from kivymd.uix.scrollview import MDScrollView  # Kaydırılabilir liste için
from kivymd.uix.label import MDLabel  # Metin göstermek için

from bleak import BleakScanner  # BLE cihaz taraması
import threading  # Arka planda tarama iş parçacığı
import asyncio  # Asenkron BLE tarama işlemi

class SettingsScreen(MDBoxLayout, MDTabsBase):
    def __init__(self, connect_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'  # Yatay değil, dikey düzen
        self.padding = dp(20)  # Kenar boşlukları
        self.spacing = dp(10)  # İçerikler arası boşluk
        self.connect_callback = connect_callback  # Seçilen cihazı ana uygulamaya iletmek için

        # Başlık etiketi
        self.add_widget(
            MDLabel(
                text="Bluetooth Ayarları",
                font_style="H5",
                size_hint_y=None,
                height=dp(40)
            )
        )

        # Tara butonu: Cihaz aramayı başlatır
        self.scan_btn = MDRaisedButton(
            text="Cihazları Tara",
            size_hint=(1, None),
            height=dp(40),
            on_release=self.start_scan
        )
        self.add_widget(self.scan_btn)

        # Durum mesajı: Taranıyor, hata, bağlandı bildirimleri
        self.msg_label = MDLabel(
            text="",
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Secondary",
            halign="center"
        )
        self.add_widget(self.msg_label)

        # Cihaz listesini gösterecek kaydırılabilir alan
        self.scroll = MDScrollView()
        self.device_list = MDList(spacing=dp(4), padding=[0,0,0,dp(10)])
        self.scroll.add_widget(self.device_list)
        self.add_widget(self.scroll)

    def start_scan(self, *args):
        # Tarama öncesi listeyi temizle ve mesajı güncelle
        self.device_list.clear_widgets()
        self.msg_label.text = "Taranıyor..."
        # BLE taramasını iş parçacığında yap
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        try:
            # Yeni event loop oluşturup asenkron taramayı gerçekleştir
            loop = asyncio.new_event_loop()
            devices = loop.run_until_complete(BleakScanner.discover())
            loop.close()
            # UI güncellemesini ana thread'e planla
            Clock.schedule_once(lambda dt: self._show_devices(devices), 0)
        except Exception as e:
            # Hata durumunu ana thread ile göster
            Clock.schedule_once(lambda dt, err=e: self._show_error(err), 0)

    def _show_devices(self, devices):
        # Bulunan cihazlar yoksa hata göster
        if not devices:
            self._show_error("Hiç cihaz bulunamadı.")
            return
        # Cihaz sayısını kullanıcıya bildir
        self.msg_label.text = f"{len(devices)} cihaz bulundu."
        # Her cihaz için liste öğesi oluştur
        for d in devices:
            name = d.name or "Adsız"
            addr = d.address
            item = OneLineIconListItem(
                text=f"{name} — {addr}",
                on_release=lambda widget, a=addr: self._select_device(a)
            )
            icon = IconLeftWidget(icon="bluetooth", theme_text_color="Primary")
            item.add_widget(icon)
            self.device_list.add_widget(item)

    def _show_error(self, err):
        # Hata veya bilgi mesajını güncelle
        self.msg_label.text = f"Hata: {err}"

    def _select_device(self, address):
        # Seçilen cihazı kullanıcıya bildir ve callback ile ilet
        self.msg_label.text = f"Seçildi: {address}"
        self.connect_callback(address)
