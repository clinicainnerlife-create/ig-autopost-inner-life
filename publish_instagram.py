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
# Tokens gerados via "API Setup with Instagram Business Login" (os que começam
# com IGAAT...) falam com graph.instagram.com. Só tokens vindos de Facebook
# Login (Página conectada) usam graph.facebook.com.
GRAPH_BASE = f"https://graph.instagram.com/{GRAPH_API_VERSION}"


def _create_container(data: dict) -> str:
    ig_user_id = os.environ["IG_USER_ID"]
    access_token = os.environ["IG_ACCESS_TOKEN"]

    resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media",
        data={**data, "access_token": access_token},
        timeout=30,
    )
    if not resp.ok:
        print(f"Resposta da Meta: {resp.text}")
    resp.raise_for_status()
    return resp.json()["id"]


def _wait_until_finished(creation_id: str, attempts: int = 10, delay_seconds: int = 3) -> None:
    access_token = os.environ["IG_ACCESS_TOKEN"]
    status = None
    for _ in range(attempts):
        status_resp = requests.get(
            f"{GRAPH_BASE}/{creation_id}",
            params={"fields": "status_code", "access_token": access_token},
            timeout=30,
        )
        status = status_resp.json().get("status_code")
        if status == "FINISHED":
            return
        time.sleep(delay_seconds)
    raise RuntimeError(f"Container {creation_id} não ficou pronto a tempo (status: {status})")


def _publish_container(creation_id: str) -> str:
    ig_user_id = os.environ["IG_USER_ID"]
    access_token = os.environ["IG_ACCESS_TOKEN"]

    publish_resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": access_token},
        timeout=30,
    )
    if not publish_resp.ok:
        print(f"Resposta da Meta: {publish_resp.text}")
    publish_resp.raise_for_status()
    return publish_resp.json()["id"]


def publish_image_post(image_url: str, caption: str) -> str:
    creation_id = _create_container({"image_url": image_url, "caption": caption})
    _wait_until_finished(creation_id)
    return _publish_container(creation_id)


def publish_carousel_post(image_urls: list[str], caption: str) -> str:
    """Publica um carrossel: cria um container 'filho' pra cada imagem
    (is_carousel_item=true), espera todos ficarem prontos, cria o
    container 'pai' do tipo CAROUSEL apontando pros filhos, e publica."""
    child_ids = []
    for url in image_urls:
        child_id = _create_container({"image_url": url, "is_carousel_item": "true"})
        _wait_until_finished(child_id)
        child_ids.append(child_id)
        print(f"Slide pronto: {child_id}")

    parent_id = _create_container(
        {
            "media_type": "CAROUSEL",
            "caption": caption,
            "children": ",".join(child_ids),
        }
    )
    _wait_until_finished(parent_id)
    return _publish_container(parent_id)
