# AtendeMax

Sistema de fila de atendimento containerizado com Docker Compose.

## Início rápido

```bash
docker compose up --build
```

| Serviço   | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost:5500      |
| API Docs  | http://localhost:8000/docs |

## Estrutura

- `backend/` — API FastAPI + PostgreSQL
- `frontend/` — Interface Nginx
- `docs/DOCUMENTACAO.pdf` — Documentação técnica para entrega

## Comandos

```bash
docker compose config      # validar configuração
docker compose down        # parar containers
docker compose down -v     # parar e apagar dados do banco
```
