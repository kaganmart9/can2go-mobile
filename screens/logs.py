# screens/logs.py

import importlib  # Android için dinamik modül yükleme
import platform  # Platform kontrolü
import os        # Dosya yolu işlemleri
from datetime import datetime  # Zaman damgası oluşturmak için

from kivy.clock import Clock  # Zamanlanmış görevler için
from kivy.metrics import dp  # DPI bağımsız ölçümler
from kivy.uix.boxlayout import BoxLayout  # Yatay/dikey düzenleme
from kivymd.uix.boxlayout import MDBoxLayout  # Material kutu düzeni
from kivymd.uix.tab import MDTabsBase  # Sekme temel sınıfı
from kivymd.uix.label import MDLabel  # Metin gösterimi
from kivymd.uix.button import MDIconButton, MDRaisedButton  # İkonlu ve yükseltilmiş butonlar
from kivymd.uix.dialog import MDDialog  # Diyalog pencereleri
from kivymd.uix.textfield import MDTextField  # Metin girişi
from kivymd.uix.gridlayout import MDGridLayout  # Esnek ızgara düzeni
from kivymd.uix.menu import MDDropdownMenu  # Açılır menü
from kivymd.uix.list import OneLineListItem  # Basit liste öğesi

# Android tespiti ve paylaşım fonksiyonu
IS_ANDROID = platform.system() == "Android"
try:
    from plyer import share  # Android paylaşım API
except ImportError:
    share = None

# Android dışı dosya kaydetme için tkinter
primary_external_storage_path = None
if IS_ANDROID:
    try:
        android_storage = importlib.import_module("android.storage")
        primary_external_storage_path = android_storage.primary_external_storage_path
    except (ImportError, AttributeError):
        primary_external_storage_path = None

# Masaüstü kaydetmek için filedialog
tk = filedialog = None
if not IS_ANDROID:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        tk = None
        filedialog = None

