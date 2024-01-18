import json
from bs4 import BeautifulSoup
import logging
import aiohttp
import asyncio

class HotspotsAggregator:
    def __init__(self, proxies=None, amount=10):
        self.proxies = proxies if proxies else {}
        self.result_dict = {}
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        }
        self.amount = amount
        logging.basicConfig(level=logging.INFO)

    def print_results(self):
        for site, values in self.result_dict.items():
            for title, url in values.items():
                print(f"网站: {site}\n标题: {title}\n链接: {url}\n")

    def parse_response(self, response, type):
        if type == "json":
            return json.loads(response.text)
        elif type == "html":
            return BeautifulSoup(response.text, "html.parser")

    async def get_content_async(self, url, type="json"):
        async with aiohttp.ClientSession(headers=self.base_headers) as session:
            try:
                async with session.get(url, timeout=10) as response:  # 使用 aiohttp 的内置超时
                    if response.status == 200:
                        if type == "json":
                            return await response.json()
                        elif type == "html":
                            text = await response.text()
                            return BeautifulSoup(text, "html.parser")
                    else:
                        logging.error(f"从 {url} 获取数据时出错: {response.status}")
                        return None
            except asyncio.TimeoutError:
                logging.error(f"请求 {url} 超时")
                return None

    def save_data(self, site, data, key):
        for index, value in enumerate(data[key]):
            if index < self.amount:
                # 根据不同网站的数据结构来处理
                title, url = self.extract_data(site, value)
                self.result_dict[site].update({title: url})
            else:
                break

    def extract_data(self, site, value):
        # 根据每个网站的特定结构提取标题和URL
        if site == "今日头条":
            return value["Title"], value["Url"]
        elif site == "微博头条":
            return value["word"], f"https://s.weibo.com/weibo?q={value['word']}&topic_ad="
        elif site == "知乎热榜":
            return value["target"]["titleArea"]["text"], value["target"]["link"]["url"]
        elif site == "B站热榜":
            return value["title"], value["short_link_v2"]
        elif site == "微信热榜":
            return value.text, value.get("href")
        else:
            return None, None

    async def scrape_site(self, site_name, url, content_type="json", data_key=None):
        content = await self.get_content_async(url, type=content_type)
        if content_type == "json" and data_key:
            # 特殊处理
            if site_name == "微博头条" or site_name == "B站热榜":
                content = content['data']
        if content_type == "html":
            # 特殊处理HTML内容
            if site_name == "知乎热榜":
                content = json.loads(content.find("script", id="js-initialData").text)["initialState"]["topstory"]
            elif site_name == "微信热榜":
                tr_tags = content.find("tbody").find_all("tr")[:self.amount]
                content = {"微信热榜": tr_tags}
        self.result_dict[site_name] = {}
        self.save_data(site_name, content, data_key or site_name.lower())

    async def aggregate_hotspots(self):
        await asyncio.gather(
            self.scrape_site("今日头条", "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc&_signature=_02B4Z6wo00f01fAdWzAAAIDAD15KaUl.IEnwOV-AABie87", "json", "data"),
            self.scrape_site("微博头条", "https://weibo.com/ajax/side/hotSearch", "json", "realtime"),
            self.scrape_site("知乎热榜", "https://www.zhihu.com/billboard", "html", "hotList"),
            self.scrape_site("微信热榜", "https://tophub.today/n/WnBe01o371", "html"),
            self.scrape_site("B站热榜", "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all", "json", "list")
        )


if __name__ == "__main__":
    aggregator = HotspotsAggregator()
    asyncio.run(aggregator.aggregate_hotspots())
    aggregator.print_results()
