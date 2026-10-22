# Halüsinasyon ve Hata Analiz Günlüğü (HALLUCINATIONS.md)

Bu belge, YZM301 Teardown Sprint kapsamında yapay zeka ajanının modelleme ve tersine mühendislik sürecinde ürettiği asılsız varsayımları (halüsinasyonları), bunların nasıl tespit edildiğini ve hangi diferansiyel testlerin bu hataları yakaladığını belgeler.

---

## Halüsinasyon 1: İki Yönlü Testte Negatif Kuyruğun İhmal Edilmesi

### Ajanın İlk İddiası / Varsayımı
Ajan, bağımsız iki grup t-testinde iki yönlü (Two-tailed) güç hesaplanırken pozitif etki büyüklüğü ($d > 0$) durumunda sol kuyruk integralinin ($F(-t_{crit}; df, \delta)$) sıfıra çok yakın olduğunu ve hesaplama maliyetinden kaçınmak için yalnızca sağ kuyruğun ($1 - F(t_{crit}; df, \delta)$) alınmasının yeterli olduğunu ileri sürdü.

### Gerçek Davranış (G*Power Davranışı)
G*Power 3.1.9.7 matematik motoru, iki yönlü testlerde noncentral t kümülatif dağılım fonksiyonunun (NCT CDF) her iki kuyruğunu da tam olarak hesaplamaktadır:
$$\text{Power} = 1 - F(t_{crit}; df, \delta) + F(-t_{crit}; df, \delta)$$
Özellikle küçük etki boyutlarında ($d \le 0.20$) veya düşük hedef güç durumlarında sol kuyruk $10^{-4}$ ile $10^{-5}$ düzeyinde katkı sağlamaktadır. Bu terim ihmal edildiğinde G*Power'ın ekranda gösterdiği 4. ondalık basamak ile CLI çıktısı arasında uyuşmazlık çıkmıştır.

### Nasıl Fark Edildi ve Hangi Test Yakaladı?
- **Yakalanan Test:** `tests/test_oracle.py::test_vector_4` ve `tests/test_edge_cases.py::test_small_effect_size`
- **Fark:** V4 senaryosunda ($d=0.20, \alpha=0.01$) sol kuyruk eklenmediğinde elde edilen güç `0.94998` iken G*Power protokolünde `0.95004` olarak raporlanmıştır. Sol kuyruk formüle dahil edilince tam eşleşme sağlanmıştır.

---

## Halüsinasyon 2: Asimetrik Gruplarda Bağımsız Örneklem Yuvarlama (Ceil) Varsayımı

### Ajanın İlk İddiası / Varsayımı
Ajan, a priori örneklem büyüklüğü aramasında hedef gücü sağlayan sürekli $N_1$ ve $N_2$ değerleri bulunduktan sonra, her iki grubun birbirinden bağımsız olarak tavana yuvarlandığını iddia etti:
$$N_1 = \lceil N_1^* \rceil, \quad N_2 = \lceil N_2^* \rceil$$

### Gerçek Davranış (G*Power Davranışı)
G*Power 3.1.9.7, grup oranı $k = N_2/N_1$ kısıtını korumak için bağımsız yuvarlama yapmaz. Arama doğrudan $N_1$ tamsayısı üzerinden yürütülür. Belirlenen tamsayı $N_1$ için $N_2 = \lceil k \cdot N_1 \rceil$ (veya tam tamsayı eşleme) kuralı işletilir. Bağımsız yuvarlama yapıldığında $N_2/N_1$ oranı bozulmakta ve toplam örneklem sayısı ($N_{total}$) G*Power değerinden 1 birim farklı çıkmaktadır.

### Nasıl Fark Edildi ve Hangi Test Yakaladı?
- **Yakalanan Test:** `tests/test_oracle.py::test_vector_3` ($ratio = 2.0$) ve `tests/test_edge_cases.py::test_fractional_allocation_ratio` ($ratio = 1.5$)
- **Fark:** Kesirli oranlarda ($k=1.5$), analitik sürekli çözümün bağımsız yuvarlanması $N_1=35, N_2=52 \rightarrow N=87$ verirken, G*Power kesikli aramasında tamsayı adımında $N_1=35 \rightarrow N_2=53 \rightarrow N=88$ üretildiği gözlenmiştir.

---

## Halüsinasyon 3: Serbestlik Derecesinin (df) Sürekli Değişken Kabul Edilmesi

### Ajanın İlk İddiası / Varsayımı
Ajan, SciPy'ın `scipy.optimize.brentq` kök bulucusunu kullanarak $N$ değerini gerçel bir sayı olarak aramayı ve serbestlik derecesini sürekli bir parametre ($df = N_1 + N_2 - 2$) olarak NCT fonksiyonuna vermeyi önerdi.

### Gerçek Davranış (G*Power Davranışı)
G*Power, kullanıcıya hiçbir zaman kesirli $df$ veya kesirli örneklem göstermez. Analitik bir normal yaklaşım tahmininin ardından tamsayı ızgarası üzerinde doğrudan tamsayı $df$'ler ile gücü hesaplar ve gücün $\ge 1-\beta$ olduğu en küçük tamsayı çiftini döndürür. Sürekli kök bulucu ile bulunan kesirli $N$'in doğrudan yuvarlanması, bazı sınır noktalarda 1 eksik örneklemle durma hatasına yol açmıştır.

### Nasıl Fark Edildi ve Hangi Test Yakaladı?
- **Yakalanan Test:** `tests/test_scale.py::test_scale_against_statsmodels_discrepancy`
- **Fark:** Statsmodels ve R'ın `pwr.t2n.test` fonksiyonlarının kesirli $N$ verip yukarı yuvarlandığında bazı sınırlarda G*Power'dan farklı tamsayı vermesiyle kanıtlandı.
