# screens/errors.py

from kivy.metrics import dp  # DPI bağımsız ölçümler için
from kivy.clock import Clock  # UI thread'e görev planlamak için
from kivymd.uix.boxlayout import MDBoxLayout  # Material kutu düzeni
from kivymd.uix.tab import MDTabsBase  # Sekme temel sınıfı
from kivymd.uix.scrollview import MDScrollView  # Kaydırılabilir liste
from kivymd.uix.list import MDList, TwoLineAvatarListItem, IconLeftWidget  # Hata listesi bileşenleri
from kivymd.uix.menu import MDDropdownMenu  # Açılır menü
from kivymd.uix.button import MDRaisedButton  # Yükseltilmiş buton
from kivymd.uix.label import MDLabel  # Metin göstermek için
from utils.parser import parse_error  # Gelen veriyi hata mesajı ve koda dönüştürmek için
from datetime import datetime  # Zaman damgası oluşturmak için
import random  # Demo amacıyla rastgele BCU seçmek için (gerçek veride kaldırılabilir)

class ErrorScreen(MDBoxLayout, MDTabsBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dikey düzen, kenar boşlukları ve aralıklar
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)

        # Her BCU için hata listesini başlat
        self.bcu_errors = {f"BCU {i}": [] for i in range(1, 17)}
        self.selected_bcu = "BCU 1"  # Varsayılan seçili BCU

        # BCU seçmek için açılır menüyü tetikleyen buton
        self.dropdown_button = MDRaisedButton(
            text=self.selected_bcu,
            size_hint=(None, None),
            size=(dp(120), dp(40)),
            pos_hint={"center_x": 0.5},
            on_release=self.open_menu
        )
        # Menü öğelerini oluştur
        menu_items = [
            {
                "text": f"BCU {i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"BCU {i}": self.set_bcu(x)
            } for i in range(1, 17)
        ]
        self.menu = MDDropdownMenu(caller=self.dropdown_button, items=menu_items, width_mult=4)
        self.add_widget(self.dropdown_button)

        # Hata mesajlarını göstermek için kaydırılabilir liste
        scroll = MDScrollView()
        self.error_list = MDList(spacing=dp(4), padding=[0,0,0,dp(10)])
        scroll.add_widget(self.error_list)
        self.add_widget(scroll)

    def open_menu(self, *args):
        # BCU seçim menüsünü aç
        self.menu.open()

    def set_bcu(self, bcu_name):
        # Yeni BCU adını uygula ve listeyi yenile
        self.selected_bcu = bcu_name
        self.dropdown_button.text = bcu_name
        self.menu.dismiss()
        self.refresh_error_list()

    def on_new_data(self, data: bytes):
        # Yeni veri geldiğinde, hataları güncellemek için UI thread'e ilet
        Clock.schedule_once(lambda dt: self.update_errors(data), 0)

    def update_errors(self, data: bytes):
        # Ham veriyi anlamlı hataya parse et
        parsed = parse_error(data)
        if not parsed:
            return  # Geçersiz veri ise çık
        # Demo: rastgele bir BCU seç (gerçek kullanımda doğrudan ilgili BCU'dan al)
        sim_bcu = f"BCU {random.randint(1, 16)}"
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Zaman damgası
        # Hata bilgisini o BCU için sakla
        self.bcu_errors[sim_bcu].append((parsed["error_message"], parsed["error_code"], ts))
        # Eğer kayıtlı BCU seçiliyse listeye ekle
        if sim_bcu == self.selected_bcu:
            self._add_item(parsed["error_message"], parsed["error_code"], ts)

    def refresh_error_list(self):
        # Mevcut seçili BCU'nun tüm hatalarını listele
        self.error_list.clear_widgets()
        for msg, code, ts in self.bcu_errors[self.selected_bcu]:
            self._add_item(msg, code, ts)

    def _add_item(self, message, code, timestamp):
        # İki satırlı liste öğesi oluştur: mesaj ve zaman+kod
        item = TwoLineAvatarListItem(
            text=message,
            secondary_text=f"{timestamp}    Code: 0x{code:02X}",
            _no_ripple_effect=True
        )
        # Hatanın yanına uyarı ikonu ekle
        icon = IconLeftWidget(icon="alert-circle", theme_text_color="Error")
        item.add_widget(icon)
        self.error_list.add_widget(item)