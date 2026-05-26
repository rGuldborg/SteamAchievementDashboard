# Steam Achievement Dashboard

Et dashboard der viser Steam-achievements for dine spil, med AI-estimat for tid til 100% completion.

## Opsætning

Opret en `.env` fil i roden af projektet med følgende nøgler:

```
STEAM_API_KEY=XXXXX
MISTRAL_API_KEY=XXXXX
```

- **Steam API key:** hentes på [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)
- **Mistral API key:** hentes på [console.mistral.ai](https://console.mistral.ai)

## Start

```bash
docker compose up --build
```

Åbn derefter [http://localhost:8501](http://localhost:8501) i din browser.
