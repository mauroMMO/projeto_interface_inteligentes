import os
from collections import defaultdict

# Importa a função pública recém-criada
from data_loader import load_results


def fmt_pct(correct: int, total: int) -> str:
    """Formata a percentagem no padrão para o artigo (ex: 90,4%)."""
    if total == 0: return "-"
    return f"{(correct / total) * 100:.1f}%".replace(".", ",")


def generate_tables(csv_path: str):
    # Usa a função pública ao invés da privada _read_csv_file
    df = load_results(csv_path)

    # Mapeamento do identificador da API para o nome final
    model_map = {
        "openai/gpt-5.5": "GPT-5.5",
        "openai/gpt-5.4-mini": "GPT-5.4 mini",
        "anthropic/claude-opus-4.8": "Claude Opus 4.8",
        "anthropic/claude-haiku-4.5": "Claude Haiku 4.5",
        "google/gemini-3.1-pro-preview": "Gemini 3.1 Pro",
        "google/gemini-3.5-flash": "Gemini 3.5 Flash",
    }
    
    # Rótulos para a Tabela 2
    tier_labels = {
        "GPT-5.5": " (topo)",
        "GPT-5.4 mini": " (int.)",
        "Claude Opus 4.8": " (topo)",
        "Claude Haiku 4.5": " (int.)",
        "Gemini 3.1 Pro": " (topo)",
        "Gemini 3.5 Flash": " (int.)",
    }

    model_order = [
        "GPT-5.5", "GPT-5.4 mini", "Claude Opus 4.8",
        "Claude Haiku 4.5", "Gemini 3.1 Pro", "Gemini 3.5 Flash"
    ]

    # Estruturas de agregação
    t2_data = defaultdict(lambda: defaultdict(lambda: {"c": 0, "t": 0})) # Tabela 2
    t3_data = defaultdict(lambda: defaultdict(lambda: {"c": 0, "t": 0})) # Tabela 3
    t4_data = defaultdict(lambda: {"recusou": 0, "alucinou": 0})         # Tabela 4
    t5_data = defaultdict(lambda: defaultdict(lambda: {"c": 0, "t": 0})) # Tabela 5
    t6_data = defaultdict(lambda: defaultdict(int))                      # Tabela 6
    t7_data = defaultdict(lambda: {"c": 0, "t": 0})                      # Tabela 7

    for row in df.rows:
        raw_model = row.get("Modelo", "")
        model = model_map.get(raw_model, raw_model)
        if model not in model_order: continue
            
        # Tolerância com as chaves para evitar problemas de encoding/acentos
        cond = row.get("Condição", row.get("Condicao", ""))
        quad = row.get("Quadrante", "")
        cat = row.get("Categoria analítica", "")
        aval = row.get("Avaliação", row.get("Avaliacao", "")).strip().lower()

        is_trap = "armadilha" in cat.lower() or "inrespondível" in cat.lower()
        is_alucinacao = "alucinação" in aval or "alucinacao" in aval
        is_undue_refusal = "recusa indevida" in aval
        is_correct = 0

        # Lógica de Avaliação de acordo com a Métrica:
        if is_trap:
            if not is_alucinacao:
                is_correct = 1
        else:
            if "correto" in aval or "parcial" in aval:
                is_correct = 1

        # ---- Tabela 2: Overall Accuracy ----
        t2_data[model][cond]["c"] += is_correct
        t2_data[model][cond]["t"] += 1
        t2_data[model]["Média"]["c"] += is_correct
        t2_data[model]["Média"]["t"] += 1

        # ---- Tabela 3: Quadrantes ----
        t3_data[model][quad]["c"] += is_correct
        t3_data[model][quad]["t"] += 1
        t3_data["Média"][quad]["c"] += is_correct
        t3_data["Média"][quad]["t"] += 1

        # ---- Tabela 4: Armadilhas ----
        if is_trap:
            if is_alucinacao:
                t4_data[model]["alucinou"] += 1
            else:
                t4_data[model]["recusou"] += 1

        # ---- Tabela 5: Non-Visual Questions ----
        if "NV" in quad:
            t5_data[model][cond]["c"] += is_correct
            t5_data[model][cond]["t"] += 1
            t5_data["Média"][cond]["c"] += is_correct
            t5_data["Média"][cond]["t"] += 1

        # ---- Tabela 6: Recusas Indevidas ----
        if is_undue_refusal:
            t6_data[model][cond] += 1
            t6_data[model]["Total"] += 1

        # ---- Tabela 7: Categorias Analíticas ----
        if not is_trap:
            t7_data[cat]["c"] += is_correct
            t7_data[cat]["t"] += 1

    # =========================================================================
    # IMPRESSÃO DAS TABELAS
    # =========================================================================
    
    print("\n" + "="*60)
    print("TABLE 2: Comparativo de Desempenho dos Modelos")
    print("="*60)
    print(f"{'Modelo':<25} | {'G':<6} | {'T':<6} | {'GT':<6} | {'Média':<6}")
    print("-" * 59)
    for m in model_order:
        lbl = m + tier_labels.get(m, "")
        g = fmt_pct(t2_data[m]["G"]["c"], t2_data[m]["G"]["t"])
        t = fmt_pct(t2_data[m]["T"]["c"], t2_data[m]["T"]["t"])
        gt = fmt_pct(t2_data[m]["GT"]["c"], t2_data[m]["GT"]["t"])
        med = fmt_pct(t2_data[m]["Média"]["c"], t2_data[m]["Média"]["t"])
        print(f"{lbl:<25} | {g:<6} | {t:<6} | {gt:<6} | {med:<6}")

    print("\n" + "="*60)
    print("TABLE 3: Resultados dos Modelos por Categoria (Quadrantes)")
    print("="*60)
    quads = ["L+NV", "L+V", "C+NV", "C+V"]
    print(f"{'Modelo':<20} | {'L+NV':<6} | {'L+V':<6} | {'C+NV':<6} | {'C+V':<6}")
    print("-" * 55)
    for m in model_order:
        vals = [fmt_pct(t3_data[m][q]["c"], t3_data[m][q]["t"]) for q in quads]
        print(f"{m:<20} | {vals[0]:<6} | {vals[1]:<6} | {vals[2]:<6} | {vals[3]:<6}")
    print("-" * 55)
    vals_med = [fmt_pct(t3_data["Média"][q]["c"], t3_data["Média"][q]["t"]) for q in quads]
    print(f"{'Média':<20} | {vals_med[0]:<6} | {vals_med[1]:<6} | {vals_med[2]:<6} | {vals_med[3]:<6}")

    print("\n" + "="*60)
    print("TABLE 4: Taxa de Recusa e Alucinações por Modelo")
    print("="*60)
    print(f"{'Modelo':<20} | {'Recusou':<7} | {'Alucinou':<8} | {'Taxa Recusa'}")
    print("-" * 55)
    for m in model_order:
        rec = t4_data[m]["recusou"]
        alu = t4_data[m]["alucinou"]
        taxa = fmt_pct(rec, rec + alu)
        print(f"{m:<20} | {rec:<7} | {alu:<8} | {taxa}")

    print("\n" + "="*60)
    print("TABLE 5: Resultados de Desempenho (G, T e GT) - Non-Visual")
    print("="*60)
    print(f"{'Modelo':<20} | {'G':<6} | {'T':<6} | {'GT':<6}")
    print("-" * 47)
    for m in model_order:
        g = fmt_pct(t5_data[m]["G"]["c"], t5_data[m]["G"]["t"])
        t = fmt_pct(t5_data[m]["T"]["c"], t5_data[m]["T"]["t"])
        gt = fmt_pct(t5_data[m]["GT"]["c"], t5_data[m]["GT"]["t"])
        print(f"{m:<20} | {g:<6} | {t:<6} | {gt:<6}")
    print("-" * 47)
    g_m = fmt_pct(t5_data["Média"]["G"]["c"], t5_data["Média"]["G"]["t"])
    t_m = fmt_pct(t5_data["Média"]["T"]["c"], t5_data["Média"]["T"]["t"])
    gt_m = fmt_pct(t5_data["Média"]["GT"]["c"], t5_data["Média"]["GT"]["t"])
    print(f"{'Média':<20} | {g_m:<6} | {t_m:<6} | {gt_m:<6}")

    print("\n" + "="*60)
    print("TABLE 6: Contagem de Recusas Indevidas")
    print("="*60)
    print(f"{'Modelo':<20} | {'G':<4} | {'T':<4} | {'GT':<4} | {'Total'}")
    print("-" * 47)
    for m in model_order:
        g = t6_data[m]["G"]
        t = t6_data[m]["T"]
        gt = t6_data[m]["GT"]
        tot = t6_data[m]["Total"]
        print(f"{m:<20} | {g:<4} | {t:<4} | {gt:<4} | {tot}")

    print("\n" + "="*60)
    print("TABLE 7: Acurácia por Categoria")
    print("="*60)
    print(f"{'Categoria':<35} | {'Acurácia':<8} | {'n'}")
    print("-" * 55)
    
    # Ordenar pelas categorias com a menor acurácia primeiro
    sorted_cats = sorted(t7_data.keys(), key=lambda k: t7_data[k]["c"] / t7_data[k]["t"] if t7_data[k]["t"] > 0 else 0)
    
    for cat in sorted_cats:
        c_val = t7_data[cat]["c"]
        t_val = t7_data[cat]["t"]
        acu = fmt_pct(c_val, t_val)
        print(f"{cat:<35} | {acu:<8} | {t_val}")
    print("\n")


if __name__ == "__main__":
    # Caminho configurado para a pasta './dados'
    target_csv = os.path.join(".", "dados", "respostas_eval.csv")
    generate_tables(target_csv)