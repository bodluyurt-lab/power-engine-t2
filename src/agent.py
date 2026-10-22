"""
Klinik Araştırmacı AI Ajanı (src/agent.py)

Bu modül, hekimlerin ve araştırmacıların kendi klinik diliyle (Türkçe) sordukları
araştırma sorularını anlayıp, Sistem 1 sınıflandırma ve parametre çıkarımı yaparak
MCP hesaplama motorunu tetikleyen ajandır.

KURALLAR:
1. Ajan hesabı kendisi YAPMAZ; sayısal sonucu daima MCP motorundan alır.
2. Sistem 1 modelleme etiketleri:
   ['t2-indep', 't-paired', 'anova-oneway', 'chi2-contingency', 'multireg-r2', 'ambiguous', 'unsupported']
3. Güven skoru < 0.75 veya etiket ambiguous/unsupported ise kullanıcıya açıklama yöneltilir.
"""

import re
import json
import time
from typing import Dict, Any, Tuple, List, Optional
from src.engine import compute_a_priori, compute_post_hoc

LABELS = [
    "t2-indep",
    "t-paired",
    "anova-oneway",
    "chi2-contingency",
    "multireg-r2",
    "ambiguous",
    "unsupported"
]

def tr_lower(text: str) -> str:
    """Türkçe karakterleri (İ, I, vb.) doğru şekilde küçük harfe çevirir."""
    return text.replace('İ', 'i').replace('I', 'ı').lower()

def system1_classify_test_family(query: str) -> Tuple[str, float, str]:
    """
    Klinik soruyu Sistem 1 hızında etiketler ve güven skoru üretir.
    Döndürür: (etiket, güven_skoru, gerekçe)
    """
    q_norm = tr_lower(query)

    # Ambiguous / Yetersiz bilgi
    if len(query.strip()) < 15 or "bilmiyorum" in q_norm or "emin değilim" in q_norm:
        return ("ambiguous", 0.50, "Soru klinik tasarım ve grup yapısı hakkında yeterli bilgi içermiyor.")

    # 1. Eşleştirilmiş Grup (t-paired) - Öncelikli kontrol
    paired_keywords = ["önce ve sonra", "öncesi ve sonrası", "aynı hasta", "eşleştirilmiş", "tekrarlı ölçüm"]
    if any(k in q_norm for k in paired_keywords):
        return ("t-paired", 0.95, "Aynı denekler üzerinde önce/sonra ölçümü (eşleştirilmiş t-testi).")

    # 2. Tek Yönlü ANOVA (anova-oneway)
    anova_keywords = ["üç farklı", "üç grup", "3 grup", "4 grup", "dört grup", "üç kol", "çoklu grup"]
    if any(k in q_norm for k in anova_keywords):
        return ("anova-oneway", 0.92, "İkiden fazla grup ortalaması karşılaştırması (Tek yönlü ANOVA).")

    # 3. Ki-Kare Olumsallık Tablosu (chi2-contingency)
    chi2_keywords = ["oran", "oranlar", "yüzde", "iyileşme oranı", "yanıt oranı", "kontenjans", "ki-kare", "kategorik"]
    if any(k in q_norm for k in chi2_keywords) and not ("üç farklı" in q_norm or "bağımsız" in q_norm and "ortalama" in q_norm):
        return ("chi2-contingency", 0.90, "Kategorik oran karşılaştırması (Ki-kare testi).")

    # 4. Çoklu Regresyon R² (multireg-r2)
    reg_keywords = ["regresyon", "r2", "r kare", "yordayıcı", "risk faktör", "bağımsız değişken"]
    if any(k in q_norm for k in reg_keywords):
        return ("multireg-r2", 0.92, "Çoklu belirleyicilik ve risk faktörleri regresyon analizi.")

    # 5. Bağımsız İki Grup (t2-indep)
    indep_keywords = [
        "bağımsız", "ilaç ve plasebo", "kontrol ve deney",
        "iki grup", "tedavi kolu", "iki kol", "farklı grup"
    ]
    if any(k in q_norm for k in indep_keywords):
        confidence = 0.95 if any(x in q_norm for x in ["ortalama", "fark", "puan", "skor", "d=", "etki", "güç", "alfa"]) else 0.85
        return ("t2-indep", confidence, "İki bağımsız grup ortalaması karşılaştırması tespit edildi.")

    return ("unsupported", 0.40, "Belirtilen klinik senaryo desteklenen standart ailelerle net eşleşmedi.")

