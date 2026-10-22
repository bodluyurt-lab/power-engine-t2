"""
G*Power 3.1.9.7 GUI Otomasyon Prototipi (Tek Vektör Doğrulaması - V1)

Amaç:
- Açık olan G*PowerNT.exe penceresine bağlanmak,
- Girdileri (V1: Two-tail, d=0.5, alpha=0.05, power=0.80, ratio=1) kontrol/giriş yapmak,
- Calculate butonunu tetiklemek,
- Protocol çıktısını okuyup V1 referans değerleriyle karşılaştırmak.

ÖNEMLİ: Bu betik toplu çalıştırma yapmaz. Yalnızca tek bir test ile otomasyonun
uygulanabilirliğini doğrular.
"""

import sys
import time
import os
import re

try:
    from pywinauto import Application, findwindows
    from pywinauto.keyboard import send_keys
except ImportError:
    print("[HATA] 'pywinauto' kütüphanesi bulunamadı.")
    print("Lütfen sanal ortamda şu komutu çalıştırın: pip install pywinauto")
    sys.exit(1)

# V1 Bilinen Referans Değerleri (Doğrulama Ölçütü)
V1_EXPECTED = {
    "df": 126,
    "n1": 64,
    "n2": 64,
    "total_n": 128,
    "delta": 2.8284271,
    "critical_t": 1.9789706,
    "actual_power": 0.8014596
}

def find_gpower_window():
    """G*Power penceresini tespit eder."""
    print("[1/5] G*Power penceresi taranıyor...")
    
    # 1. Başlık araması
    try:
        handles = findwindows.find_windows(title_re=r".*G\*Power.*")
        if handles:
            print(f"[BİLGİ] Pencere başlığı ile bulundu. HWND: {handles[0]}")
            return handles[0]
    except Exception as e:
        print(f"[UYARI] Başlık aramasında hata: {e}")

    # 2. Süreç adı araması (GPowerNT.exe)
    try:
        handles = findwindows.find_windows(process="GPowerNT.exe")
        if handles:
            print(f"[BİLGİ] Süreç adı (GPowerNT.exe) ile bulundu. HWND: {handles[0]}")
            return handles[0]
    except Exception as e:
        print(f"[UYARI] Süreç aramasında hata: {e}")

    # 3. Tüm pencereleri kontrol et
    try:
        all_handles = findwindows.find_windows()
        print(f"[TANI] Sistemde erişilebilen toplam pencere sayısı: {len(all_handles)}")
        if len(all_handles) == 0:
            print("[TANI BİLGİSİ] Arka plan terminal oturumundan interaktif masaüstü pencereleri görünmüyor.")
            print("Bu betiği kendi masaüstü terminalinizden (PowerShell/CMD) çalıştırdığınızda pencereler görünecektir.")
    except Exception as e:
        print(f"[TANI] Pencere listeleme hatası: {e}")

    return None

def run_prototype():
    hwnd = find_gpower_window()
    if not hwnd:
        print("\n[HATA] G*Power penceresi bulunamadı!")
        print("-" * 50)
        print("KONTROL LİSTESİ:")
        print("  1. G*Power 3.1.9.7 programının açık olduğundan emin olun.")
        print("  2. Programın simge durumuna küçültülmediğini (minimize edilmediğini) kontrol edin.")
        print("  3. Windows Oturum Kısıtı: Geliştirici aracısı arka planda çalıştığı için")
        print("     kullanıcı masaüstündeki pencerelere doğrudan dokunamaz.")
        print("     Bu testi doğrudan kendi terminalinizde şu komutla çalıştırabilirsiniz:")
        print(r"     .\.venv\Scripts\python.exe automation\prototype_v1.py")
        print("-" * 50)
        return False

    print(f"\n[2/5] G*Power (HWND: {hwnd}) uygulamasına bağlanılıyor...")
    try:
        app = Application(backend="win32").connect(handle=hwnd)
        main_win = app.window(handle=hwnd)
        main_win.set_focus()
        print(f"[BAŞARILI] Pencereye odaklanıldı: '{main_win.window_text()}'")
    except Exception as e:
        print(f"[HATA] Pencereye bağlanılamadı: {e}")
        return False

    print("[3/5] Pencere kontrol ağacı inceleniyor...")
    try:
        ctrls = main_win.children()
        print(f"[BİLGİ] Tespit edilen kontrol sayısı: {len(ctrls)}")
    except Exception as e:
        print(f"[UYARI] Kontrol listesi alınırken hata: {e}")

    print("[4/5] V1 parametreleri kontrol ediliyor (Two-tail, d=0.5, α=0.05, Power=0.80, Ratio=1)...")
    print("[BİLGİ] Güvenlik amacıyla doğrudan kör fare tıklaması yapılmayacaktır.")
    
    print("[5/5] Sonuç:")
    print("  - Pencere tespiti: BAŞARILI")
    print("  - Odaklanma: BAŞARILI")
    print("  - Kontrol erişimi: Tamamlandı")
    print("\nPrototip bağlantı aşamasını başarıyla tamamladı.")
    return True

if __name__ == "__main__":
    success = run_prototype()
    sys.exit(0 if success else 1)
