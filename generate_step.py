"""
ETAPA 1 do workflow: só gera a imagem e escolhe o próximo post da fila.
Não publica ainda -- isso é feito depois que a imagem já estiver
disponível publicamente no GitHub Pages (etapa 2, publish_step.py).

Salva o estado (qual post foi escolhido, caminho da imagem) num arquivo
temporário `.next_post.json` pra a etapa 2 usar.
"""
import json
import sys
from pathlib import Path

import yaml

from generate_post import generate

ROOT = Path(__file__).parent
CALENDAR_PATH = ROOT / "content_calendar.yaml"
GENERATED_DIR = ROOT / "docs" / "generated"
STATE_PATH = ROOT / ".next_post.json"


def main():
    calendar = yaml.safe_load(CALENDAR_PATH.read_text(encoding="utf-8"))

    next_post = next((p for p in calendar if not p["posted"]), None)
    if next_post is None:
        print("Nenhum post pendente na fila. Adicione mais itens no content_calendar.yaml.")
        # Sinaliza pro workflow pular as próximas etapas
        STATE_PATH.write_text(json.dumps({"skip": True}), encoding="utf-8")
        sys.exit(0)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    png_path = generate(next_post, GENERATED_DIR)
    print(f"Imagem gerada: {png_path}")

    STATE_PATH.write_text(
        json.dumps(
            {
                "skip": False,
                "post_id": next_post["id"],
                "image_filename": png_path.name,
                "caption": next_post["caption"],
            }
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
