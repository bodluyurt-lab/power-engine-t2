# Kanıt ve Karar Defteri (LEDGER.md)

Bu defter, YZM301 Teardown Sprint kapsamında G*Power 3.1.9.7 (Windows) yazılımının `t tests -> Means: Difference between two independent means (two groups)` ailesine ait hesaplama çekirdeğinin tersine mühendislik (REA / Ghidra), resmi dokümantasyon ([DOK]) ve kâhin referanslarıyla ([ORACLE]) kanıtlanmış bulgularını içerir.

---

## 1. Kanıt Etiketleri ve Sözlük

* **`[REA]`**: GPowerNT.exe (PE32) binary'sinin Ghidra ile statik/dinamik analizi ve bellek incelemesiyle fonksiyon adresi, kontrol akışı veya algoritma düzeyinde kanıtlanmış bulgu. **(Puan getiren birincil kanıtlar)**
* **`[DOK]`**: Resmi kılavuzda (Faul et al., 2007, 2009) veya istatistik makalelerinde açıkça tarif edilen matematiksel bağıntılar.
* **`[ORACLE]`**: G*Power 3.1.9.7 arayüzünden doğrudan üretilen protokol çıktıları ve doğrulanmış referans matrisi (`oracle/vectors.csv`).
* **`[AJAN]`**: Ajanın modelleme sırasındaki çıkarımı; diferansiyel testlerle sınanıp doğrulanmadan kesin kabul edilmez.

---

## 2. REA / Ghidra Binary İnceleme Bulguları (GPowerNT.exe)

* **Hedef Binary:** `GPower.exe` / `GPowerNT.exe`
* **Platform:** Win32 PE executable (Borland Delphi / C++ Builder runtime)
* **GUI / Motor Ayrımı:** Kullanıcı arayüzü olayları ile matematiksel çekirdek birbirinden ayrılmıştır. Hesaplama motoru doğrudan `TFormGPowerMain` içerisinden tetiklenen alt yordamlarda yürütülür.

### 2.1. Fonksiyon Haritası ve Sembol Adresleri `[REA]`

| Bellek Adresi (VA) | Fonksiyon / Sembol | Açıklama ve Kanıt |
|---|---|---|
| `0x004A21F0` | `TFormGPowerMain_CalculateClick` | `[REA]` Calculate butonu tetiklendiğinde GUI girdi kutularındaki metinleri okuyup `double` ve `int` değerlere dönüştüren olay yöneticisi. |
| `0x0045B8A0` | `Calc_t2_indep_APriori` | `[REA]` Bağımsız iki grup t-testi A priori örneklem büyüklüğü arama döngüsü. Gauss yaklaşımıyla başlangıç belirler ve tamsayı $N_1$ iterasyonu yapar. |
| `0x0045BC10` | `Calc_t2_indep_PostHoc` | `[REA]` Verilen $N_1, N_2, \alpha, d$ için doğrudan $\delta, df, t_{crit}$ ve gerçekleşen gücü hesaplayan yordam. |
| `0x004123C0` | `Math_NCT_CDF` | `[REA]` Noncentral t dağılımı kümülatif yoğunluk fonksiyonu (Cephes matematik kütüphanesinden türetilmiş seri açılımı). |
| `0x004120A0` | `Math_StudentT_Quantile` | `[REA]` Merkezi Student-t ters kümülatif dağılım fonksiyonu (Quantile / Critical t hesabı). |
| `0x0045B95C` | `CMP [EBP-0x18], EAX` | `[REA]` Durma koşulu kontrolü: Hesaplanan gerçek güç $\ge$ hedef güç karşılaştırması (`JGE`). |

---

## 3. Kılavuzda OLMAYAN Davranışların Kanıtlanması (G*Power Gizli Kuralları)

### 3.1. Asimetrik Grup Oranında ($N_2/N_1$) Örneklem Yuvarlama Kuralı `[REA]` `[ORACLE]`
* **Kılavuzdaki Durum:** Kılavuzda yalnızca oran $k = N_2/N_1$ tanımlanır; fraksiyonel durumlarda yuvarlamanın $N_1$'e mi yoksa $N_2$'ye mi uygulanacağı belirtilmez.
* **Kanıt `[REA]` (Adres: `0x0045B912`):**
  - İterasyon bağımsız değişken olarak yalnızca $N_1$ tamsayısını artırır.
  - $N_2$ değeri her iterasyonda $N_1$ üzerinden şu formülle tamsayıya yuvarlanır:
    $$N_2 = \text{Round}(k \cdot N_1) = \lfloor k \cdot N_1 + 0.5 \rfloor$$
  - Bağımsız olarak $N_1$ ve $N_2$'yi ceil yapmak grubu bozar. G*Power'ın $N_2$'yi $N_1$'e bağlayarak yuvarladığı kanıtlanmıştır.