def extract_parameters(query: str) -> Dict[str, Any]:
    """Soru metninden etki büyüklüğü (d), alpha, güç, oran ve kuyruk çıkarır."""
    params = {
        "tails": 2,
        "d": 0.50,
        "alpha": 0.05,
        "power": 0.80,
        "ratio": 1.0,
        "mode": "a-priori"
    }
    q = tr_lower(query)

    # Tails
    if "tek yönlü" in q or "tek taraflı" in q or "one tail" in q:
        params["tails"] = 1
    elif "çift yönlü" in q or "iki yönlü" in q or "iki taraflı" in q or "two tail" in q:
        params["tails"] = 2

    # Effect size d
    d_match = re.search(r'(?:etki\s*büyüklüğü|effect\s*size|d)\s*[=:]?\s*(\d+(?:[.,]\d+)?)', q)
    if d_match:
        params["d"] = float(d_match.group(1).replace(',', '.'))
    elif "orta etki" in q:
        params["d"] = 0.50
    elif "küçük etki" in q:
        params["d"] = 0.20
    elif "büyük etki" in q:
        params["d"] = 0.80

    # Alpha
    alpha_match = re.search(r'(?:alfa|alpha|anlamlılık|p)\s*[=:<]?\s*(\d+(?:[.,]\d+)?)', q)
    if alpha_match:
        params["alpha"] = float(alpha_match.group(1).replace(',', '.'))

    # Power
    power_match = re.search(r'(?:güç|power|1-beta)\s*[=:]?\s*(?:%\s*)?(\d+(?:[.,]\d+)?)', q)
    if power_match:
        val = float(power_match.group(1).replace(',', '.'))
        params["power"] = val / 100.0 if val > 1.0 else val

    # Ratio
    if "2 kat" in q or "iki katı" in q or "ratio=2" in q:
        params["ratio"] = 2.0
    ratio_match = re.search(r'(?:oran|ratio)\s*[=:]?\s*(\d+(?:[.,]\d+)?)', q)
    if ratio_match:
        params["ratio"] = float(ratio_match.group(1).replace(',', '.'))

    return params

def run_clinical_agent(query: str) -> Dict[str, Any]:
    """
    Hekim sorusunu işler, gerekirse onay ister, motoru çağırır ve klinik yanıt döner.
    """
    start_time = time.time()
    label, confidence, reason = system1_classify_test_family(query)

    if confidence < 0.75 or label in ("ambiguous", "unsupported"):
        return {
            "status": "NEEDS_CLARIFICATION",
            "label": label,
            "confidence": confidence,
            "message": f"Klinik tasarım tam olarak anlaşılamadı (Güven: {confidence:.2f}). {reason} Lütfen çalışmanızdaki grup yapısını ve karşılaştırılacak değişken türünü (ortalama/oran) netleştiriniz.",
            "elapsed_ms": round((time.time() - start_time) * 1000, 2)
        }

    if label != "t2-indep":
        return {
            "status": "UNSUPPORTED_FAMILY",
            "label": label,
            "confidence": confidence,
            "message": f"Bu araştırma '{label}' ailesine girmektedir ({reason}). Ancak bu sprint kapsamındaki motorumuz şu an yalnızca Bağımsız İki Grup t-Testi ('t2-indep') için aktiftir.",
            "elapsed_ms": round((time.time() - start_time) * 1000, 2)
        }

    # Parametreleri çıkar
    params = extract_parameters(query)

    # Motoru çağır (Ajan hesabı KENDİSİ YAPMAZ, motordan alır)
    calc_result = compute_a_priori(
        tails=params["tails"],
        d=params["d"],
        alpha=params["alpha"],
        power=params["power"],
        ratio=params["ratio"]
    )

    elapsed = round((time.time() - start_time) * 1000, 2)

    response_text = (
        f"Sayın Araştırmacı, çalışmanız için bağımsız iki grup t-testi belirlenmiştir (Güven: {confidence:.2f}).\n"
        f"Girdi Parametreleri: Kuyruk={params['tails']}, Etki Büyüklüğü (d)={params['d']}, Alfa={params['alpha']}, Hedef Güç={params['power']}, Grup Oranı={params['ratio']}.\n"
        f"Hesaplanan Gereksinimler:\n"
        f"  - 1. Grup Örneklemi (n1): {calc_result['n1']}\n"
        f"  - 2. Grup Örneklemi (n2): {calc_result['n2']}\n"
        f"  - Toplam Gereken Hasta Sayısı (N): {calc_result['n_total']}\n"
        f"  - Elde Edilen Gerçek Güç: {calc_result['actual_power']}\n"
        f"  - Kritik t Değeri: {calc_result['critical']} (Serbestlik Derecesi df={calc_result['df']})"
    )

    return {
        "status": "SUCCESS",
        "label": label,
        "confidence": confidence,
        "parameters": params,
        "engine_output": calc_result,
        "clinical_response": response_text,
        "elapsed_ms": elapsed
    }

