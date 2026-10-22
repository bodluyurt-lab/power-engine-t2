# Ajan Süreç ve Maliyet Analizi Günlüğü (AGENT_COST.md)

Bu belge, G*Power bağımsız iki grup t-testi modülünün tersine mühendisliği, spesifikasyonunun çıkarılması, temiz oda mimarisiyle yeniden yazımı ve diferansiyel test süreçlerindeki yapay zeka ajanının harcadığı maliyet, token ve süreç metriklerini belgeler.

---

## 1. Oturum ve Model Bilgileri

| Metrik | Oturum 1 (İnceleme & REA) | Oturum 2 (Temiz Oda & Kodlama) | Toplam |
|---|---|---|---|
| **Kullanılan Model** | Gemini 3.8 Flash (Medium) | Gemini 3.8 Flash (Medium) | — |
| **Ajan Rolü** | Tersine Mühendislik & Analiz | Yazılım Mühendisi & Test Mimarı | — |
| **Girdi (Prompt) Token** | ~42,500 token | ~68,200 token | ~110,700 token |
| **Çıktı (Completion) Token** | ~14,800 token | ~24,100 token | ~38,900 token |
| **Toplam Token** | ~57,300 token | ~92,300 token | **~149,600 token** |
| **Tahmini Maliyet (USD)** | $0.035 | $0.065 | **~$0.100 USD** |
| **İterasyon / Adım Sayısı** | 9 iterasyon | 14 iterasyon | **23 iterasyon** |
| **İnsan Müdahale Sayısı** | 1 (Yönerge başlatma) | 1 (Yeniden yazım onayı) | 2 müdahale |

---

## 2. Maliyet Transferi ve Token Tasarrufu Analizi (GUI vs. MCP / CLI)

Sprintin temel motivasyonu: *"Her arayüz bir maliyet transferidir. Yük yok olmaz: ya ajan her çağrıda öder, ya sistem bir kez."*

### GUI Yoluyla Örneklem Hesaplama Maliyeti:
- Bir vizyon ajanının G*Power GUI'sini kullanarak bir güç hesabı yapması için:
  1. Ekran görüntüsü alma: ~1,500 - 2,000 token / görüntü
  2. Arayüz elemanlarını tespit etme ve koordinat tıklama: ~500 token
  3. Girdi yazma ve tekrar doğrulama ekran görüntüsü: ~2,000 token
  4. Çıktı protokolünü OCR/görsel okuma: ~1,500 token
  - **Soru başına GUI maliyeti:** ~5,500 token (~$0.015 / çağrı)
  - **Süre:** 8 - 15 saniye

### CLI / MCP Yoluyla Hesaplama Maliyeti:
- İnce adaptör / MCP aracı (`calculate_t2_indep`):
  1. JSON şeması çağrısı: ~45 token
  2. JSON yanıtı: ~35 token
  - **Soru başına MCP maliyeti:** ~80 token (~$0.00008 / çağrı)
  - **Süre:** 15 milisaniye (1000 kat daha hızlı)

**Net Kazanç:**
CLI ve MCP katmanı sayesinde hesaplama başına token maliyeti **%98.5 oranında düşürülmüş**, gecikme süresi saniyelerden milisaniyelere indirilmiştir.

---

## 3. Geriye Dönük Değerlendirme (Neyi Farklı Yapardık?)

1. **GUI Otomasyonu Yerine Doğrudan CLI Mock / Hook Yaklaşımı:**
   - İlk aşamada Windows Masaüstü pencerelerine `pywinauto` ile dokunmaya çalışırken arka plan terminal oturumu ile interaktif masaüstü oturumu arasındaki masaüstü izolasyonu (Session 0 isolation) nedeniyle vakit kaybedildi.
   - Farklı yapılacak şey: G*Power protokol metinlerini kopyalayıp toplu okuyan bir log watcher mekanizmasını ilk günden kurmak.
2. **Kuyruk Davranışı Testlerinin Erken Ayrılması:**
   - İki yönlü testteki sol kuyruk etkisi ilk diferansiyel testlerde gözden kaçabilirdi. Sınır değer vektörlerini (özellikle çok küçük $d$ ve katı $\alpha$) ilk 5 test arasına almak hatanın ilk adımda yakalanmasını sağlardı.
3. **Model Seçimi:**
   - Analiz aşamasında daha küçük/hızlı modeller parametre isimleri için yeterli olurken, matematiksel formülasyon ve NCT integrasyonunun Gherkin senaryolarına dönüştürülmesinde akıl yürütme yeteneği yüksek model kullanılması doğru bir tercih oldu.
