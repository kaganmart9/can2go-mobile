import threading
import time
import random

class DummyBluetoothSimulator:
    def __init__(self):
        self._running = False
        self._subscribers = []

    def start(self):
        self._running = True
        threading.Thread(target=self._simulate_data, daemon=True).start()

    def stop(self):
        self._running = False

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def _simulate_data(self):
        error_ids = [145, 146, 147, 148, 149, 150, 151, 152]

        while self._running:
            # %50 ihtimalle geçerli bir error_id gönderiyoruz
            if random.random() < 0.5:
                first_byte = random.choice(error_ids)
            else:
                first_byte = random.randint(0, 255)

            fake_data = bytes([first_byte] + [random.randint(0, 255) for _ in range(7)])

            for callback in self._subscribers:
                callback(fake_data)

            time.sleep(1)
