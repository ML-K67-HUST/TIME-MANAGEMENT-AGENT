import chromadb
from config import settings
from chromadb.api import AsyncClientAPI, ClientAPI


class ChromadbClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ChromadbClient, cls).__new__(cls)
            cls._instance.client = chromadb.HttpClient(
                host=settings.chroma_endpoint,
            )
        return cls._instance

    def get_client(self) -> ClientAPI:
        return self.client


class AsyncChromadbClient:
    _instance = None
    _client = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AsyncChromadbClient, cls).__new__(cls)
        return cls._instance

    async def init(self):
        if not self._client:
            self._client = await chromadb.AsyncHttpClient(
                host=settings.chroma_endpoint,
            )
        return self

    async def get_client(self) -> AsyncClientAPI:
        if not self._client:
            await self.init()
        return self._client