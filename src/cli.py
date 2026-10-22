"""
G*Power Clone CLI Arayüzü (src/cli.py)

CLI Sözleşmesi:
gpower-clone --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1
Beklenen çıktı (tek satır JSON):
{"n1":105,"n2":105,"n_total":210,"actual_power":0.9501,"critical":1.9714,"df":208,"ncp":3.6228}

Geçersiz girdide:
{"error":"<açıklama>"} ve sıfırdan farklı çıkış kodu (exit code != 0).
"""

import sys
import json
import argparse
from typing import Dict, Any
from src.engine import compute_a_priori, compute_post_hoc

def parse_args():
    parser = argparse.ArgumentParser(
        description="G*Power Bağımsız İki Grup t-Testi CLI Motoru",
        add_help=False
    )
    parser.add_argument("--test", type=str, required=True, help="Test ailesi (örn: t2-indep)")
    parser.add_argument("--mode", type=str, required=True, choices=["a-priori", "post-hoc"], help="Analiz modu")
    parser.add_argument("--tails", type=int, required=True, choices=[1, 2], help="Kuyruk sayısı (1 veya 2)")
    parser.add_argument("--d", type=float, required=True, help="Cohen's d etki büyüklüğü")
    parser.add_argument("--alpha", type=float, required=True, help="Tip I hata olasılığı (alpha)")
    
    # A priori için
    parser.add_argument("--power", type=float, help="Hedef güç (1 - beta)")
    parser.add_argument("--ratio", type=float, default=1.0, help="Grup büyüklüğü oranı (N2/N1)")
    
    # Post hoc için
    parser.add_argument("--n1", type=int, help="1. grup örneklem büyüklüğü")
    parser.add_argument("--n2", type=int, help="2. grup örneklem büyüklüğü")

    return parser

def main():
    parser = parse_args()
    try:
        args = parser.parse_args()
    except Exception as e:
        print(json.dumps({"error": f"Argüman ayrıştırma hatası: {str(e)}"}, ensure_ascii=False))
        sys.exit(2)

    if args.test != "t2-indep":
        print(json.dumps({"error": f"Desteklenmeyen test ailesi: '{args.test}'. Yalnızca 't2-indep' desteklenir."}, ensure_ascii=False))
        sys.exit(1)

    try:
        if args.mode == "a-priori":
            if args.power is None:
                raise ValueError("A priori modunda '--power' parametresi zorunludur.")
            
            res = compute_a_priori(
                tails=args.tails,
                d=args.d,
                alpha=args.alpha,
                power=args.power,
                ratio=args.ratio
            )
            # Çıktı formatı sözleşmesi (sadece istenen anahtarlar)
            output = {
                "n1": res["n1"],
                "n2": res["n2"],
                "n_total": res["n_total"],
                "actual_power": res["actual_power"],
                "critical": res["critical"],
                "df": res["df"],
                "ncp": res["ncp"]
            }
            print(json.dumps(output, separators=(',', ':'), ensure_ascii=False))
            sys.exit(0)

        elif args.mode == "post-hoc":
            if args.n1 is None or args.n2 is None:
                raise ValueError("Post hoc modunda '--n1' ve '--n2' parametreleri zorunludur.")
            
            res = compute_post_hoc(
                tails=args.tails,
                d=args.d,
                alpha=args.alpha,
                n1=args.n1,
                n2=args.n2
            )
            output = {
                "actual_power": res["actual_power"],
                "critical": res["critical"],
                "df": res["df"],
                "ncp": res["ncp"]
            }
            print(json.dumps(output, separators=(',', ':'), ensure_ascii=False))
            sys.exit(0)

    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
