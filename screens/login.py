# screens/login.py

from kivymd.uix.screen import MDScreen  # Material Design ekran sınıfı
from kivymd.uix.boxlayout import MDBoxLayout  # Dikey düzenleme için kutu
from kivymd.uix.textfield import MDTextField  # Metin girişi alanı
from kivymd.uix.button import MDRaisedButton  # Yükseltilmiş buton
from kivymd.uix.dialog import MDDialog  # Diyalog pencereleri
from kivy.uix.image import Image  # Görsel göstermek için
from kivy.metrics import dp  # DPI bağımsız ölçümler
from kivy.core.window import Window  # Pencere boyut bilgisi

class LoginScreen(MDScreen):
    def __init__(self, login_success_callback, **kwargs):
        super().__init__(**kwargs)
        # Giriş başarılı olunca çağrılacak fonksiyon
        self.login_success_callback = login_success_callback
        # Test amaçlı geçerli kullanıcı bilgileri
        self.valid_username = "admin"
        self.valid_password = "temsa"

        # Ana düzen: dikey, ortalanmış ve pencere boyuna göre yükseklik
        layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=[dp(40)] * 4,
            size_hint=(1, None),
            height=Window.height,
        )

        # Üstte logo: merkezlenmiş ve 150×150 dp boyutunda
        logo = Image(
            source="assets/logo.png",
            size_hint=(None, None),
            size=(dp(150), dp(150)),
            pos_hint={"center_x": 0.5}
        )
        layout.add_widget(logo)

        # Kullanıcı adı alanı
        self.username = MDTextField(
            hint_text="Kullanıcı Adı",
            icon_right="account",
            mode="rectangle",
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5}
        )
        layout.add_widget(self.username)

        # Şifre alanı: girilen karakterleri gizler
        self.password = MDTextField(
            hint_text="Şifre",
            icon_right="lock",
            password=True,
            mode="rectangle",
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5}
        )
        layout.add_widget(self.password)

        # Giriş butonu: tıklanınca kimlik kontrolü yapar
        login_btn = MDRaisedButton(
            text="Giriş Yap",
            pos_hint={"center_x": 0.5},
            on_release=self.check_credentials
        )
        layout.add_widget(login_btn)

        # Düzeni ekrana ekle
        self.add_widget(layout)

    def check_credentials(self, *args):
        # Girilen değerleri kontrol et
        if (self.username.text.strip() == self.valid_username and
                self.password.text.strip() == self.valid_password):
            # Doğruysa ana sekmelere geç
            self.login_success_callback()
        else:
            # Yanlışsa hata diyaloğu aç
            MDDialog(
                title="Hatalı Giriş",
                text="Kullanıcı adı veya şifre yanlış.",
                size_hint=(0.8, 0.3)
            ).open()
