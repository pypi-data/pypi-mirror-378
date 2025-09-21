from typing import Generic, Type
from urllib.parse import urljoin, urlparse


from .api_client import ApiClient, HttpResponse
from .validators import BaseApiResponseValidator


class BaseApiSection(Generic[HttpResponse]):
    base_url = None

    def __init__(self, client: ApiClient[HttpResponse],
                 validator_class: Type[BaseApiResponseValidator] = BaseApiResponseValidator):
        self.client: ApiClient[HttpResponse] = client
        self.validator_class = validator_class

    def url_join(self, path: str, base: str = None):
        if not base:
            if self.base_url:
                base = self.base_url
            else:
                raise Exception
        # Проверяем, что path — не абсолютный URL
        parsed = urlparse(path)
        if parsed.scheme or parsed.netloc:
            raise ValueError(f"Path '{path}' is absolute URL, cannot join safely")
        return urljoin(base, path)

    def validator(self, response: HttpResponse) -> BaseApiResponseValidator[HttpResponse]:
        return self.validator_class(response)