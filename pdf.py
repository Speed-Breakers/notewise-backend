from dataclasses import dataclass
from functools import partial
import io
from typing import BinaryIO, List, Set
import cohere
import PyPDF2
from env import COHERE_API_KEY
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor

# from nltk.corpus import stopwords


# cachedStopWords = stopwords.words("english")
# with open("adverbs.txt") as fp:
#     cachedStopWords += fp.readlines()

# cohere_client = cohere.Client(COHERE_API_KEY)


@dataclass
class PDFDocument:
    name: str
    author: str
    pdf_id: str
    page_num: int | None = None
    pdf_size: int | None = None


@dataclass
class TagResult:
    pdf_name: str
    pdf_id: str
    page_id: str
    page_num: int | None = None
    summary: str | None = None

    @staticmethod
    def from_pdf_document(pdf_document: PDFDocument):
        return TagResult(
            pdf_name=pdf_document.name,
            pdf_id=pdf_document.pdf_id,
            page_num=pdf_document.page_num,
            page_id=uuid4().__str__(),
        )


def gettags(
    pdf_document: PDFDocument, page_num: int, page: PyPDF2.PageObject
) -> TagResult:
    prompt = fix_text(page.extract_text())

    result = TagResult.from_pdf_document(pdf_document)
    result.page_num = page_num

    # if len(prompt) < 250:
    #     result.summary = prompt
    #     return result

    # # response = cohere_client.summarize(
    # #     text=prompt, model="summarize-xlarge", length="short"
    # # )

    # result.summary = response.summary
    result.summary = prompt

    return result


def fix_text(text: str) -> str:
    text = text.replace("   ", " ").replace(".", "")
    return text


@dataclass
class ContentTagResult:
    documents: List[TagResult]
    pdf: PDFDocument


async def get_pdf_content_tags(pdf_name: str, file: io.BytesIO):
    pdf_file = PyPDF2.PdfReader(file)

    pdf_document = PDFDocument(
        name=pdf_name,
        author=pdf_file.metadata.author,
        pdf_id=uuid4().__str__(),
        page_num=len(pdf_file.pages),
    )

    partial_gettags = partial(gettags, pdf_document)

    with ThreadPoolExecutor(max_workers=10) as executor:
        result = executor.map(
            partial_gettags, list(range(1, pdf_document.page_num + 1)), pdf_file.pages
        )

    return ContentTagResult(documents=list(result), pdf=pdf_document)
