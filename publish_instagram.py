"""
Publica uma imagem no Instagram via Graph API (Content Publishing).
Precisa de:
  - IG_USER_ID: o ID da conta comercial do Instagram (não é o @, é um número)
  - IG_ACCESS_TOKEN: token de acesso de longa duração (60 dias, renovável)
  - image_url: URL PÚBLICA da imagem (a API não aceita upload de arquivo local)

Documentação oficial: https://developers.facebook.com/docs/instagram-platform/content-publishing
"""
import os
import time
import requests

GRAPH_API_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def publish_image_post(image_url: str, caption: str) -> str:
    ig_user_id = os.environ["IG_USER_ID"]
    access_token = os.environ["IG_ACCESS_TOKEN"]

    # 1. Cria o "container" de mídia (o Instagram baixa a imagem da URL)
    container_resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": access_token,
        },
        timeout=30,
    )
    container_resp.raise_for_status()
    creation_id = container_resp.json()["id"]

    # 2. Espera o container ficar pronto (status_code = FINISHED)
    status = None
    for _ in range(10):
        status_resp = requests.get(
            f"{GRAPH_BASE}/{creation_id}",
            params={"fields": "status_code", "access_token": access_token},
            timeout=30,
        )
        status = status_resp.json().get("status_code")
        if status == "FINISHED":
            break
        time.sleep(3)

    if status != "FINISHED":
        raise RuntimeError(f"Container não ficou pronto a tempo (status: {status})")

    # 3. Publica de fato
    publish_resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": access_token},
        timeout=30,
    )
    publish_resp.raise_for_status()
    return publish_resp.json()["id"]
