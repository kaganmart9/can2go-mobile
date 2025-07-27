# components/bluetooth_settings.py

import threading  # BLE taramasını ana akışı bloklamadan yapmak için
import asyncio   # Asenkron BLE işlemleri
from kivy.clock import Clock  # UI güncellemelerini planlamak için
from kivy.metrics import dp  # DPI bağımsız ölçümler
from kivymd.uix.dialog import MDDialog  # Diyalog pencereleri
from kivymd.uix.boxlayout import MDBoxLayout  # Dikey düzen kutusu
from kivymd.uix.label import MDLabel  # Metin göstermek için
from kivymd.uix.scrollview import MDScrollView  # Kaydırılabilir alan
from kivymd.uix.list import MDList, OneLineListItem  # Basit liste bileşenleri
from bleak import BleakScanner  # BLE cihaz tarayıcı

class BluetoothSettingsDialog:
    def __init__(self, select_callback=None):
        """
        select_callback: cihaz seçildiğinde adresiyle çağrılacak fonksiyon
        """
        self.dialog = None
        self.label = None
        self.device_list = None
        self.select_callback = select_callback  # Seçim callback'i

    def open(self):
        # Diyalog içeriği: başlık, etiket ve cihaz listesi
        container = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        self.label = MDLabel(text="Cihazlar taranıyor...", halign="center")
        container.add_widget(self.label)

        # Sabit yüksekliğe sahip kaydırılabilir liste
        scroll = MDScrollView(size_hint=(1, None), height=dp(200), bar_width=dp(4), scroll_type=['bars', 'content'])
        self.device_list = MDList()
        scroll.add_widget(self.device_list)
        container.add_widget(scroll)

        # Diyaloğu oluştur ve göster
        self.dialog = MDDialog(
            title="Bluetooth Cihaz Seçimi",
            type="custom",
            content_cls=container,
            size_hint=(0.8, None),
            height=dp(300),
            buttons=[]
        )
        self.dialog.open()

        # Cihaz taramayı arka planda başlat
        threading.Thread(target=self._scan_in_thread, daemon=True).start()

    def _scan_in_thread(self):
        try:
            # Asenkron keşif işlemi, süre sınırı 5 saniye
            devices = asyncio.run(BleakScanner.discover(timeout=5.0))
        except Exception as e:
            # Hata mesajını UI thread'e ilet
            Clock.schedule_once(lambda dt: self._set_label(f"Hata: {e}"))
            return
        # Bulunan cihazları UI thread'te listele
        Clock.schedule_once(lambda dt: self._populate_list(devices))

    def _set_label(self, text: str):
        # Durum etiketini güncelle
        if self.label:
            self.label.text = text

    def _populate_list(self, devices):
        # Debug bilgisi: konsola cihaz sayısını yaz
        print(f"[BluetoothSettingsDialog] {len(devices)} cihaz bulundu")

        self.device_list.clear_widgets()

        if not devices:
            self._set_label("Hiçbir cihaz bulunamadı.")
            return

        self._set_label("Bulunan Cihazlar (tıklayarak seç):")
        # Her cihaz için liste öğesi oluştur
        for d in devices:
            name = d.name or "Adsız"
            address = d.address
            item_text = f"{name} — {address}"
            item = OneLineListItem(text=item_text, on_release=lambda x, addr=address: self._on_device_selected(addr))
            self.device_list.add_widget(item)

    def _on_device_selected(self, address: str):
        # Cihaz seçildiğinde callback'i çağır ve diyaloğu kapat
        if self.select_callback:
            self.select_callback(address)
        self.dialog.dismiss()