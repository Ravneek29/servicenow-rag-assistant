# Backend container for Hugging Face Spaces (Docker SDK) or any container host.
FROM python:3.12-slim

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app

COPY --chown=user backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=user backend/ .

# Writable data dirs (ephemeral — sample docs re-seed on startup)
ENV CHROMA_DIR=/home/user/data/chroma \
    UPLOAD_DIR=/home/user/data/uploads \
    SEED_SAMPLES_IF_EMPTY=true \
    ANSWER_MODE=auto \
    LLM_PROVIDER=gemini

EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
