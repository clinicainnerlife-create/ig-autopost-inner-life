"""
Orquestrador rodado pelo GitHub Actions 2x por semana.

Fluxo:
  1. Lê content_calendar.yaml e pega o primeiro post com posted: false
  2. Gera o PNG a partir do template
  3. Salva em docs/generated/ (essa pasta é publicada pelo GitHub Pages,
     então vira uma URL pública automaticamente)
  4. Publica no Instagram apontando pra essa URL pública
  5. Marca o post como posted: true no YAML (o workflow faz commit disso)

Pré-requisito: GitHub Pages ativado no repositório, servindo a partir de /docs.
"""
import sys
from pathlib import Path

import yaml

from generate_post import generate
from publish_instagram import publish_image_post

ROOT = Path(__file__).parent
CALENDAR_PATH = ROOT / "content_calendar.yaml"
GENERATED_DIR = ROOT / "docs" / "generated"

# Troque pelo seu usuário/repositório reais depois de criar o repo no GitHub
PAGES_BASE_URL = "https://SEU_USUARIO.github.io/SEU_REPOSITORIO"


def main():
    calendar = yaml.safe_load(CALENDAR_PATH.read_text(encoding="utf-8"))

    next_post = next((p for p in calendar if not p["posted"]), None)
    if next_post is None:
        print("Nenhum post pendente na fila. Adicione mais itens no content_calendar.yaml.")
        sys.exit(0)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    png_path = generate(next_post, GENERATED_DIR)
    print(f"Imagem gerada: {png_path}")

    image_url = f"{PAGES_BASE_URL}/generated/{png_path.name}"
    print(f"URL pública esperada: {image_url}")
    print("Publicando no Instagram...")

    media_id = publish_image_post(image_url, next_post["caption"])
    print(f"Publicado! media_id = {media_id}")

    next_post["posted"] = True
    CALENDAR_PATH.write_text(
        yaml.dump(calendar, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