# 10 Soruluk Değerlendirme Seti (Benchmark)
BENCHMARK_QUESTIONS = [
    {
        "id": 1,
        "question": "Yeni geliştirdiğimiz antihipertansif ilacı plasebo ile karşılaştıracağız. İki bağımsız hasta grubumuz var, tansiyon düşüşü ortalamalarına bakacağız. Orta düzey bir etki (d=0.50), %5 alfa ve %80 güç istiyoruz. Kaç hasta gerekir?",
        "expected_family": "t2-indep",
        "expected_n": 128
    },
    {
        "id": 2,
        "question": "Diyabetik hastalarımızda yeni ilacın kan şekerini düşürmesini bekliyoruz (tek yönlü hipotez). İki bağımsız grup var. d=0.50, alfa 0.05 ve güç 0.80 için toplam hasta sayısı ne olmalı?",
        "expected_family": "t2-indep",
        "expected_n": 102
    },
    {
        "id": 3,
        "question": "Nadir bir hastalıkta deney grubuna 1 hasta alırken kontrol grubuna 2 hasta alabiliyoruz (oran=2). İki bağımsız grup ortalaması, d=0.50, alfa=0.05, güç=0.80 için N nedir?",
        "expected_family": "t2-indep",
        "expected_n": 144
    },
    {
        "id": 4,
        "question": "Çok katı bir kardiyoloji çalışmasında iki bağımsız grupta küçük bir etkiyi (d=0.20) yakalamak istiyoruz. Alfa=0.01 ve güç=%95 olsun. Çift yönlü testte kaç hasta almalıyız?",
        "expected_family": "t2-indep",
        "expected_n": 1786
    },
    {
        "id": 5,
        "question": "Aynı hastaların ameliyat öncesi ve ameliyat sonrası ağrı skorlarını karşılaştıracağız. Kaç hasta almalıyız?",
        "expected_family": "t-paired",
        "expected_n": None
    },
    {
        "id": 6,
        "question": "Üç farklı kemoterapi protokolünün tümör küçülme oranları ortalamasını karşılaştırmak istiyoruz. Hangi testi yapmalıyız?",
        "expected_family": "anova-oneway",
        "expected_n": None
    },
    {
        "id": 7,
        "question": "İki grubun tedaviye yanıt verme yüzdelerini (iyileşti / iyileşmedi oranlarını) karşılaştıracağız.",
        "expected_family": "chi2-contingency",
        "expected_n": None
    },
    {
        "id": 8,
        "question": "Miyokard enfarktüsü riskini açıklamak için yaş, kolesterol ve sigara gibi 5 risk faktörünün R2 belirleyiciliğini inceleyeceğiz.",
        "expected_family": "multireg-r2",
        "expected_n": None
    },
    {
        "id": 9,
        "question": "Bir çalışma planlıyorum ama tam olarak ne ölçeceğimi bilmiyorum, grup sayısı da belli değil.",
        "expected_family": "ambiguous",
        "expected_n": None
    },
    {
        "id": 10,
        "question": "İki bağımsız kolda büyük bir etki (d=0.80) bekliyoruz. Alfa 0.05 ve güç 0.80 ile iki yönlü tasarımda kaç kişi yeterli?",
        "expected_family": "t2-indep",
        "expected_n": 52
    }
]

def run_benchmark():
    """10 soruluk değerlendirme setini çalıştırır ve doğruluk oranını raporlar."""
    correct_family = 0
    correct_n = 0
    t2_count = 0

    results = []
    for item in BENCHMARK_QUESTIONS:
        res = run_clinical_agent(item["question"])
        family_match = (res["label"] == item["expected_family"])
        if family_match:
            correct_family += 1

        n_match = False
        if item["expected_n"] is not None:
            t2_count += 1
            if res.get("engine_output") and res["engine_output"]["n_total"] == item["expected_n"]:
                correct_n += 1
                n_match = True

        results.append({
            "id": item["id"],
            "expected_family": item["expected_family"],
            "predicted_family": res["label"],
            "confidence": res["confidence"],
            "family_match": family_match,
            "expected_n": item["expected_n"],
            "predicted_n": res.get("engine_output", {}).get("n_total") if res.get("engine_output") else None,
            "n_match": n_match,
            "elapsed_ms": res["elapsed_ms"]
        })

    accuracy_family = (correct_family / len(BENCHMARK_QUESTIONS)) * 100.0
    accuracy_n = (correct_n / t2_count) * 100.0 if t2_count > 0 else 0.0

    report = {
        "total_questions": len(BENCHMARK_QUESTIONS),
        "family_accuracy_percent": accuracy_family,
        "n_accuracy_percent": accuracy_n,
        "details": results
    }
    return report

if __name__ == "__main__":
    report = run_benchmark()
    print(json.dumps(report, indent=2, ensure_ascii=False))
