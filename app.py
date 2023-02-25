from dataclasses import asdict, dataclass
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import meilisearch
import copy
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
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    file_upload = copy.deepcopy(file)
    pdf = await add_to_meilisearch(file.filename, file.file)
    upload_file(file_upload, pdf)
    return pdf


async def add_to_meilisearch(filename: str, file):
    content = await get_pdf_content_tags(filename, file)
    pdf_index = client.index("pdfs")
    pdf_page_index = client.index("pdf_pages")
    task = pdf_page_index.add_documents(
        [asdict(document) for document in content.documents], primary_key="page_id"
    )
    task = pdf_index.add_documents(asdict(content.pdf), primary_key="pdf_id")
    return content.pdf


# @app.get("/tasks/{task_id}")
# async def get_task(task_id: str):
#     index = client.index(DEFAULT_INDEX)
#     task = index.get_task(task_id)
#     return task


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app", host="0.0.0.0", port=8000, reload=True)
