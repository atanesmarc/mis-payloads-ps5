# Mis Payloads PS5

Catàleg personal de payloads PS5 (`.elf`) en format `payloads.json`, servit via GitHub Pages.

Només releases estables (no alfa/beta/prerelease). Afegir una entrada nova:

1. Consultar l'API de releases del repo origen: `curl -s "https://api.github.com/repos/<owner>/<repo>/releases/tags/<tag>"`
2. Comprovar `"prerelease": false`
3. Copiar `browser_download_url`, `digest` (checksum) i `size` de l'asset `.elf`
4. Afegir entrada a `payloads.json` seguint el mateix format

## Format

Veure `payloads.json` — cada entrada té `name`, `filename`, `url`, `source`, `source_direct`, `description`, `last_update`, `version`, `category`, `checksum`.
