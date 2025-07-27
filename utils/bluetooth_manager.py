# utils/bluetooth_manager.py

import asyncio
from bleak import BleakClient

class BluetoothManager:
    def __init__(self):
        self.client = None
        self.connected = False
        self.notify_callback = None

    async def connect_and_listen_fixed_address(self, address, characteristic_uuid, notify_callback):
        """
        Belirli bir Bluetooth adresine bağlanır ve karakteristik UUID'den veri dinler.
        """
        self.notify_callback = notify_callback
        self.client = BleakClient(address)

        try:
            await self.client.connect()
            self.connected = await self.client.is_connected()
            print(f"✅ Bağlantı durumu: {self.connected}")

            # notify başlat
            await self.client.start_notify(characteristic_uuid, self._notification_handler)
            print(f"🔔 Dinlemeye başlandı: {characteristic_uuid}")

        except Exception as e:
            print(f"⚠️ Bağlantı hatası: {e}")
            self.connected = False

    async def disconnect(self):
        if self.client and self.connected:
            await self.client.disconnect()
            self.connected = False
            print("🔌 Bağlantı sonlandırıldı.")

    def _notification_handler(self, sender, data: bytearray):
        print(f"📥 Veri alındı ({sender}): {data.hex()}")
        if self.notify_callback:
            self.notify_callback(bytes(data))
