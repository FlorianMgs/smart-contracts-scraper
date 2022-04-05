import json
import requests
from bs4 import BeautifulSoup
from web3 import Web3
import re


class Scraper:
    def __init__(self):
        self.settings = json.load(open("settings.json"))
        self.web3 = Web3(Web3.WebsocketProvider(self.settings["rpc_endpoint"]))
        self.base_url = self.settings["website_url"]

    @property
    def session(self):
        return requests.Session()

    def get_links_from_html(self, text: str) -> dict:
        links = {
            "html": [],
            "scripts": [],
            "files": []
        }
        soup = BeautifulSoup(text, 'lxml')

        # Getting HTML pages
        for link in soup.find_all('a'):
            if self.base_url.replace("https://", "").replace("www", "") in link.get('href'):
                links["html"].append(link.get('href'))

        # Getting scripts
        for script_link in soup.find_all('script'):
            if script_link.get('src'):
                links['scripts'].append(script_link.get('src'))
            else:
                links['files'].append(script_link)

        # Getting CSS
        for css_file in soup.find_all('link', attrs={'rel': 'stylesheet'}):
            if css_file.get('href'):
                links['scripts'].append(css_file.get('href'))
            else:
                links['files'].append(css_file)
        return links

    def scrap_links_from_page(self) -> list:
        # formatting url
        if self.base_url[-1] == "/":
            self.base_url = self.base_url[:-1]

        urls_to_scrape = [self.base_url]
        files = []

        print(f"Scrapping complete source code of {self.base_url}...")

        for url in urls_to_scrape:
            resp = self.session.get(url).text
            files.append(resp)
            found_links = self.get_links_from_html(resp)
            for link in found_links['html']:
                if link not in urls_to_scrape:
                    urls_to_scrape.append(link)
            for link in found_links['scripts']:
                files.append(self.session.get(self.base_url + link).text)

        return files

    def search_contract_address(self) -> list:
        address_pattern = re.compile("0x[a-fA-F0-9]{40}")
        scrapped_source_code = ' '.join(self.scrap_links_from_page())
        results = []

        print("Searching for smart contracts...")

        for match in re.finditer(address_pattern, scrapped_source_code):
            if self.web3.eth.get_code(self.web3.toChecksumAddress(match.group(0))):
                print("Smart Contract found: ", match.group(0))
                results.append(match.group(0).lower())

        self.write_results(results)
        return results

    @staticmethod
    def write_results(results: list):
        if results:
            result_file = open('results.txt', 'w+')
            results = list(dict.fromkeys(results))
            for address in results:
                result_file.write(address + '\n')
            print("Results saved in results.txt")
        else:
            print("No smart contracts found...")
