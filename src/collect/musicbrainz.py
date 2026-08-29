"""
Coleta de dados de artistas via MusicBrainz API.
Rate limit: 1 requisição por segundo (obrigatório).
"""
import requests
import time

HEADERS = {"User-Agent": "EDA2-MusicSearch/1.0 (https://github.com/eda2-2026/G8_Busca_EDA2-2026.2)"}

# Ajuste essa lista com os gêneros que vocês combinaram usar
GENEROS_SEMENTE = [
    "rock", "jazz", "samba", "mpb", "funk", "metal", "pop",
    "reggae", "punk", "blues", "eletronica", "hip hop",
    "forro", "sertanejo", "bossa nova", "indie", "classica",
    "country", "soul", "disco",
]


def buscar_artistas_musicbrainz(termo, limite=25, pais="BR"):
    """Busca artistas na API do MusicBrainz por um termo (ex: um gênero),
    filtrando por país de origem via sintaxe de query do MusicBrainz
    (campo 'country'). Isso restringe os resultados a artistas
    brasileiros, evitando que a busca por gênero traga só nomes
    internacionais em inglês."""
    url = "https://musicbrainz.org/ws/2/artist/"
    query = f'tag:"{termo}"'
    if pais:
        query += f' AND country:{pais}'
    params = {"query": query, "fmt": "json", "limit": limite}
    resp = requests.get(url, params=params, headers=HEADERS)
    resp.raise_for_status()
    time.sleep(1)  # respeitar rate limit
    return resp.json().get("artists", [])


# Entidades "especiais" do MusicBrainz — não são artistas de verdade,
# são placeholders para compilações/casos sem artista definido.
# Convenção do MusicBrainz: nomes entre colchetes ou "Various Artists".
def _e_entidade_especial(nome):
    if not nome:
        return True
    nome_lower = nome.strip().lower()
    if nome_lower == "various artists":
        return True
    if nome.strip().startswith("[") and nome.strip().endswith("]"):
        return True
    return False


def extrair_dados(artista_json):
    """Converte o JSON bruto da API no formato do schema do projeto.
    Retorna None se for uma entidade especial (deve ser descartada)."""
    nome = artista_json.get("name")
    if _e_entidade_especial(nome):
        return None

    # Ordena as tags por contagem (quantas vezes foram aplicadas) e pega
    # só as mais relevantes — evita poluir "generos" com tags de ruído
    # que têm contagem baixa/zero.
    tags_ordenadas = sorted(
        artista_json.get("tags", []),
        key=lambda t: t.get("count", 0),
        reverse=True,
    )
    generos = [t["name"] for t in tags_ordenadas[:8]]

    return {
        "id": artista_json.get("id"),
        "nome": nome,
        "pais": artista_json.get("country"),
        "ano_formacao": artista_json.get("life-span", {}).get("begin"),
        "generos": generos,
        "tags_lastfm": [],   # preenchido depois, se usar Last.fm
        "ouvintes": None,    # preenchido depois, se usar Last.fm
    }


def coletar_todos(generos=None, limite_por_termo=50, pais="BR"):
    """Roda a coleta completa: busca cada gênero-semente (filtrando por
    país) e junta os resultados, descartando duplicados pelo id e
    entidades especiais (ex: 'Various Artists')."""
    generos = generos or GENEROS_SEMENTE
    todos_artistas = {}

    for i, genero in enumerate(generos, start=1):
        print(f"[{i}/{len(generos)}] Buscando '{genero}' (país={pais})...")
        try:
            resultados = buscar_artistas_musicbrainz(genero, limite=limite_por_termo, pais=pais)
        except requests.exceptions.RequestException as e:
            print(f"  Erro ao buscar '{genero}': {e}")
            continue

        novos = 0
        for a in resultados:
            dados = extrair_dados(a)
            if dados is None:
                continue  # entidade especial (ex: "Various Artists"), descartada
            if dados["id"] and dados["id"] not in todos_artistas:
                todos_artistas[dados["id"]] = dados
                novos += 1
        print(f"  +{novos} artistas novos (total: {len(todos_artistas)})")

    return list(todos_artistas.values())


if __name__ == "__main__":
    # Teste rápido com 1 gênero antes de rodar a coleta completa
    resultados = buscar_artistas_musicbrainz("rock", limite=5)
    for r in resultados:
        print(extrair_dados(r))