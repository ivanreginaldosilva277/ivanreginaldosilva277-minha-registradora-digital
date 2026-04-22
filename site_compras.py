def buscar_nome_ninja(codigo):
    memoria = carregar_memoria()
    if codigo in memoria: return memoria[codigo]

    # NOVO LINK: Base focada em produtos brasileiros
    urls = [
        f"https://openfoodfacts.org{codigo}.json",
        f"https://openfoodfacts.org{codigo}.json"
    ]
    
    for url in urls:
        try:
            r = requests.get(url, timeout=1.5) # Busca ultra rápida de 1.5 segundos
            if r.status_code == 200:
                d = r.json()
                if d.get("status") == 1:
                    p = d["product"]
                    # Prioridade total para o nome em português
                    nome = p.get("product_name_pt") or p.get("product_name") or p.get("brands")
                    if nome:
                        nome_final = nome.strip().upper()
                        memoria[codigo] = nome_final
                        with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
                            json.dump(memoria, f, ensure_ascii=False)
                        return nome_final
        except:
            continue
    return None
