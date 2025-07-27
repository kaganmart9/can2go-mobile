# screens/dashboard.py

from kivymd.uix.boxlayout import MDBoxLayout  # Material dikey düzen kutusu
from kivymd.uix.tab import MDTabsBase  # Sekme tabanı
from kivymd.uix.card import MDCard  # Kart bileşeni
from kivymd.uix.label import MDLabel  # Metin gösterimi
from kivymd.uix.button import MDIconButton, MDRaisedButton  # İkonlu ve yükseltilmiş butonlar
from kivymd.uix.menu import MDDropdownMenu  # Açılır menü
from kivymd.uix.scrollview import MDScrollView  # Kaydırılabilir alan
from kivy.clock import Clock  # Zamanlanmış görevler
from kivy.metrics import dp  # DPI bağımsız ölçümler
from utils.parser import parse_metrics  # Ham veriyi metriklere çevirme
from datetime import datetime  # (Gerekirse zaman damgası için)

class DashboardScreen(MDBoxLayout, MDTabsBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dikey düzen, iç boşluklar ve aralıklar
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)

        # Data yapıları: her BCU ve toplam için metrikler
        self.metrics = {f"BCU {i}": {"soc": 0, "soh": 0, "voltage": 0, "temperature": 0} for i in range(1,17)}
        self.metrics["Total"] = {"soc": 0, "soh": 0, "voltage": 0, "temperature": 0}
        self.selected = "Total"  # Başlangıç seçimi

        # Dropdown menü için öğeler
        items = [
            {"text": name, "viewclass": "OneLineListItem", "on_release": lambda x=name: self._set_selection(x)}
            for name in ["Total"] + [f"BCU {i}" for i in range(1,17)]
        ]
        # Seçim butonu
        self.dd_btn = MDRaisedButton(
            text="Total",
            size_hint=(None,None),
            size=(dp(120), dp(40)),
            pos_hint={"center_x":0.5},
            on_release=self._open_menu
        )
        self.menu = MDDropdownMenu(caller=self.dd_btn, items=items, width_mult=4)
        self.add_widget(self.dd_btn)

        # Kaydırılabilir konteyner
        scroll = MDScrollView()
        self.container = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10), size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll.add_widget(self.container)
        self.add_widget(scroll)

        # Kartları oluştur ve sakla
        self.cards = {}
        self._build_cards()

    def _build_cards(self):
        # SOC, SOH, Voltage ve Temperature için kartlar
        card_style = {"md_bg_color": (0.95,0.95,0.95,1)}
        mapping = {
            "soc": ("State of Charge", "battery"),
            "soh": ("State of Health", "heart"),
            "voltage": ("Voltage", "flash"),
            "temperature": ("Temperature", "thermometer")
        }
        for key, (title, icon) in mapping.items():
            card = MDCard(orientation="horizontal", size_hint=(1,None), height=dp(90), padding=dp(10), **card_style)
            # İkon
            card.add_widget(MDIconButton(icon=icon, theme_text_color="Secondary"))
            # Metin kutusu: başlık ve değer
            box = MDBoxLayout(orientation='vertical')
            box.add_widget(MDLabel(text=title, font_style="Subtitle1", theme_text_color="Primary"))
            value_lbl = MDLabel(text="0", font_style="H6", theme_text_color="Primary")
            box.add_widget(value_lbl)
            card.add_widget(box)
            self.container.add_widget(card)
            # Label referansını sakla
            self.cards[key] = value_lbl

    def _open_menu(self, *args):
        # Dropdown menüyü aç
        self.menu.open()

    def _set_selection(self, name):
        # Yeni seçimi uygula ve ekranda güncelle
        self.selected = name
        self.dd_btn.text = name
        self.menu.dismiss()
        self._refresh_display()

    def on_new_data(self, data: bytes):
        # Gelen verileri işlemek için zamanla planla
        Clock.schedule_once(lambda dt: self._process_data(data))

    def _process_data(self, data: bytes):
        # Ham veriyi ayrıştır
        parsed = parse_metrics(data)
        # Hangi BCU olduğunu belirle (örnek: ilk byte ile)
        bcu = f"BCU {(data[0] % 16) + 1}"
        # BCU metriklerini güncelle
        self.metrics[bcu] = parsed
        # Total için ortalamaları hesapla
        total = {"soc":0,"soh":0,"voltage":0,"temperature":0}
        for i in range(1,17):
            m = self.metrics[f"BCU {i}"]
            for k in total:
                total[k] += m[k]
        for k in total:
            total[k] /= 16
        self.metrics["Total"] = total
        # Ekranı yenile
        self._refresh_display()

    def _refresh_display(self):
        # Seçili metrikleri kartlara yaz
        m = self.metrics[self.selected]
        self.cards["soc"].text = f"{m['soc']}%"
        self.cards["soh"].text = f"{m['soh']}%"
        self.cards["voltage"].text = f"{m['voltage']:.2f} V"
        self.cards["temperature"].text = f"{m['temperature']}°C"