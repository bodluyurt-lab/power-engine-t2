"""
MCP Sunucusu ve CLI Eşdeğerlik Testi (tests/test_mcp.py)

Ödev Şartı (+15 MCP Sunucusu):
- CLI ile MCP'nin aynı girdide aynı çıktıyı verdiğini gösteren testler.
- Hesap mantığının kopyalanmadığını, doğrudan motorun kullanıldığını doğrular.
"""

import subprocess
import json
import pytest
from src.mcp_server import calculate_t2_indep_a_priori, calculate_t2_indep_post_hoc

@pytest.mark.parametrize("tails,d,alpha,power,ratio", [
    (2, 0.50, 0.05, 0.95, 1.0),
    (1, 0.50, 0.05, 0.80, 1.0),
    (2, 0.30, 0.01, 0.90, 1.5),
    (2, 0.80, 0.05, 0.80, 2.0),
])
def test_mcp_cli_a_priori_equivalence(tails, d, alpha, power, ratio):
    """MCP a priori fonksiyonu ile CLI çıktısının birebir aynı olduğunu doğrular."""
    # 1. MCP fonksiyonu çıktısı
    mcp_out = calculate_t2_indep_a_priori(
        tails=tails,
        d=d,
        alpha=alpha,
        power=power,
        ratio=ratio
    )

    # 2. CLI çıktısı
    cmd = [
        r".\.venv\Scripts\python.exe",
        "-m", "src.cli",
        "--test", "t2-indep",
        "--mode", "a-priori",
        "--tails", str(tails),
        "--d", str(d),
        "--alpha", str(alpha),
        "--power", str(power),
        "--ratio", str(ratio)
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert proc.returncode == 0
    cli_out = json.loads(proc.stdout)

    # Birebir Eşdeğerlik Kontrolü
    assert mcp_out == cli_out, f"MCP ve CLI çıktıları uyuşmuyor!\nMCP: {mcp_out}\nCLI: {cli_out}"

@pytest.mark.parametrize("tails,d,alpha,n1,n2", [
    (2, 0.50, 0.05, 64, 64),
    (1, 0.50, 0.05, 51, 51),
    (2, 0.60, 0.01, 40, 80),
])
def test_mcp_cli_post_hoc_equivalence(tails, d, alpha, n1, n2):
    """MCP post hoc fonksiyonu ile CLI çıktısının birebir aynı olduğunu doğrular."""
    # 1. MCP çıktısı
    mcp_out = calculate_t2_indep_post_hoc(
        tails=tails,
        d=d,
        alpha=alpha,
        n1=n1,
        n2=n2
    )

    # 2. CLI çıktısı
    cmd = [
        r".\.venv\Scripts\python.exe",
        "-m", "src.cli",
        "--test", "t2-indep",
        "--mode", "post-hoc",
        "--tails", str(tails),
        "--d", str(d),
        "--alpha", str(alpha),
        "--n1", str(n1),
        "--n2", str(n2)
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert proc.returncode == 0
    cli_out = json.loads(proc.stdout)

    assert mcp_out == cli_out, f"MCP ve CLI post-hoc çıktıları uyuşmuyor!\nMCP: {mcp_out}\nCLI: {cli_out}"
