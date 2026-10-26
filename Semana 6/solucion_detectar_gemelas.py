def detectar_gemelas(redes):
    """redes: lista de dicts {'ssid','bssid','seguridad'}. Devuelve {ssid: [bssid,...]} de SSID sospechosos
    (mismo SSID anunciado por más de un BSSID con seguridad distinta)."""
    grupos = {}
    for r in redes:
        grupos.setdefault(r["ssid"], []).append(r)
    sospechosos = {}
    for ssid, lista in grupos.items():
        if len({r["seguridad"] for r in lista}) > 1:
            sospechosos[ssid] = sorted(r["bssid"] for r in lista)
    return sospechosos

if __name__ == "__main__":
    redes = [
        {"ssid": "CafeNova_Gratis", "bssid": "aa:bb:cc:00:00:01", "seguridad": "WPA2"},
        {"ssid": "CafeNova_Gratis", "bssid": "de:ad:be:ef:00:66", "seguridad": "ABIERTA"},
        {"ssid": "Libreria_WiFi", "bssid": "aa:bb:cc:00:00:02", "seguridad": "WPA2"},
        {"ssid": "Libreria_WiFi", "bssid": "aa:bb:cc:00:00:12", "seguridad": "WPA2"},  # repetidor legítimo
    ]
    print(detectar_gemelas(redes))
    assert detectar_gemelas(redes) == {"CafeNova_Gratis": ["aa:bb:cc:00:00:01", "de:ad:be:ef:00:66"]}
    assert detectar_gemelas([]) == {}
    print("OK")
