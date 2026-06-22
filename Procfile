api: uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
bot: python -m bot.main
worker: celery -A worker.celery_app worker --loglevel=info
beat: celery -A worker.celery_app beat --loglevel=info