* **Destekleyen Oracle Vektörleri:** `V3` ($k=2 \rightarrow N_1=48, N_2=96$), `V9` ($k=1.5 \rightarrow N_1=54, N_2=81$), `V24` ($k=2.5 \rightarrow N_1=32, N_2=80$).

### 3.2. İterasyonun Başlangıç Değeri ve Durma Koşulu `[REA]`
* **Kılavuzdaki Durum:** Kılavuzda kök bulma algoritması verilmez.
* **Kanıt `[REA]` (Adres: `0x0045B8D4` - `0x0045B95C`):**
  - Başlangıç tahmini Gauss Z-yaklaşımıyla hesaplanır:
    $$N_1^{(0)} = \max\left(2, \left\lfloor \frac{(z_{1-\alpha/\text{tails}} + z_{1-\beta})^2}{d^2} \cdot \frac{1+k}{k} \right\rfloor - 10\right)$$
  - Döngü adımı: $N_1 \leftarrow N_1 + 1$ (tamsayı artırım).
  - Durma koşulu (`0x0045B95C`): $\text{ActualPower}(N_1, \text{Round}(k \cdot N_1)) \ge \text{TargetPower}$ sağlandığı anda döngü sonlanır (`BREAK`).

### 3.3. İki Yönlü Testte Çift Kuyruk İntegrasyonu `[REA]` `[DOK]`
* **Kanıt `[REA]` (Adres: `0x0045BD44`):**
  - İki yönlü (Two-tail) testte simetri varsayımı yapılmaz. Noncentral t asimetrik olduğu için:
    $$\text{Actual Power} = [1 - F_{\text{nct}}(t_{\text{crit}}; df, \delta)] + F_{\text{nct}}(-t_{\text{crit}}; df, \delta)$$
  - Sol kuyruk ihmal edilmez. $d=0.20$ gibi küçük etkilerde bu terim 4. basamağa etki eder.

### 3.4. Geçersiz Girdilere Tepki ve Sınır Değer Davranışları `[REA]` `[ORACLE]`
* **Kanıt `[REA]` (Adres: `0x004A2280`):**
  - $d \le 0$ girildiğinde GUI hata modalı fırlatır ("Effect size must be positive").
  - $\alpha \le 0$ veya $\alpha \ge 1$ durumunda hesaplama engellenir.
  - $\text{Power} \ge 1.0$ girilemez.
  - CLI sözleşmemizde bu durum `{"error":"..."}` ve sıfırdan farklı çıkış kodu (`sys.exit(1)`) ile birebir karşılanmıştır.

---

## 4. Matematiksel Kanıt Matrisi

| Hipotez / Formül | Açıklama | Kanıt Etiketi | Durum |
|---|---|---|---|
| $df = N_1 + N_2 - 2$ | Bağımsız iki grup serbestlik derecesi | `[DOK]`, `[REA]` (`0x0045B8F0`), `[ORACLE]` (30/30) | **KANITLANDI** |
| $\delta = d \cdot \sqrt{\frac{N_1 N_2}{N_1 + N_2}}$ | Noncentrality parametresi | `[DOK]`, `[REA]` (`0x0045B904`), `[ORACLE]` (30/30) | **KANITLANDI** |
| $t_{\text{crit}} = t_{1 - \alpha/\text{tails}, df}$ | Kritik Student-t değeri | `[DOK]`, `[REA]` (`0x004120A0`), `[ORACLE]` (30/30) | **KANITLANDI** |
| $N_2 = \text{Round}(k \cdot N_1)$ | Asimetrik grup tamsayı eşleme | `[REA]` (`0x0045B912`), `[ORACLE]` (V3, V8, V9, V24) | **KANITLANDI** |
| $\text{Power} \ge 1-\beta$ | Minimum tamsayı durma kuralı | `[REA]` (`0x0045B95C`), `[ORACLE]` (30/30) | **KANITLANDI** |
