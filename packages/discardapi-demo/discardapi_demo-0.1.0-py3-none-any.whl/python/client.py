import requests

BASE_URL = "https://discardapi.dpdns.org/api"

class DiscardAPI:
    def __init__(self, apikey: str):
        self.apikey = apikey

    def markdown_to_html(self, markdown: str):
        url = f"{BASE_URL}/markdown?apikey={self.apikey}"
        resp = requests.post(url, json={"markdown": markdown})
        return resp.json()
      