class LogsScreen(MDBoxLayout, MDTabsBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Genel düzen ayarları
        self.orientation = 'vertical'
        self.padding = [dp(20), dp(20), dp(20), dp(80)]
        self.spacing = dp(10)

        # Kayıt verileri ve ayarlar
        self.log_data = []  # Zaman damgası + hex veriler listesi
        self.latest_data = None  # Son alınan veri
        self.log_event = None  # Zamanlanmış kayıt olayı
        self.log_interval = 1  # Varsayılan 1 saniye

        # Durum göstergesi
        self.status_label = MDLabel(
            text="Hazır",
            halign="center",
            theme_text_color="Primary",
            size_hint=(1, None),
            height=dp(40)
        )
        self.add_widget(self.status_label)

        # Zaman aralığı seçimi: girdi ve açılır menü ikonu
        hl = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40), spacing=dp(10))
        self.interval_input = MDTextField(
            hint_text="Saniye",
            text=str(self.log_interval),
            mode="rectangle",
            size_hint=(0.7, 1)
        )
        hl.add_widget(self.interval_input)

        # Açılır menü butonu
        self.dd_icon = MDIconButton(
            icon="chevron-down",
            icon_size=dp(24),
            on_release=self._open_dropdown
        )
        hl.add_widget(self.dd_icon)
        self.add_widget(hl)

        # Menü seçenekleri
        items = [
            {"text": "50 ms", "viewclass": "OneLineListItem", "on_release": lambda x="0.05": self._select_interval(x)},
            {"text": "2 s",  "viewclass": "OneLineListItem", "on_release": lambda x="2":    self._select_interval(x)},
            {"text": "5 s",  "viewclass": "OneLineListItem", "on_release": lambda x="5":    self._select_interval(x)},
            {"text": "10 s", "viewclass": "OneLineListItem", "on_release": lambda x="10":   self._select_interval(x)},
            {"text": "20 s", "viewclass": "OneLineListItem", "on_release": lambda x="20":   self._select_interval(x)},
            {"text": "50 s", "viewclass": "OneLineListItem", "on_release": lambda x="50":   self._select_interval(x)},
        ]
        self.dropdown = MDDropdownMenu(caller=self.dd_icon, items=items, width_mult=3)

        # Kayıt kontrol butonları: Başlat, Durdur, Sıfırla, Paylaş
        button_grid = MDGridLayout(
            cols=2,
            spacing=dp(15),
            padding=[0, 0, 0, dp(20)],
            adaptive_height=True
        )
        btn_style = {"size_hint": (1, None), "height": dp(60), "md_bg_color": (0.2, 0.5, 0.9, 1)}
        self.start_button = MDRaisedButton(text="Başlat", icon="record-circle", on_release=self.start_recording, **btn_style)
        self.stop_button  = MDRaisedButton(text="Durdur", icon="stop-circle",     on_release=self.stop_recording, **btn_style)
        self.reset_button = MDRaisedButton(text="Sıfırla", icon="backup-restore", on_release=self.reset_log, **btn_style)
        self.share_button = MDRaisedButton(text="Paylaş", icon="share-variant",   on_release=self.share_log, disabled=True, **btn_style)

        for w in (self.start_button, self.stop_button, self.reset_button, self.share_button):
            button_grid.add_widget(w)
        self.add_widget(button_grid)

    def _open_dropdown(self, *args):
        # Zaman aralığı menüsünü göster
        self.dropdown.open()

    def _select_interval(self, value_str):
        # Seçilen değeri girdi alanına yaz ve güncelle
        self.interval_input.text = value_str
        self.log_interval = float(value_str)
        self.dropdown.dismiss()

    def on_new_data(self, data: bytes):
        # Yeni veri geldiğinde sakla
        self.latest_data = data

    def _log_latest(self, dt):
        # Son veriyi zaman damgasıyla kaydet
        if self.latest_data is None:
            return
        hex_data = self.latest_data.hex(' ').upper()
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.log_data.append((ts, hex_data))
        self.status_label.text = f"Kaydedilen: {len(self.log_data)}"

    def start_recording(self, *args):
        # Aralık değeri geçerliyse kaydı başlat
        try:
            val = float(self.interval_input.text)
            if val <= 0:
                raise ValueError
            self.log_interval = val
        except ValueError:
            MDDialog(title="Hata", text="Geçerli bir sayı girin.", size_hint=(0.8,0.3)).open()
            return
        # Önceki zamanlanan kaydı iptal et
        if self.log_event:
            Clock.unschedule(self.log_event)
        self.log_data.clear()
        self.start_button.disabled = True
        self.share_button.disabled = True
        self.status_label.text = "Kayıt başladı..."
        # Zamanlanmış kaydı başlat
        self.log_event = Clock.schedule_interval(self._log_latest, self.log_interval)

    def stop_recording(self, *args):
        # Kaydı durdur ve dosya ismi sor
        if self.log_event:
            Clock.unschedule(self.log_event)
            self.log_event = None
        self.start_button.disabled = False
        self.ask_filename()

    def reset_log(self, *args):
        # Kayıt verisini sıfırla
        if self.log_event:
            Clock.unschedule(self.log_event)
            self.log_event = None
        self.log_data.clear()
        self.start_button.disabled = False
        self.share_button.disabled = True
        self.status_label.text = "Kayıt sıfırlandı."

    def ask_filename(self):
        # Kaydedilecek dosya adını girmek için diyalog
        self.filename_input = MDTextField(hint_text="Dosya adı", mode="rectangle")
        self.dialog = MDDialog(
            title="Log Kaydet",
            type="custom",
            content_cls=self.filename_input,
            buttons=[
                MDRaisedButton(text="İptal", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Kaydet", on_release=lambda x: self.finish_log_save())
            ]
        )
        self.dialog.open()

    def finish_log_save(self):
        # Diyalogdan alınan adı kontrol et
        filename = self.filename_input.text.strip()
        if not filename:
            MDDialog(title="Uyarı", text="Dosya adı boş.", size_hint=(0.8,0.3)).open()
            return
        filename += ".blf"

        # Android veya masaüstü için kayıt yolunu belirle
        if IS_ANDROID and primary_external_storage_path:
            save_path = os.path.join(primary_external_storage_path(), "Download", filename)
        else:
            if tk and filedialog:
                tk.Tk().withdraw()
                save_path = filedialog.asksaveasfilename(defaultextension=".blf", initialfile=filename,
                                                        filetypes=[("BLF Dosyası","*.blf")])
            else:
                MDDialog(title="Hata", text="Dosya seçici açılamıyor.", size_hint=(0.8,0.3)).open()
                return

        # Verileri dosyaya yaz ve paylaşmayı etkinleştir
        self.dialog.dismiss()
        with open(save_path, "w") as f:
            for ts, hx in self.log_data:
                f.write(f"{ts} || {hx}\n")
        self.share_button.disabled = False
        MDDialog(title="Başarılı", text=f"{save_path} kaydedildi.", size_hint=(0.8,0.3)).open()

    def share_log(self, *args):
        # Android paylaşım desteği varsa paylaş
        if not self.log_data:
            MDDialog(title="Uyarı", text="Kaydedilecek veri yok.", size_hint=(0.8,0.3)).open()
            return
        if share:
            try:
                share.share(filepath=self.last_saved_file, title="Log Paylaş")
            except Exception as e:
                MDDialog(title="Hata", text=str(e), size_hint=(0.8,0.3)).open()
        else:
            MDDialog(title="Bilgi", text="Paylaşım yalnızca Android'de destekler.", size_hint=(0.8,0.3)).open()
