import os

# Vercel Python functions can write to /tmp, so keep the MVP database there.
os.environ.setdefault("AURION_DB_PATH", "/tmp/aurion.db")

from app.main import app
