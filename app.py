from dataclasses import asdict, dataclass
import io
from uuid import uuid4
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import meilisearch
import copy
import shutil
from pydantic import BaseModel, Field
from env import MEILISEARCH_MASTER_KEY, MEILISEARCH_URI
from file_upload import upload_file

from pdf import get_pdf_content_tags

app = FastAPI(
    docs_url="/docs",
    title="NoteWise V0.0.1",
)

origins = [
    "http://localhost:3000",
    "http://www.notewise.study",
    "https://www.notewise.study",
    "http://notewise.study",
    "https://notewise.study",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Initialize MeiliSearch
client = meilisearch.Client(
    MEILISEARCH_URI,
    MEILISEARCH_MASTER_KEY,
)


@app.get("/")
async def hello():
    return "Hello World"


@app.post("/files")
async def create_file(file: UploadFile):
    file_obj = io.BytesIO(file.file.read())
    try:
        pdf = await add_to_meilisearch(file.filename, file_obj)
        upload_file(file_obj, pdf)
    finally:
        file.file.close()
    return pdf


async def add_to_meilisearch(filename: str, file: io.BytesIO):
    content = await get_pdf_content_tags(filename, file)
    pdf_index = client.index("pdfs")
    pdf_page_index = client.index("pdf_pages")
    task = pdf_page_index.add_documents(
        [asdict(document) for document in content.documents], primary_key="page_id"
    )
    task = pdf_index.add_documents(asdict(content.pdf), primary_key="pdf_id")
    return content.pdf


def delete_all(index: str):
    content = client.index(index)
    content.delete_all_documents()
    content.delete()


class NoteItem(BaseModel):
    note_id: str = Field(default_factory=lambda: uuid4().__str__())
    description: str
    pdf_id: str
    page_id: str
    page_number: int


@app.post("/notes")
async def create_note(note: NoteItem):
    note_index = client.index("notes")
    task = note_index.add_documents(asdict(note), primary_key="note_id")
    return note


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app", host="0.0.0.0", port=8000, reload=True)
