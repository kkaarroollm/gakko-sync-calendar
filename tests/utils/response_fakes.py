import requests


def fake_response(
    url: str = "https://fake.local", text: str = "<html></html>", status_code: int = 200, headers: dict | None = None
) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = text.encode("utf-8")
    response.url = url
    if headers:
        response.headers.update(headers)
    return response
