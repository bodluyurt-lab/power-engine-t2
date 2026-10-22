"""
Sınır Değer ve Hata Yönetimi Testleri (tests/test_edge_cases.py)

Yönerge Kriteri (Madde d - Sınır Değerler):
"Hatalar en çok sınırlarda çıkar. Vektörlerinize mutlaka şunları koyun:
- d çok küçük
- d çok büyük
- güç alpha'ya eşit ya da ondan küçük
- eşit olmayan grup oranı
- geçersiz girdiler"
"""

import subprocess
import json
import pytest
from src.engine import compute_a_priori, compute_post_hoc

def test_very_small_effect_size():
    """Çok küçük etki boyutu (d = 0.05) - Büyük örneklem kararlılığı."""
    res = compute_a_priori(tails=2, d=0.05, alpha=0.05, power=0.80, ratio=1.0)
    assert res["n_total"] > 10000
    assert res["actual_power"] >= 0.80
    assert res["df"] == res["n_total"] - 2

def test_very_large_effect_size():
    """Çok büyük etki boyutu (d = 2.5) - Çok küçük örneklem kararlılığı."""
    res = compute_a_priori(tails=2, d=2.5, alpha=0.05, power=0.90, ratio=1.0)
    assert res["n1"] >= 2
    assert res["n2"] >= 2
    assert res["actual_power"] >= 0.90

def test_extreme_asymmetric_ratio():
    """Aşırı asimetrik grup oranları (ratio = 4.0 ve ratio = 0.25)."""
    res_high = compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=4.0)
    assert abs((res_high["n2"] / res_high["n1"]) - 4.0) < 0.05
    assert res_high["actual_power"] >= 0.80

    res_low = compute_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=0.25)
    assert abs((res_low["n2"] / res_low["n1"]) - 0.25) < 0.02
    assert res_low["actual_power"] >= 0.80

def test_post_hoc_edge_samples():
    """Minimum serbestlik derecesi (n1=2, n2=2, df=2)."""
    res = compute_post_hoc(tails=2, d=0.5, alpha=0.05, n1=2, n2=2)
    assert res["df"] == 2
    assert 0 < res["actual_power"] < 1.0

def test_invalid_tails_raises_error():
    """Geçersiz kuyruk parametresi (tails=3)."""
    with pytest.raises(ValueError):
        compute_a_priori(tails=3, d=0.5, alpha=0.05, power=0.80)

def test_invalid_negative_d_raises_error():
    """Geçersiz negatif etki büyüklüğü (d = -0.2)."""
    with pytest.raises(ValueError):
        compute_a_priori(tails=2, d=-0.2, alpha=0.05, power=0.80)

def test_invalid_alpha_range():
    """Geçersiz alpha değeri (alpha >= 1 veya <= 0)."""
    with pytest.raises(ValueError):
        compute_a_priori(tails=2, d=0.5, alpha=1.05, power=0.80)
    with pytest.raises(ValueError):
        compute_a_priori(tails=2, d=0.5, alpha=0.0, power=0.80)

def test_cli_error_contract():
    """CLI'nin geçersiz parametre verildiğinde exit code != 0 ve JSON hata döndürdüğü doğrulanır."""
    cmd = [
        r".\.venv\Scripts\python.exe",
        "-m", "src.cli",
        "--test", "t2-indep",
        "--mode", "a-priori",
        "--tails", "2",
        "--d", "-1.0",
        "--alpha", "0.05",
        "--power", "0.80"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert proc.returncode != 0, "Hatalı girdi ile CLI 0 koduyla çıkmamalıdır."
    data = json.loads(proc.stdout)
    assert "error" in data, "Çıktıda 'error' anahtarı bulunmalıdır."
