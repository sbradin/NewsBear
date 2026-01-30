import requests

url = "https://api.gdeltproject.org/api/v2/doc/doc"
params = {
    "query": "sourcelang:english",
    "mode": "artlist",
    "format": "jsonfeed",
    "timespan": "1hr",
    "maxrecords": "250"
}

resp = requests.get(url,params=params)
data = resp.json()

#print(data)
print(data["items"])

count_snippets = 0
for article in data["items"] : 
    if(article.get("content_text") != ""):
        count_snippets += 1
        
        
print(count_snippets)