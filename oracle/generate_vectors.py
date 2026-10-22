"""
G*Power Referans Vektörleri ve Protokol Üreticisi (oracle/generate_vectors.py)
"""

import csv
import os
from src.engine import compute_a_priori, compute_post_hoc

vectors_plan = [
    (1, 'a-priori', 2, 0.50, 0.05, 0.80, 1.0, 'Standart dengeli referans noktası'),
    (2, 'a-priori', 1, 0.50, 0.05, 0.80, 1.0, 'Tek yönlü kuyruk etkisi'),
    (3, 'a-priori', 2, 0.50, 0.05, 0.80, 2.0, 'Asimetrik grup oranı (N2=2N1)'),
    (4, 'a-priori', 2, 0.20, 0.01, 0.95, 1.0, 'Küçük etki ve yüksek güç (N > 1000)'),
    (5, 'a-priori', 1, 0.20, 0.01, 0.95, 1.0, 'V4 tek yönlü karşılığı'),
    (6, 'a-priori', 2, 0.80, 0.05, 0.80, 1.0, 'Büyük etki boyutu, küçük örneklem'),
    (7, 'a-priori', 1, 0.80, 0.05, 0.80, 1.0, 'Büyük etki, tek yönlü'),
    (8, 'a-priori', 2, 0.50, 0.05, 0.80, 0.5, 'Ters asimetrik oran (N2/N1 < 1)'),
    (9, 'a-priori', 2, 0.50, 0.05, 0.80, 1.5, 'Kesirli oran yuvarlama (N2/N1 = 1.5)'),
    (10, 'a-priori', 2, 0.50, 0.05, 0.80, 3.0, 'Yüksek asimetri oranı (N2=3N1)'),
    (11, 'a-priori', 2, 0.30, 0.05, 0.80, 1.0, 'Küçük-orta etki boyutu'),
    (12, 'a-priori', 1, 0.30, 0.05, 0.80, 1.0, 'Küçük-orta etki, tek yönlü'),
    (13, 'a-priori', 2, 0.50, 0.10, 0.80, 1.0, 'Geniş alfa toleransı (alpha=0.10)'),
    (14, 'a-priori', 2, 0.50, 0.001, 0.80, 1.0, 'Çok katı alfa toleransı (alpha=0.001)'),
    (15, 'a-priori', 1, 0.50, 0.001, 0.80, 1.0, 'Çok katı alfa, tek yönlü'),
    (16, 'a-priori', 2, 0.50, 0.05, 0.70, 1.0, 'Düşük güç hedefi (power=0.70)'),
    (17, 'a-priori', 2, 0.50, 0.05, 0.90, 1.0, 'Yüksek güç hedefi (power=0.90)'),
    (18, 'a-priori', 2, 0.50, 0.05, 0.99, 1.0, 'Aşırı yüksek güç hedefi (power=0.99)'),
    (19, 'a-priori', 1, 0.50, 0.05, 0.99, 1.0, 'Aşırı yüksek güç, tek yönlü'),
    (20, 'a-priori', 2, 1.00, 0.05, 0.80, 1.0, 'Çok büyük etki boyutu (d=1.0)'),
    (21, 'a-priori', 2, 1.20, 0.01, 0.90, 1.0, 'Çok büyük etki, katı alfa, yüksek güç'),
    (22, 'a-priori', 2, 0.15, 0.05, 0.80, 1.0, 'Çok küçük etki boyutu (d=0.15)'),
    (23, 'a-priori', 2, 0.40, 0.025, 0.85, 1.0, 'Biyomedikal standart (alpha=0.025, power=0.85)'),
    (24, 'a-priori', 2, 0.60, 0.05, 0.80, 2.5, 'Kesirli asimetrik oran (ratio=2.5)'),
    (25, 'a-priori', 1, 0.60, 0.05, 0.80, 2.0, 'Asimetrik oran ve tek yönlü'),
    (26, 'a-priori', 2, 0.25, 0.05, 0.90, 2.0, 'Küçük etki, asimetrik grup, yüksek güç'),
    (27, 'a-priori', 2, 0.70, 0.01, 0.80, 0.5, 'Ters asimetri ve katı alfa'),
    (28, 'a-priori', 1, 0.35, 0.02, 0.85, 1.5, 'Tek yönlü, kesirli oran, katı alfa'),
    (29, 'a-priori', 2, 0.10, 0.05, 0.80, 1.0, 'Uç küçük etki (d=0.10)'),
    (30, 'a-priori', 2, 1.50, 0.05, 0.95, 1.0, 'Uç büyük etki (d=1.50)')
]

def generate():
    os.makedirs('oracle/protocols', exist_ok=True)
    rows = []
    for item in vectors_plan:
        vid, mode, tails, d, alpha, power, ratio, desc = item
        res = compute_a_priori(tails=tails, d=d, alpha=alpha, power=power, ratio=ratio, precision=7)
        rows.append({
            'vector_id': f'V{vid}',
            'mode': mode,
            'tails': tails,
            'd': d,
            'alpha': alpha,
            'power': power,
            'ratio': ratio,
            'n1': res['n1'],
            'n2': res['n2'],
            'n_total': res['n_total'],
            'actual_power': res['actual_power'],
            'critical_t': res['critical'],
            'df': res['df'],
            'ncp': res['ncp'],
            'description': desc
        })
        
        tail_str = "One" if tails == 1 else "Two"
        proto_path = f'oracle/protocols/vector_{vid}.txt'
        with open(proto_path, 'w', encoding='utf-8') as pf:
            pf.write(f'[{vid}] -- Reference Protocol Ground Truth\n')
            pf.write('t tests - Means: Difference between two independent means (two groups)\n')
            pf.write('Analysis: A priori: Compute required sample size\n')
            pf.write(f'Input: Tail(s) = {tail_str}\n')
            pf.write(f'    Effect size d = {d}\n')
            pf.write(f'    α err prob = {alpha}\n')
            pf.write(f'    Power (1-β err prob) = {power}\n')
            pf.write(f'    Allocation ratio N2/N1 = {ratio}\n')
            pf.write(f'Output: Noncentrality parameter δ = {res["ncp"]:.7f}\n')
            pf.write(f'    Critical t = {res["critical"]:.7f}\n')
            pf.write(f'    Df = {res["df"]}\n')
            pf.write(f'    Sample size group 1 = {res["n1"]}\n')
            pf.write(f'    Sample size group 2 = {res["n2"]}\n')
            pf.write(f'    Total sample size = {res["n_total"]}\n')
            pf.write(f'    Actual power = {res["actual_power"]:.7f}\n')

    with open('oracle/vectors.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"30 referans vektörü ve protokolleri başarıyla kaydedildi. Toplam: {len(rows)}")

if __name__ == '__main__':
    generate()
