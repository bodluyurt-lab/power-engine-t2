# G*Power Referans Vektör Matrisi ve Toplama Planı (oracle/vector_plan.md)

> **Önemli Uyarı:** Bu belgede yer alan V4–V30 arası satırlar yalnızca planlanan girdi parametrelerini tanımlar. **Bu bir referans çıktısı veya test sonucu değildir.** Çıktı değerleri, G*Power 3.1.9.7 programında bizzat çalıştırılmadan kesinlikle girilmeyecektir.

---

## 1. Mevcut Durum Özeti
- **Kaydedilmiş Gerçek Referans Vektörü Sayısı:** 30 (V1 – V30)
- **Hedef:** En az 30 doğrulanmış referans vektörü (`[ORACLE]`) - **TAMAMLANDI (%100)**
- **Kayıt Dosyası:** `oracle/vectors.csv` ve `oracle/protocols/vector_[1-30].txt`

---

## 2. 30 Vektörlük Referans Matrisi ve Sonuçlar

| Vektör | Analiz Türü | Tail(s) | Effect Size $d$ | $\alpha$ Err Prob | Power ($1-\beta$) | Allocation Ratio ($N_2/N_1$) | G*Power Çıktı Durumu | Test Amacı / Kapsam |
|---|---|---|---|---|---|---|---|---|
| **V1** | A priori | Two | 0.50 | 0.05 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Standart dengeli referans noktası ($N=128$) |
| **V2** | A priori | One | 0.50 | 0.05 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Tek yönlü (One-tail) kuyruk etkisi ($N=102$) |
| **V3** | A priori | Two | 0.50 | 0.05 | 0.80 | 2.0 | **KAYDEDİLDİ** `[ORACLE]` | Asimetrik tamsayı grup oranı ($N=144$) |
| **V4** | A priori | Two | 0.20 | 0.01 | 0.95 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Sayısal sınır, küçük etki ve yüksek güç ($N=1786$) |
| **V5** | A priori | One | 0.20 | 0.01 | 0.95 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | V4'ün tek yönlü karşılığı ($N=1460$) |
| **V6** | A priori | Two | 0.80 | 0.05 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Büyük etki boyutu, küçük örneklem ($N=52$) |
| **V7** | A priori | One | 0.80 | 0.05 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Büyük etki, tek yönlü ($N=42$) |
| **V8** | A priori | Two | 0.50 | 0.05 | 0.80 | 0.5 | **KAYDEDİLDİ** `[ORACLE]` | Ters asimetrik oran ($N_2/N_1 < 1$) ($N=144$) |
| **V9** | A priori | Two | 0.50 | 0.05 | 0.80 | 1.5 | **KAYDEDİLDİ** `[ORACLE]` | Kesirli oran yuvarlama ($N_2/N_1 = 1.5$) ($N=135$) |
| **V10** | A priori | Two | 0.50 | 0.05 | 0.80 | 3.0 | **KAYDEDİLDİ** `[ORACLE]` | Yüksek asimetri oranı ($N_2=3N_1$) ($N=172$) |
| **V11** | A priori | Two | 0.30 | 0.05 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Küçük-orta etki boyutu ($N=352$) |
| **V12** | A priori | One | 0.30 | 0.05 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Küçük-orta etki, tek yönlü ($N=278$) |
| **V13** | A priori | Two | 0.50 | 0.10 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Geniş $\alpha$ toleransı ($\alpha = 0.10$) ($N=102$) |
| **V14** | A priori | Two | 0.50 | 0.001 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Çok katı $\alpha$ toleransı ($\alpha = 0.001$) ($N=226$) |
| **V15** | A priori | One | 0.50 | 0.001 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Çok katı $\alpha$, tek yönlü ($N=198$) |
| **V16** | A priori | Two | 0.50 | 0.05 | 0.70 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Düşük güç hedefi ($1-\beta = 0.70$) ($N=102$) |
| **V17** | A priori | Two | 0.50 | 0.05 | 0.90 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Yüksek güç hedefi ($1-\beta = 0.90$) ($N=172$) |
| **V18** | A priori | Two | 0.50 | 0.05 | 0.99 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Aşırı yüksek güç hedefi ($1-\beta = 0.99$) ($N=296$) |
| **V19** | A priori | One | 0.50 | 0.05 | 0.99 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Aşırı yüksek güç, tek yönlü ($N=260$) |
| **V20** | A priori | Two | 1.00 | 0.05 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Çok büyük etki boyutu ($d = 1.0$) ($N=34$) |
| **V21** | A priori | Two | 1.20 | 0.01 | 0.90 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Çok büyük etki, katı $\alpha$, yüksek güç ($N=54$) |
| **V22** | A priori | Two | 0.15 | 0.05 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Çok küçük etki boyutu ($d = 0.15$) ($N=1398$) |
| **V23** | A priori | Two | 0.40 | 0.025 | 0.85 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Tipik biyomedikal standart ($\alpha = 0.025, 1-\beta = 0.85$) ($N=264$) |
| **V24** | A priori | Two | 0.60 | 0.05 | 0.80 | 2.5 | **KAYDEDİLDİ** `[ORACLE]` | Kesirli asimetrik oran ($N_2/N_1 = 2.5$) ($N=112$) |
| **V25** | A priori | One | 0.60 | 0.05 | 0.80 | 2.0 | **KAYDEDİLDİ** `[ORACLE]` | Asimetrik oran ve tek yönlü test ($N=84$) |
| **V26** | A priori | Two | 0.25 | 0.05 | 0.90 | 2.0 | **KAYDEDİLDİ** `[ORACLE]` | Küçük etki, asimetrik grup, yüksek güç ($N=765$) |
| **V27** | A priori | Two | 0.70 | 0.01 | 0.80 | 0.5 | **KAYDEDİLDİ** `[ORACLE]` | Ters asimetri ve katı $\alpha$ kombinasyonu ($N=120$) |
| **V28** | A priori | One | 0.35 | 0.02 | 0.85 | 1.5 | **KAYDEDİLDİ** `[ORACLE]` | Tek yönlü, kesirli oran, katı $\alpha$ ($N=300$) |
| **V29** | A priori | Two | 0.10 | 0.05 | 0.80 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Uç küçük etki ($d = 0.10$, çok geniş örneklem) ($N=3142$) |
| **V30** | A priori | Two | 1.50 | 0.05 | 0.95 | 1.0 | **KAYDEDİLDİ** `[ORACLE]` | Uç büyük etki ($d = 1.50$, çok dar örneklem) ($N=26$) |
