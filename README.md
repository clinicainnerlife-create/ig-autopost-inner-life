# ig-autopost — robô de postagem automática (Clínica Inner Life)

Gera as artes com sua identidade visual e publica no Instagram sozinho,
2x por semana (terça e sexta, 10h), sem você precisar clicar em nada.

## O que você precisa fazer (uma vez só)

### 1. Transformar o Instagram em conta comercial (se ainda não for)
No app: Configurações → Conta → Mudar para conta profissional → Empresa.
Precisa estar vinculado a uma Página do Facebook (crie uma se não tiver).

### 2. Criar um app no Meta for Developers
1. Acesse https://developers.facebook.com/apps → Criar app → tipo "Business"
2. No app, adicione o produto "Instagram" (Content Publishing)
3. Em Ferramentas → Graph API Explorer, gere um token com as permissões:
   `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`
4. Troque esse token de curta duração por um de **longa duração** (60 dias):
   `GET https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=SEU_APP_ID&client_secret=SEU_APP_SECRET&fb_exchange_token=TOKEN_CURTO`
5. Pegue o **IG_USER_ID**: `GET https://graph.facebook.com/v21.0/me/accounts` →
   pegue o `id` da Página → depois
   `GET https://graph.facebook.com/v21.0/{page_id}?fields=instagram_business_account`

⚠️ O token expira a cada 60 dias — você (ou eu, se me chamar) precisa renovar
manualmente, a menos que configure token de sistema (System User) numa conta
Business Manager, que não expira.

### 3. Criar o repositório no GitHub
1. Crie um repositório novo (pode ser privado)
2. Suba todos os arquivos desta pasta
3. Em Settings → Pages, ative o GitHub Pages servindo da branch `main`, pasta `/docs`
4. Em Settings → Secrets and variables → Actions, crie os secrets:
   - `IG_USER_ID`
   - `IG_ACCESS_TOKEN`
5. Edite `run_scheduled_post.py` e troque `PAGES_BASE_URL` pela URL real
   do seu GitHub Pages (aparece em Settings → Pages depois de ativado)

### 4. Pronto
O workflow em `.github/workflows/scheduled-post.yml` já roda sozinho
toda terça e sexta. Pra testar sem esperar, vá em Actions → "Post agendado
no Instagram" → Run workflow.

## Alimentando a fila de posts

Edite `content_calendar.yaml` e adicione novos itens no final, no mesmo
formato dos exemplos (sempre com `posted: false`). O robô consome na ordem,
um por execução, e marca como `posted: true` sozinho depois de publicar.

Quando a fila esvaziar, o robô simplesmente não publica nada naquele dia
(sem erro) — é seu sinal pra me chamar de novo e pedir mais posts.

## Limitação atual

Este robô publica **posts de imagem única**. Publicar carrossel (5 imagens)
via API é mais complexo (precisa criar 5 containers filhos + 1 container pai
do tipo CAROUSEL) — se quiser isso automatizado também, é só pedir que eu
estendo o script.
