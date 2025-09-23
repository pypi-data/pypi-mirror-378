from .api_client import ApiClient
from .articles import ArticleService
from .sources import SourcesService
from .websocket_client import WebSocketClient
from .webhook_service import WebhookService, WebhookVerificationError
from .models import ApiConfig


class FinlightApi:
    def __init__(self, config: ApiConfig):
        self.config: ApiConfig = config or ApiConfig()
        self.api_client = ApiClient(self.config)
        self.articles = ArticleService(self.api_client)
        self.websocket = WebSocketClient(self.config)
        self.sources = SourcesService(self.api_client)
        self.webhook = WebhookService()
