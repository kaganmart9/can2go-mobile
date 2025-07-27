# utils/parser.py

def parse_error(data: bytes):
    """
    Prototip aşamasında, gelen her veri paketi için hata olarak değerlendirin.
    data[0]: hata ID
    data[1]: hata kodu
    """
    error_id = data[0]
    error_code = data[1]
    # Önceden tanımlı hatalar (ileride detaylandırılacak)
    error_definitions = {
        145: "Cell Overvoltage",
        146: "Cell Undervoltage",
        147: "Over Temperature",
        148: "Under Temperature",
        149: "Charge Overcurrent",
        150: "Discharge Overcurrent",
        151: "BMS Communication Lost",
        152: "Battery Pack Unbalanced",
    }
    if error_id in error_definitions:
        return {
            "error_message": error_definitions[error_id],
            "error_code": error_code
        }
    # Prototip: bilinmeyen bir hata ID’si de prototip mesaj olarak göster
    return {
        "error_message": f"Unknown Error ID {error_id}",
        "error_code": error_code
    }

def parse_metrics(data: bytes):
    """
    Dummy veri üzerinden metrik üretimi (real-time parser bu fonksiyonu değiştirecek).
    """
    soc = data[0] * 100 // 255  # 0-100
    soh = data[1] * 100 // 255
    voltage = (data[2] << 8 | data[3]) / 100.0  # 0-65535 -> 0-655.35 V
    temp = data[4] - 40  # 0-255 -> -40 to +215°C

    return {
        "soc": soc,
        "soh": soh,
        "voltage": voltage,
        "temperature": temp
    }
