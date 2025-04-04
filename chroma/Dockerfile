FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the reranker model
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('BAAI/bge-reranker-base')"

# Pre-download embedding model and convert to ctranslate2 format
RUN mkdir -p /app/bge_model_ctranslate2 && \
    python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('BAAI/bge-base-en-v1.5')" && \
    pip install -U ctranslate2 && \
    ct2-transformers-converter --model BAAI/bge-base-en-v1.5 --output_dir /app/bge_model_ctranslate2 --force

COPY . .

ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV EMBEDDING_MODEL_PATH="/app/bge_model_ctranslate2"

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"] 