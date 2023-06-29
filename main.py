import requests
import json
from bs4 import BeautifulSoup

class HotspotsAggregator:
    def __init__(self):
        # 设置代理
        self.proxies = {}
        # 创建新的字典用于存储结果
        self.result_dict = {}
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        }
        #设置每个网站爬取的熟练，默认10
        self.amount=10

    def print_toutiao(self):
        for site, values in self.result_dict.items():
            for title, url in values.items():
                print(f"Site: {site}")
                print(f"Title: {title}")
                print(f"URL: {url}")
                print()

    def get_content(self, url, type="json"):
        response = requests.get(url, headers=self.base_headers, proxies=self.proxies)
        response.raise_for_status()
        if type == "json":
            result = json.loads(BeautifulSoup(response.text, "html.parser").text)
        elif type == "html":
            result = BeautifulSoup(response.text, "html.parser")
        return result

    def save_data(self, site, data, key):
        # 保存到字典中
        for index, value in enumerate(data[key]):
            if index < amount:
                if site == "微博头条":
                    if index == 0:
                        continue
                    self.result_dict[site][value["word"]] = f"https://s.weibo.com/weibo?q={value['word']}&topic_ad="
                elif site == "今日头条":
                    self.result_dict[site][value["Title"]] = value["Url"]
                elif site == "知乎热榜":
                    self.result_dict[site].update({value["target"]["titleArea"]["text"]: value["target"]["link"]["url"]})
                elif site == "B站热榜":
                    self.result_dict[site].update({value["title"]: value["short_link_v2"]})
            else:
                break

    def toutiao(self):
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc&_signature=_02B4Z6wo00f01fAdWzAAAIDAD15KaUl.IEnwOV-AABie87"
        data = self.get_content(url)
        title_top_title = data["fixed_top_data"][0]["Title"]
        title_top_url = data["fixed_top_data"][0]["Url"]
        self.result_dict["今日头条"] = {title_top_title: title_top_url}
        self.save_data("今日头条", data, "data")

    def weibo(self):
        url = "https://weibo.com/ajax/side/hotSearch"
        data = self.get_content(url)["data"]
        title_top_title = data["hotgov"]["word"]
        title_top_url = data["hotgov"]["url"]
        self.result_dict["微博头条"] = {title_top_title: title_top_url}
        self.save_data("微博头条", data, "realtime")

    def zhihu(self):
        content = self.get_content(url="https://www.zhihu.com/billboard", type="html")
        data = json.loads(content.find("script", id="js-initialData").text)["initialState"]["topstory"]
        self.result_dict["知乎热榜"] = {}
        self.save_data("知乎热榜", data, "hotList")

    def weixin(self):
        self.result_dict["微信热榜"] = {}
        content = self.get_content("https://tophub.today/n/WnBe01o371", "html")
        tbody = content.find("tbody")
        tr_tags = tbody.find_all("tr")[:10]
        for tr in tr_tags:
            a_tag = tr.find("a")
            if a_tag:
                a_content = a_tag.text
                a_href = a_tag.get("href")
                base_url = "https://tophub.today"
                complete_url = base_url + a_href
                response = requests.get(complete_url, allow_redirects=False, headers=self.base_headers, proxies=self.proxies)
                redirected_url = response.headers.get("Location")
                self.result_dict["微信热榜"].update({a_content: redirected_url})

    def bilibili(self):
        data = self.get_content("https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all", "json")["data"]
        self.result_dict["B站热榜"] = {}
        self.save_data("B站热榜", data, "list")

    def aggregation_hotspots(self):
        weight = {
            "今日头条": 2,
            "微博头条": 2,
            "知乎热榜": 2,
            "微信热榜": 2,
            "B站热榜": 2
        }
        new_dict = {}
        for key, value in weight.items():
            keys = list(self.result_dict[key].keys())
            values = list(self.result_dict[key].values())
            new_dict.update(dict(zip(keys[:value], values[:value])))
        print(new_dict)

if __name__ == "__main__":
    aggregator = HotspotsAggregator()
    aggregator.toutiao()
    aggregator.weibo()
    aggregator.zhihu()
    aggregator.weixin()
    aggregator.bilibili()
    aggregator.aggregation_hotspots()
