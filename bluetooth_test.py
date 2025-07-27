import os  # Dosya yolları için işletim sistemi modülü
import sys  # Sistem yolunu güncellemek için
# Proje kök dizinini ve utils klasörünü modüle dahil et
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

import asyncio  # Asenkron işlemler için
from utils.bluetooth_manager import BluetoothManager  # BLE yöneticisi

def on_data(data: bytearray):
    # ESP32'den gelen ham veriyi hex formatında yazdır
    print(f"📥 ESP32'den Alınan Veri: {data.hex()}")

async def main():
    # Bağlanılacak ESP32 cihazının BLE adresi
    address = "A8:42:E3:AB:6D:AA"
    # BLE karakteristik UUID (Arduino sketch ile eşleşmeli)
    characteristic_uuid = "abcd1234-5678-90ab-cdef-1234567890ab"

    manager = BluetoothManager()  # BLE yöneticisini başlat
    await manager.connect_and_listen_fixed_address(
        address,
        characteristic_uuid,
        on_data  # Bağlantı sonrası gelen veriler bu fonksiyona iletilecek
    )

    # Script'in çalışmasını sürdürmek için sonsuz döngü
    print("⏳ Dinleme devam ediyor... Çıkmak için Ctrl+C")
    while True:
        await asyncio.sleep(1)  # 1 saniye bekle ve döngüyü tekrarla

if __name__ == "__main__":
    try:
        # Ana asenkron fonksiyonu çalıştır
        asyncio.run(main())
    except KeyboardInterrupt:
        # Kullanıcı tarafından durdurulduğunda bilgilendirme
        print("\n🔌 Dinleme sonlandırıldı.")
