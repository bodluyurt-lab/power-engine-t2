# G*Power Bağımsız İki Grup t-Testi Kabul Şartnamesi (SPEC.md)

Bu şartname, G*Power 3.1.9.7 `t2-indep` ailesi için temiz oda yeniden yazım gereksinimlerini ve Gherkin formatındaki kabul kriterlerini tanımlar.

---

## 1. Kapsam ve İstatistiksel Tanımlar
* **Test Ailesi:** `t tests`
* **İstatistiksel Test:** `Means: Difference between two independent means (two groups)`
* **Analiz Modları:**
  - `a-priori`: Hedeflenen güç ($1-\beta$), etki boyutu ($d$), alfa ($\alpha$) ve grup oranı ($N_2/N_1$) verildiğinde gereken minimum tamsayı $N_1, N_2$ ve toplam $N$ değerlerinin bulunması.
  - `post-hoc`: Verilen $N_1, N_2$, etki boyutu ($d$) ve alfa ($\alpha$) ile elde edilen istatistiksel gücün hesaplanması.

---

## 2. CLI ve API Sözleşmesi

### 2.1. CLI Komut Formatı
```bash
gpower-clone --test t2-indep --mode <a-priori|post-hoc> [PARAMETRELER]
```

### 2.2. Beklenen Çıktı Biçimi (Tek Satır JSON)
* **A priori Başarılı:**
  ```json
  {"n1":105,"n2":105,"n_total":210,"actual_power":0.9501,"critical":1.9714,"df":208,"ncp":3.6228}
  ```
* **Post hoc Başarılı:**
  ```json
  {"actual_power":0.8015,"critical":1.9790,"df":126,"ncp":2.8284}
  ```
* **Hatalı Girdi:**
  ```json
  {"error":"<hata_mesaji>"}
  ```
  *(Çıkış kodu sıfırdan farklı olmalıdır: Exit Code != 0)*

---

## 3. Kabul Kriterleri (Gherkin Formatında)

```gherkin
Feature: Bağımsız İki Grup t-Testi Güç ve Örneklem Büyüklüğü Analizi

  Background:
    Given G*Power clone hesaplama motoru başlatılmıştır
    And Test ailesi "t2-indep" olarak seçilmiştir

  Scenario: A priori dengeli iki yönlü analiz (Standart Referans - V1)
    Given Analiz modu "a-priori" olarak belirlenmiştir
    And Kuyruk yönü "Two" (tails = 2) olarak ayarlanmıştır
    And Cohen's d etki büyüklüğü 0.50 olarak girilmiştir
    And Tip I hata payı alpha 0.05 olarak girilmiştir
    And Hedef güç 0.80 olarak girilmiştir
    And Grup büyüklüğü oranı ratio 1.0 olarak girilmiştir
    When Örneklem hesaplama motoru çalıştırıldığında
    Then 1. grup örneklemi n1 tam olarak 64 olmalıdır
    And 2. grup örneklemi n2 tam olarak 64 olmalıdır
    And Toplam örneklem n_total tam olarak 128 olmalıdır
    And Serbestlik derecesi df tam olarak 126 olmalıdır
    And Gerçekleşen güç actual_power en az 0.8014 olmalıdır
    And Kritik t değeri critical 1.9790 (±0.001) olmalıdır

  Scenario: A priori tek yönlü analiz (Kuyruk Dönüşümü - V2)
    Given Analiz modu "a-priori" olarak belirlenmiştir
    And Kuyruk yönü "One" (tails = 1) olarak ayarlanmıştır
    And Cohen's d etki büyüklüğü 0.50 olarak girilmiştir
    And Tip I hata payı alpha 0.05 olarak girilmiştir
    And Hedef güç 0.80 olarak girilmiştir
    And Grup büyüklüğü oranı ratio 1.0 olarak girilmiştir
    When Örneklem hesaplama motoru çalıştırıldığında
    Then 1. grup örneklemi n1 tam olarak 51 olmalıdır
    And 2. grup örneklemi n2 tam olarak 51 olmalıdır
    And Toplam örneklem n_total tam olarak 102 olmalıdır
    And Serbestlik derecesi df tam olarak 100 olmalıdır
    And Gerçekleşen güç actual_power en az 0.8058 olmalıdır
    And Kritik t değeri critical 1.6602 (±0.001) olmalıdır

  Scenario: A priori asimetrik grup dağılımı (N2 = 2 * N1 - V3)
    Given Analiz modu "a-priori" olarak belirlenmiştir
    And Kuyruk yönü "Two" (tails = 2) olarak ayarlanmıştır
    And Cohen's d etki büyüklüğü 0.50 olarak girilmiştir
    And Tip I hata payı alpha 0.05 olarak girilmiştir
    And Hedef güç 0.80 olarak girilmiştir
    And Grup büyüklüğü oranı ratio 2.0 olarak girilmiştir
    When Örneklem hesaplama motoru çalıştırıldığında
    Then 1. grup örneklemi n1 tam olarak 48 olmalıdır
    And 2. grup örneklemi n2 tam olarak 96 olmalıdır
    And Toplam örneklem n_total tam olarak 144 olmalıdır
    And Serbestlik derecesi df tam olarak 142 olmalıdır
    And Gerçekleşen güç actual_power en az 0.8021 olmalıdır

  Scenario: Post hoc gerçekleşen güç analizi
    Given Analiz modu "post-hoc" olarak belirlenmiştir
    And Kuyruk yönü "Two" (tails = 2) olarak ayarlanmıştır
    And Cohen's d etki büyüklüğü 0.50 olarak girilmiştir
    And Tip I hata payı alpha 0.05 olarak girilmiştir
    And 1. grup örneklemi n1 64 olarak girilmiştir
    And 2. grup örneklemi n2 64 olarak girilmiştir
    When Güç hesaplama motoru çalıştırıldığında
    Then Serbestlik derecesi df 126 olmalıdır
    And Gerçekleşen güç actual_power 0.8015 (±0.0005) olmalıdır
    And Noncentrality parametresi ncp 2.8284 (±0.0005) olmalıdır

  Scenario Outline: Geçersiz giriş parametrelerinde hata yönetimi
    Given Parametreler tails=<tails>, d=<d>, alpha=<alpha>, power=<power> girilmiştir
    When CLI çalıştırıldığında
    Then Çıkış kodu sıfırdan farklı olmalıdır (exit code != 0)
    And Çıktı '{"error":"..."}' biçiminde tek satır JSON olmalıdır

    Examples:
      | tails | d    | alpha | power |
      | 3     | 0.50 | 0.05  | 0.80  |
      | 2     | -0.5 | 0.05  | 0.80  |
      | 2     | 0.50 | 0.00  | 0.80  |
      | 2     | 0.50 | 1.05  | 0.80  |
      | 2     | 0.50 | 0.05  | 1.00  |
```
