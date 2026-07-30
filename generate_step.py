"""
ETAPA 1 do workflow: só gera a(s) imagem(ns) e escolhe o próximo post da fila.
Não publica ainda -- isso é feito depois que as imagens já estiverem
disponíveis publicamente no GitHub Pages (etapa 2, publish_step.py).

Suporta dois tipos de post:
  - type: image     -> uma imagem só, gerada a partir do template
  - type: carousel  -> várias imagens, cada uma vinda de um arquivo .svg pronto

Salva o estado (qual post foi escolhido, nomes das imagens) num arquivo
temporário `.next_post.json` pra a etapa 2 usar.
"""
import json
import sys
from pathlib import Path

import yaml

from generate_post import generate, generate_carousel

ROOT = Path(__file__).parent
CALENDAR_PATH = ROOT / "content_calendar.yaml"
GENERATED_DIR = ROOT / "docs" / "generated"
ASSETS_DIR = ROOT / "assets"
STATE_PATH = ROOT / ".next_post.json"


def main():
    calendar = yaml.safe_load(CALENDAR_PATH.read_text(encoding="utf-8"))

    next_post = next((p for p in calendar if not p["posted"]), None)
    if next_post is None:
        print("Nenhum post pendente na fila. Adicione mais itens no content_calendar.yaml.")
        STATE_PATH.write_text(json.dumps({"skip": True}), encoding="utf-8")
        sys.exit(0)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    post_type = next_post.get("type", "image")

    if post_type == "carousel":
        paths = generate_carousel(next_post, GENERATED_DIR, ASSETS_DIR)
        print(f"Imagens geradas: {[p.name for p in paths]}")
        state = {
            "skip": False,
            "type": "carousel",
            "post_id": next_post["id"],
            "image_filenames": [p.name for p in paths],
            "caption": next_post["caption"],
        }
    else:
        png_path = generate(next_post, GENERATED_DIR)
        print(f"Imagem gerada: {png_path}")
        state = {
            "skip": False,
            "type": "image",
            "post_id": next_post["id"],
            "image_filenames": [png_path.name],
            "caption": next_post["caption"],
        }

    STATE_PATH.write_text(json.dumps(state), encoding="utf-8")


if __name__ == "__main__":
    main()
