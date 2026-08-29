"""
Cache local dos dados coletados — evita chamadas repetidas à API.
"""
import json
import os


def salvar_cache(dados, caminho="data/raw/artistas.json"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Salvo: {len(dados)} artistas em {caminho}")


def carregar_cache(caminho="data/raw/artistas.json"):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)
