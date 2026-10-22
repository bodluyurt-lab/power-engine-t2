"""
G*Power 3.1.9.7 Bağımsız İki Grup t-Testi Temiz Oda Hesap Motoru (src/engine.py)

Kapsam:
- Test Ailesi: t tests
- İstatistiksel Test: Means: Difference between two independent means (two groups)
- Modlar: A priori (N hesaplama), Post hoc (Gerçekleşen güç hesaplama)

Matematiksel Model:
- Noncentral t-distribution (NCT)
- Student's t distribution kuantilleri
- Çift yönlü ve tek yönlü kuyruk integralleri
"""

import math
from typing import Dict, Any, Tuple
from scipy.stats import t as student_t, nct, norm

def validate_common_inputs(tails: int, d: float, alpha: float) -> None:
    """Ortak giriş parametrelerini doğrular."""
    if tails not in (1, 2):
        raise ValueError(f"Geçersiz kuyruk parametresi: {tails}. Tails yalnızca 1 veya 2 olabilir.")
    if d <= 0:
        raise ValueError(f"Geçersiz etki büyüklüğü: {d}. Effect size (d) pozitif bir sayı olmalıdır (> 0).")
    if not (0 < alpha < 1):
        raise ValueError(f"Geçersiz alfa düzeyi: {alpha}. Alpha hata olasılığı (0, 1) aralığında olmalıdır.")

def calculate_ncp(d: float, n1: int, n2: int) -> float:
    """Noncentrality parametresini (delta) hesaplar: delta = d * sqrt((n1 * n2) / (n1 + n2))"""
    harmonic_n = (n1 * n2) / (n1 + n2)
    return d * math.sqrt(harmonic_n)

def calculate_critical_t(alpha: float, df: int, tails: int) -> float:
    """Serbestlik derecesi ve alfa için kritik t değerini hesaplar."""
    prob = 1.0 - (alpha / tails)
    return float(student_t.ppf(prob, df))

def calculate_power(tails: int, df: int, ncp: float, critical_t: float) -> float:
    """
    Noncentral t dağılımı üzerinden gücü tam olarak hesaplar.
    İki yönlü testte her iki kuyruk da hesaplanır:
    Power = 1 - F(t_crit; df, delta) + F(-t_crit; df, delta)
    """
    if tails == 1:
        # Tek yönlü (One-tail) sağ kuyruk
        return float(nct.sf(critical_t, df, ncp))
    else:
        # İki yönlü (Two-tail): sağ kuyruk + sol kuyruk
        upper_tail = float(nct.sf(critical_t, df, ncp))
        lower_tail = float(nct.cdf(-critical_t, df, ncp))
        return upper_tail + lower_tail

def compute_post_hoc(tails: int, d: float, alpha: float, n1: int, n2: int, precision: int = 4) -> Dict[str, Any]:
    """
    Post hoc analizi: Verilen n1, n2, alpha ve d parametreleri için elde edilen gücü hesaplar.
    """
    validate_common_inputs(tails, d, alpha)
    if n1 < 2 or n2 < 2:
        raise ValueError(f"Örneklem büyüklükleri n1={n1}, n2={n2} en az 2 olmalıdır.")

    df = n1 + n2 - 2
    ncp = calculate_ncp(d, n1, n2)
    crit_t = calculate_critical_t(alpha, df, tails)
    power = calculate_power(tails, df, ncp, crit_t)

    return {
        "actual_power": round(power, precision),
        "critical": round(crit_t, precision),
        "df": df,
        "ncp": round(ncp, precision),
        "_raw": {
            "actual_power": power,
            "critical": crit_t,
            "df": df,
            "ncp": ncp,
            "n1": n1,
            "n2": n2,
            "n_total": n1 + n2
        }
    }

def compute_a_priori(tails: int, d: float, alpha: float, power: float, ratio: float = 1.0, precision: int = 4) -> Dict[str, Any]:
    """
    A priori analizi: Verilen hedef güç, alfa, etki büyüklüğü ve grup oranı için
    gereken minimum tamsayı n1 ve n2 değerlerini bulur.
    
    G*Power Davranışı:
    - n2 = round(ratio * n1)
    - actual_power >= target_power koşulunu sağlayan ilk tamsayı n1 bulunur.
    """
    validate_common_inputs(tails, d, alpha)
    if not (0 < power < 1):
        raise ValueError(f"Geçersiz hedef güç: {power}. Power (1-beta) (0, 1) aralığında olmalıdır.")
    if ratio <= 0:
        raise ValueError(f"Geçersiz grup oranı: {ratio}. Allocation ratio (N2/N1) pozitif olmalıdır (> 0).")

    # 1. Normal dağılım yaklaşımı ile başlangıç n1 tahmini (hızlı yakınsama için)
    z_alpha = norm.ppf(1.0 - (alpha / tails))
    z_beta = norm.ppf(power)
    approx_n1 = ((z_alpha + z_beta) ** 2 / (d ** 2)) * ((1.0 + ratio) / ratio)
    
    start_n1 = max(2, int(approx_n1) - 15)
    
    # 2. Tamsayı adımlarla hedef gücü sağlayan minimum n1 arayışı
    current_n1 = start_n1
    best_result = None

    while True:
        # G*Power yuvarlama kuralı
        current_n2 = max(2, int(round(ratio * current_n1)))
        df = current_n1 + current_n2 - 2
        ncp = calculate_ncp(d, current_n1, current_n2)
        crit_t = calculate_critical_t(alpha, df, tails)
        act_power = calculate_power(tails, df, ncp, crit_t)

        if act_power >= power:
            best_result = {
                "n1": current_n1,
                "n2": current_n2,
                "n_total": current_n1 + current_n2,
                "actual_power": round(act_power, precision),
                "critical": round(crit_t, precision),
                "df": df,
                "ncp": round(ncp, precision),
                "_raw": {
                    "actual_power": act_power,
                    "critical": crit_t,
                    "df": df,
                    "ncp": ncp,
                    "n1": current_n1,
                    "n2": current_n2,
                    "n_total": current_n1 + current_n2
                }
            }
            break
        current_n1 += 1
        
        # Güvenlik sınırı (sonsuz döngü önleyici)
        if current_n1 > 1_000_000:
            raise RuntimeError("Örneklem arama sınırı aşıldı.")

    return best_result
