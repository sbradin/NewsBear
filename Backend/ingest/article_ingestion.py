import time, datetime
from eventregistry import *
from dotenv import load_dotenv
import os
import sys
from app.db import store_articles

sys.stdout.reconfigure(encoding="utf-8") # type: ignore

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

er = EventRegistry(apiKey = NEWSAPI_KEY)

recentQ = GetRecentArticles(er, returnInfo = ReturnInfo(ArticleInfoFlags(bodyLen = 300, concepts = True, categories = True, lang = "eng")), recentActivityArticlesMaxArticleCount = 300)
starttime = time.time()
# while True:
for i in range(100):
    articleList = recentQ.getUpdates()
    print("=======\n%d articles were found since the last call" % len(articleList))
    print(f"Successfully added {store_articles(articleList)} articles to database")

    # wait a minute until next batch of new content is ready
    print("sleeping for 60 seconds...")
    time.sleep(60.0)