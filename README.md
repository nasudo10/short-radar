# Radar de Shorts Virais

Ferramenta que todo dia busca Shorts do YouTube em inglês e espanhol,
publicados nas últimas 48h, e ranqueia pelos que estão bombando mais
rápido (visualizações por hora). Entrega os 20-30 melhores num
dashboard web.

Custo: **R$ 0**. Tudo roda em serviços gratuitos (GitHub Actions +
GitHub Pages) e a YouTube Data API tem uma cota diária gratuita
generosa para esse volume de uso.

---

## Passo 1 — Criar a API Key do YouTube (10 min)

1. Acesse https://console.cloud.google.com/
2. Crie um projeto novo (canto superior esquerdo → "Novo projeto").
3. No menu, vá em **APIs e serviços → Biblioteca**.
4. Procure por **YouTube Data API v3** e clique em **Ativar**.
5. Vá em **APIs e serviços → Credenciais → Criar credenciais → Chave de API**.
6. Copie a chave gerada (algo como `AIzaSy...`). Guarde, você vai usar no Passo 3.

> Cota gratuita: 10.000 unidades/dia. Cada busca do nosso script
> consome pouco, então rodar 1x por dia é bem tranquilo dentro do limite gratuito.

## Passo 2 — Criar o repositório no GitHub

1. Crie uma conta gratuita em https://github.com (se ainda não tiver).
2. Crie um repositório novo, por exemplo `youtube-shorts-radar`.
3. Suba todos os arquivos desta pasta para esse repositório
   (pode arrastar e soltar pela interface web do GitHub, em "Add file → Upload files").

## Passo 3 — Guardar a API Key com segurança

1. No repositório, vá em **Settings → Secrets and variables → Actions**.
2. Clique em **New repository secret**.
3. Nome: `YOUTUBE_API_KEY`
4. Valor: cole a chave do Passo 1.
5. Salve.

(Isso mantém sua chave privada — ela nunca aparece no código.)

## Passo 4 — Ativar a atualização automática diária

O arquivo `.github/workflows/daily.yml` já está configurado para
rodar todo dia às 09h (horário de Brasília). Ele roda sozinho, mas
você pode forçar a primeira execução manualmente:

1. Vá na aba **Actions** do repositório.
2. Clique no workflow "Radar diário de Shorts virais".
3. Clique em **Run workflow** → **Run workflow**.
4. Aguarde ~1 minuto. Isso vai gerar o arquivo `data/data.json`.

## Passo 5 — Publicar o dashboard (GitHub Pages, grátis)

1. Vá em **Settings → Pages**.
2. Em "Source", selecione a branch `main` e a pasta `/ (root)`.
3. Salve. Em ~1 minuto sua página estará no ar em:
   `https://SEU-USUARIO.github.io/youtube-shorts-radar/`

Pronto — esse link é o seu dashboard. Ele se atualiza sozinho todo dia.

---

## Ajustes que você pode querer fazer

Abra `fetch_shorts.py` e mexa nestas variáveis no topo do arquivo:

- `MIN_VIEWS` — visualizações mínimas para um vídeo entrar na lista (hoje: 20.000)
- `TOP_N` — quantos vídeos entregar por dia (hoje: 30)
- `HOURS_WINDOW` — janela de tempo (hoje: 48h)
- `LANGUAGES` — idiomas buscados (hoje: `["en", "es"]`)

Depois de editar, é só subir a alteração pro GitHub — o próximo
disparo automático já usa a configuração nova.

## Rodando localmente (opcional, pra testar antes)

```bash
pip install requests
export YOUTUBE_API_KEY="sua_chave_aqui"
python fetch_shorts.py
```

Isso gera `data/data.json` na sua máquina, que você pode abrir junto
com `index.html` num servidor local (ex: `python -m http.server`).
