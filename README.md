# Hotspots Aggregator

Hotspots Aggregator 是一个用于聚合各大网站热点新闻的 Python 程序。它可以从不同的网站获取热门新闻和热榜数据，并将它们汇总到一个字典中进行展示。

## 安装

1. 克隆代码仓库到本地：
```shell
git clone https://github.com/your-username/hotspots-aggregator.git
```
2. 进入项目目录：
```shell
cd hotspots-aggregator
```
3. 安装依赖项（建议使用虚拟环境）：
```shell
pip install -r requirements.txt
```

## 使用方式
在项目根目录下的 main.py 文件中，运行以下命令来启动程序
```shell
python main.py
```
可以在weight中设置每个网站的权重共十条
```shell
#聚合各大网站头条，默认权重为2
        weight = {
            "今日头条": 2,
            "微博头条": 2,
            "知乎热榜": 2,
            "微信热榜": 2,
            "B站热榜": 2
        }
```
如果要修改总数请在amount这里修改
```shell
self.amount=10
```
如果你需要设置代理地址可以在这里修改：
```shell
self.proxies = {}
```

## 示例
以下是程序的输出示例：
```shell
{
    "今日头条": {
        "头条标题1": "https: //www.toutiao.com/article1"
    },
    "微博头条": {
        "热搜词1": "https://s.weibo.com/weibo?q=热搜词1"
    },
    "知乎热榜": {
        "问题1": "https://www.zhihu.com/question1"
    },
    "微信热榜": {
        "文章1": "https://weixin-url1"
    },
    "B站热榜": {
        "视频1": "https://bilibili-url1"
    }
}
```
