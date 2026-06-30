# Frontend POC Hugo

Vue 3 (Vite) + Pinia + Vue Router. Interface minimale : login, tableau de bord (groupes).

## Dev

```bash
npm install
npm run dev
```

Ouvre http://localhost:5173. Le proxy Vite envoie `/api` vers le backend (port 8000).

## Build (pour déploiement)

```bash
npm run build
```

Génère `dist/`. Nginx sert ce dossier et proxy `/api` vers l’API. Définir `VITE_API_URL=/api` en production (déjà dans `.env.production`).
