"""
ETAPA 2 do workflow: roda DEPOIS que a imagem já foi commitada e enviada
pro GitHub Pages. Espera a URL ficar acessível (com tentativas), publica
no Instagram, e marca o post como enviado no content_calendar.yaml.
"""
import json
import sys
import time
from pathlib import Path

import requests
import yaml

from publish_instagram import publish_image_post

ROOT = Path(__file__).parent
CALENDAR_PATH = ROOT / "content_calendar.yaml"
STATE_PATH = ROOT / ".next_post.json"

# Já trocado pelo domínio real do GitHub Pages da clínica
PAGES_BASE_URL = "https://clinicainnerlife-create.github.io/ig-autopost-inner-life"


def wait_until_public(url: str, attempts: int = 10, delay_seconds: int = 6) -> bool:
    for i in range(attempts):
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True)
            if resp.status_code == 200:
                print(f"URL confirmada no ar: {url}")
                return True
        except requests.RequestException:
            pass
        print(f"Ainda não disponível (tentativa {i + 1}/{attempts}), esperando {delay_seconds}s...")
        time.sleep(delay_seconds)
    return False


def main():
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if state.get("skip"):
        print("Nada pra publicar nesta execução.")
        sys.exit(0)

    image_url = f"{PAGES_BASE_URL}/generated/{state['image_filename']}"
    print(f"Aguardando a imagem ficar pública: {image_url}")

    if not wait_until_public(image_url):
        print("ERRO: a imagem não ficou disponível a tempo. Abortando publicação.")
        sys.exit(1)

    print("Publicando no Instagram...")
    media_id = publish_image_post(image_url, state["caption"])
    print(f"Publicado! media_id = {media_id}")

    calendar = yaml.safe_load(CALENDAR_PATH.read_text(encoding="utf-8"))
    for post in calendar:
        if post["id"] == state["post_id"]:
            post["posted"] = True
            break

    CALENDAR_PATH.write_text(
        yaml.dump(calendar, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
