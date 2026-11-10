# Deployment guide

## Recommended path

Deploy the FastAPI container to Render, Railway, Fly.io, or an AWS service such as App Runner. Vercel can run FastAPI as a Python Function, but its function-duration and bundle constraints make it a less natural first home for this single-container backend. See the official [Vercel FastAPI guide](https://vercel.com/docs/frameworks/backend/fastapi) and [Render web service guide](https://render.com/docs/web-services).

Use the included Dockerfile and `render.yaml` blueprint. Set `DATABASE_URL` and any future provider keys only in the platform secret settings. The SQLite file is a local-demo choice; Render documents that its filesystem is ephemeral without a persistent disk, and a disk is attached to only one service instance. Pair the public version with managed PostgreSQL before persistent writes or multiple instances.

## Pre-deploy checklist

- Run `pytest` locally.
- Confirm `.env` is ignored and no secret is committed.
- Set an allowed production origin when adding CORS.
- Add authentication and tenant access checks before connecting real business data.
- Switch trace storage from memory to a database or observability platform.
- Configure health checks against `/api/health`.

## GitHub

```powershell
git init
git add .
git commit -m "Build Business Performance AI portfolio project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/business-performance-ai.git
git push -u origin main
```
