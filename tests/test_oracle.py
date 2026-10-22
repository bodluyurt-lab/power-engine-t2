"""
G*Power Referans Vektörleri Diferansiyel Doğrulama Testi (tests/test_oracle.py)

KAPI ŞARTI:
Gizli test vektörlerimde N değeri en az %90 oranında TAM eşleşmeli.
Bu test, 30 Oracle vektörünün tamamı üzerinde motorun N, n1 ve n2 değerlerini %100 TAM eşleşmeyle bulduğunu kanıtlar.
"""

import csv
import pytest
from src.engine import compute_a_priori, compute_post_hoc

def load_oracle_vectors():
    vectors = []
    with open("oracle/vectors.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vectors.append({
                "id": row["vector_id"],
                "mode": row["mode"],
                "tails": int(row["tails"]),
                "d": float(row["d"]),
                "alpha": float(row["alpha"]),
                "power": float(row["power"]),
                "ratio": float(row["ratio"]),
                "expected_n1": int(row["n1"]),
                "expected_n2": int(row["n2"]),
                "expected_n_total": int(row["n_total"]),
                "expected_power": float(row["actual_power"]),
                "expected_critical": float(row["critical_t"]),
                "expected_df": int(row["df"]),
                "expected_ncp": float(row["ncp"]),
                "desc": row["description"]
            })
    return vectors

ORACLE_VECTORS = load_oracle_vectors()

@pytest.mark.parametrize("vec", ORACLE_VECTORS, ids=[v["id"] for v in ORACLE_VECTORS])
def test_oracle_vector_exact_n_match(vec):
    """Her bir referans vektörün N, n1, n2 ve df değerlerinin tam eşleştiğini doğrular."""
    res = compute_a_priori(
        tails=vec["tails"],
        d=vec["d"],
        alpha=vec["alpha"],
        power=vec["power"],
        ratio=vec["ratio"],
        precision=4
    )

    # 1. TAM EŞLEŞME (KAPI ŞARTI)
    assert res["n1"] == vec["expected_n1"], f"{vec['id']}: n1 uyuşmazlığı! Beklenen: {vec['expected_n1']}, Bulunan: {res['n1']}"
    assert res["n2"] == vec["expected_n2"], f"{vec['id']}: n2 uyuşmazlığı! Beklenen: {vec['expected_n2']}, Bulunan: {res['n2']}"
    assert res["n_total"] == vec["expected_n_total"], f"{vec['id']}: n_total uyuşmazlığı! Beklenen: {vec['expected_n_total']}, Bulunan: {res['n_total']}"
    assert res["df"] == vec["expected_df"], f"{vec['id']}: df uyuşmazlığı! Beklenen: {vec['expected_df']}, Bulunan: {res['df']}"

    # 2. Tolerans Karşılaştırması (G*Power ekran ondalık hassasiyeti)
    assert abs(res["actual_power"] - vec["expected_power"]) < 0.001, f"{vec['id']}: actual_power sapması!"
    assert abs(res["critical"] - vec["expected_critical"]) < 0.005, f"{vec['id']}: critical_t sapması!"
    assert abs(res["ncp"] - vec["expected_ncp"]) < 0.005, f"{vec['id']}: ncp sapması!"

def test_oracle_gate_threshold():
    """Tüm vektörler üzerindeki toplam tam eşleşme oranının %90 üzerinde olduğunu doğrular."""
    match_count = 0
    total = len(ORACLE_VECTORS)

    for vec in ORACLE_VECTORS:
        res = compute_a_priori(
            tails=vec["tails"],
            d=vec["d"],
            alpha=vec["alpha"],
            power=vec["power"],
            ratio=vec["ratio"]
        )
        if res["n_total"] == vec["expected_n_total"] and res["n1"] == vec["expected_n1"] and res["n2"] == vec["expected_n2"]:
            match_count += 1

    match_rate = (match_count / total) * 100.0
    print(f"\n[ORACLE KAPI TESTİ] Tam Eşleşme Oranı: {match_rate:.1f}% ({match_count}/{total})")
    assert match_rate >= 90.0, f"Kapı şartı başarısız! Eşleşme oranı %90'ın altında: {match_rate}%"
