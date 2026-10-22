"""
G*Power t2-indep Model Context Protocol (MCP) Sunucusu (src/mcp_server.py)

Bu modül, hesap motorunu doğrudan çağıran ince bir adaptördür (thin adapter).
Hesaplama mantığı buraya KOPYALANMAZ; doğrudan `src.engine` fonksiyonlarını kullanır.
"""

from typing import Dict, Any, Optional
from mcp.server import MCPServer
from src.engine import compute_a_priori, compute_post_hoc

# MCPServer Sunucu Tanımı
mcp = MCPServer("GPower-t2-indep-Server")

@mcp.tool(
    name="calculate_t2_indep_a_priori",
    description="Bağımsız iki grup t-testi (Means: Difference between two independent means) için gereken örneklem büyüklüğünü (N1, N2, N_total) ve kritik değerleri hesaplar."
)
def calculate_t2_indep_a_priori(
    tails: int,
    d: float,
    alpha: float,
    power: float,
    ratio: float = 1.0
) -> Dict[str, Any]:
    """
    Parametreler:
      tails: Kuyruk yönü (1: One-tail, 2: Two-tail)
      d: Cohen's d etki büyüklüğü (d > 0)
      alpha: Tip I hata payı (0 < alpha < 1, örn: 0.05)
      power: Hedeflenen istatistiksel güç 1-beta (0 < power < 1, örn: 0.80 veya 0.95)
      ratio: Grup büyüklükleri oranı N2/N1 (varsayılan: 1.0)
    """
    res = compute_a_priori(
        tails=tails,
        d=d,
        alpha=alpha,
        power=power,
        ratio=ratio
    )
    return {
        "n1": res["n1"],
        "n2": res["n2"],
        "n_total": res["n_total"],
        "actual_power": res["actual_power"],
        "critical": res["critical"],
        "df": res["df"],
        "ncp": res["ncp"]
    }

@mcp.tool(
    name="calculate_t2_indep_post_hoc",
    description="Bağımsız iki grup t-testi için verilen örneklem büyüklükleri (N1, N2) üzerinden gerçekleşen gücü (achieved power) hesaplar."
)
def calculate_t2_indep_post_hoc(
    tails: int,
    d: float,
    alpha: float,
    n1: int,
    n2: int
) -> Dict[str, Any]:
    """
    Parametreler:
      tails: Kuyruk yönü (1 veya 2)
      d: Cohen's d etki büyüklüğü
      alpha: Anlamlılık düzeyi
      n1: 1. grup örneklem sayısı
      n2: 2. grup örneklem sayısı
    """
    res = compute_post_hoc(
        tails=tails,
        d=d,
        alpha=alpha,
        n1=n1,
        n2=n2
    )
    return {
        "actual_power": res["actual_power"],
        "critical": res["critical"],
        "df": res["df"],
        "ncp": res["ncp"]
    }

if __name__ == "__main__":
    mcp.run()
