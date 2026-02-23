import os
import uuid
from dotenv import load_dotenv
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from tqdm import tqdm

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

DATA_FOLDER = "data/code_docs"


def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text = ""

    for i in range(len(reader.pages)):
        try:
            page = reader.pages[i]
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        except Exception as e:
            print(f"⚠️ Skipping page {i} due to error: {e}")
            continue

    return text


def chunk_text(text, chunk_size=800):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        if len(chunk.strip()) > 100:
            chunks.append(chunk)
    return chunks


def upload_chunks(chunks, source, batch_size=100):
    vectors = []

    for chunk in chunks:
        embedding = model.encode(chunk).tolist()

        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {
                "text": chunk,
                "source": source
            }
        })

    # Upload in batches
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Uploaded batch {i // batch_size + 1}")


def process_pdf(file_path):
    print(f"\nProcessing: {file_path}")

    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)

    print(f"Total Chunks: {len(chunks)}")

    upload_chunks(chunks, source=os.path.basename(file_path))


def main():
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".pdf"):
            file_path = os.path.join(DATA_FOLDER, filename)
            process_pdf(file_path)


if __name__ == "__main__":
    main()