import asyncio
import aiohttp
import cachetools.func
import concurrent
import json
import random
import requests
import re
import string
import bs4
from functools import partial

from .utils import a_named_timeit, named_timeit


class TripAdviserHotelsSearch:
    """
    Just a holder for collection of methods for scrape TripAdvisor site data
    """

    hotel_name_re = re.compile(r'\s*\d+\.\s+')
    host = 'https://www.tripadvisor.com'
    items_per_page = 30
    max_workers = 5

    BASE_HEADERS = {
        'authority': 'www.tripadvisor.com',
        'accept-language': 'en-US;q=0.9',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    }

    @cachetools.func.ttl_cache(maxsize=128, ttl=3600)
    def get_hotel_list_request_details(self, query: str) -> dict:
        """
        Get hotel list url details
        """
        url = f"{self.host}/data/graphql/ids"
        payload = json.dumps(
            [
                {
                    "query": "5eec1d8288aa8741918a2a5051d289ef",
                    "variables": {
                        "request": {
                            "query": query,
                            "limit": 10,
                            "scope": "WORLDWIDE",
                            "locale": "en-US",
                            "types": [
                                "LOCATION",
                            ],
                            "locationTypes": [
                                "GEO",
                            ],
                        }
                    }
                }
            ]
        )
        headers = {
            'accept': '*/*',
            'origin': self.host,
            'referer': f'{self.host}/',
            'sec-fetch-mode': 'cors',
            'content-type': 'application/json',
            'x-requested-by': "".join(random.choice(string.ascii_lowercase + string.digits) for i in range(64))
        }

        resp = requests.get(self.host, headers=self.BASE_HEADERS)
        cookies = {'TADCID': resp.cookies.get('TADCID')}

        #         cookies = {
        # #             'TADCID': 'O1-nvQXDmYB_BQAGABQCXdElnkGETRW-Svh01l3nWnTL-nlwUj5rbXCZSrEmwslQtXhktK9knGzJfJiCfGm6VwwoxX5RWrfZHZk'
        #             'TADCID': 'o_PeJUSKY9ywtLK6ABQCXdElnkGETRW-Svh01l3nWnTNRPP_mhdsCBwAJ8gvHJqqAEL9xfTYwXWHUcoNjzmmXDiAx340YTGTg_g'
        # #             'TADCID': 'l2Xa-m6HXTLOajC0ABQCXdElnkGETRW-Svh01l3nWnS-EbHdhWzwTbjik0qpqbxIXtRCTi9x6jCQM2rjZguRdy8dP2Ez1kZUYKs'
        #         }
        return {'url': url, 'headers': headers, 'cookies': cookies, 'data': payload}

    def get_hotel_list_url(self, query: str, page: int = 1) -> str:
        """
        Get url which provides list of hotels (30 items) - it's like an API on TripAdvisor site
        """
        request_details = self.get_hotel_list_request_details(query)
        request_details['headers'].update(self.BASE_HEADERS)
        response = requests.post(**request_details)
        data = response.json()
        url = data[0]["data"]["Typeahead_autocomplete"]["results"][0]["details"]["HOTELS_URL"]
        if page > 1:
            url_parts = url.split('-')
            url_parts.insert(2, f'oa{(page - 1) * self.items_per_page}')
            url = '-'.join(url_parts)
        return self.host + url

    def parse_hotel_list_page(self, soup: bs4.BeautifulSoup) -> list[dict]:
        """
        Get initial data from hotel list page - i.e. ID, url, hotel name
        """
        data = []

        json_data_container = soup.select('div[data-hotels-data]')
        if json_data_container:
            if len(json_data_container) != 1:
                raise RuntimeError('Hotels data container Not found')
            try:
                _data = json.loads(json_data_container[0].attrs['data-hotels-data'])['hotels']
            except KeyError:
                raise RuntimeError('Hotels data container has wrong structure')

            for item in _data:
                data.append(
                    {
                        'id': item['id'],
                        'name': item['name'],
                        'url': self.host + item['detailUrl'],
                        'rating': item['bubbleRating'],
                        'reviews': item['numReviews'],
                    }
                )
        else:
            for a in soup.select('div[data-automation]>a[href^="/Hotel_Review"]'):
                data.append(
                    {
                        "id": a.attrs.get('id', '').split("_")[-1] or None,
                        "url": self.host + a.attrs['href'],
                        "name": self.hotel_name_re.sub('', a.text),
                    }
                )
        return data

    @staticmethod
    def get_description(soup) -> str:
        descr_html = soup.select_one('[data-ssrev-handlers*=locationDescription]')
        if descr_html:
            descr_container = str(descr_html).replace('&quot;', '"')
            descr_search = re.search(r'locationDescription":"(.+?)","', descr_container)
            if descr_search:
                return descr_search.groups()[0]

    def parse_hotel_page(self, html: str, initial_data: tuple | dict) -> dict:
        if isinstance(initial_data, tuple):
            initial_data = dict(initial_data)

        soup = bs4.BeautifulSoup(html, 'html.parser')

        description = self.get_description(soup)

        reg = r'reviewSummary\\":{\\"rating\\":([\d\.]+),\\"count\\":(\d+)},\\"accommodationCategory\\":\\"(?:HOTEL|OTHER)\\",\\"popIndexDetails\\":{\\"popIndexRank\\":(\d+),\\"popIndexTotal\\":(\d+)'
        reg_search = re.search(reg, html)
        if reg_search:
            rating, reviews, rank, rank_total = reg_search.groups()
        else:
            rating = reviews = rank = rank_total = None

        stars_html = soup.select_one("svg[aria-label*='of 5']")
        if stars_html:
            stars = float(stars_html.attrs['aria-label'].split()[0])
        else:
            stars = None

        return {
            **initial_data,
            'description': description,
            'rating': rating,
            'reviews': reviews,
            'rank': rank,
            'rank_total': rank_total,
            'stars': stars
        }

    async def async_get_html_page(self, url: str, session: aiohttp.ClientSession):
        headers = {
            'accept': 'text/html',
        }
        async with session.get(url, headers=headers) as response:
            return await response.text()

    def sync_get_html_page(self, url: str):
        headers = {
            **self.BASE_HEADERS,
            'accept': 'text/html',
        }
        response = requests.get(url, headers=headers)
        return response.text

    @named_timeit(name='Step 2: get html pages')
    def threading_get_html_pages(self, hotels_initial_data: list[dict]):
        urls = [i['url'] for i in hotels_initial_data]
        url_to_html = dict()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.sync_get_html_page, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
                else:
                    url_to_html[url] = data
        return [url_to_html[i] for i in urls]

    def seq_get_and_parse_html_page(self, hotel_data: dict):
        html = self.sync_get_html_page(hotel_data['url'])
        return self.parse_hotel_page(html, hotel_data)

    @named_timeit(name='Step 2,3: get html pages, parse/extract')
    def multiprocessing_get_html_pages(self, hotels_initial_data: list[dict]):
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            result = list(executor.map(self.seq_get_and_parse_html_page, hotels_initial_data))
        return result

    @named_timeit(name='Step 2: get html pages')
    def seq_get_html_pages(self, hotels_initial_data: list[dict]):
        return [self.sync_get_html_page(i['url']) for i in hotels_initial_data]

    @a_named_timeit(name='Step 2: get html pages')
    async def asyncio_get_html_pages(self, hotels_initial_data: list[dict]):
        async with aiohttp.ClientSession(headers=self.BASE_HEADERS) as session:
            return await asyncio.gather(
                *[self.async_get_html_page(hotel_data['url'], session) for hotel_data in hotels_initial_data],
                return_exceptions=True)

    @named_timeit(name='Step 1: get url list')
    def get_initial_hotels_data(self, query: str, page: int):
        hotel_list_url = self.get_hotel_list_url(query, page)
        hotel_list_html = self.sync_get_html_page(hotel_list_url)
        soup = bs4.BeautifulSoup(hotel_list_html, 'html.parser')
        hotels_initial_data = self.parse_hotel_list_page(soup)
        if not hotels_initial_data:
            raise RuntimeError(f'Hotels initial data not found, url: {hotel_list_url}')

        total_results = None
        total_results_el = soup.select_one("[data-main-list-match-count]")
        if total_results_el:
            total_results = int(total_results_el.attrs['data-main-list-match-count'])

        return total_results, hotels_initial_data

    @named_timeit(name='Step 3: parse/extract')
    def sync_post_process_extracted_data(self, htmls: list[str], hotel_initial_data: list[dict],
                                         post_process_with_multiproc: bool = True):
        if post_process_with_multiproc:
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                return list(executor.map(self.parse_hotel_page, htmls, hotel_initial_data))
        else:
            return [self.parse_hotel_page(html, hotel_initial_data[n]) for n, html in enumerate(htmls)]

    async def async_process_record(self, html, init_data, loop, executor):
        record = await loop.run_in_executor(
            executor, self.parse_hotel_page, html, tuple(init_data.items())
        )
        return record

    @a_named_timeit(name='Step 3: parse/extract')
    async def async_post_process_extracted_data(self, htmls: list[str], hotel_initial_data: list[dict]):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            res = await asyncio.gather(
                *[self.async_process_record(html, init_data, loop, executor) for html, init_data in zip(htmls, hotel_initial_data)]
            )
        return res

    @a_named_timeit(name='Total')
    async def async_scrape(self, query: str, page: int = 1):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ProcessPoolExecutor() as executor:
            total_results, hotels_initial_data = await loop.run_in_executor(
                executor, partial(self.get_initial_hotels_data, query, page))
        htmls = await self.asyncio_get_html_pages(hotels_initial_data)
        return await self.async_post_process_extracted_data(htmls, hotels_initial_data)

    @named_timeit(name='Total')
    def sync_scrape(self, query: str, page: int = 1, method: str = 'mt', post_process_with_multiproc: bool = True):
        total_results, hotels_initial_data = self.get_initial_hotels_data(query, page)

        if method == 'mp':
            return self.multiprocessing_get_html_pages(hotels_initial_data)
        elif method == 'mt':
            htmls = self.threading_get_html_pages(hotels_initial_data)
        else:
            htmls = self.seq_get_html_pages(hotels_initial_data)

        return self.sync_post_process_extracted_data(htmls, hotels_initial_data, post_process_with_multiproc)
