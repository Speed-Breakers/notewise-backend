from dotenv import load_dotenv
import os

load_dotenv()


COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")

MEILISEARCH_URI: str = os.getenv("MEILISEARCH_URI", "")

MEILISEARCH_MASTER_KEY: str = os.getenv("MEILISEARCH_MASTER_KEY", "")

DO_SPACES_ENDPOINT: str = os.getenv("DO_SPACES_ENDPOINT", "")

DO_SPACES_PLACE: str = os.getenv("DO_SPACES_PLACE", "")

DO_SPACES_KEY: str = os.getenv("DO_SPACES_KEY", "")


DO_SPACES_SECRET: str = os.getenv("DO_SPACES_SECRET", "")
