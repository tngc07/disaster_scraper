import requests
import yaml
from bs4 import BeautifulSoup
from datetime import datetime
from scraper.parser import classify_disaster_type
from scraper.utils import save_to_csv

def load_config(path="sites.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def find_articles(html, config, keywords):
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all(config["article_tag"])
    matches = []
    for article in articles:
        link_tag = article.select_one(config["article_link_selector"])
        if not link_tag or not link_tag.get("href"):
            continue
        title = link_tag.get_text(strip=True)
        url = link_tag["href"]
        if url.startswith("/"):
            url = config["base_url"].split("/")[0] + "//" + config["base_url"].split("/")[2] + url
        if any(keyword in title.lower() for keyword in keywords):
            matches.append({
                "title": title,
                "url": url,
                "scraped_at": datetime.today().strftime('%Y-%m-%d'),
                "disaster_type": classify_disaster_type(title)
            })
    return matches

def run_scraper():
    keywords = ["earthquake", "temblor", "quake", "sismo", "terremoto",
                "flood", "inundación", "flash flood", "hurricane", "huracán", "storm",
                "cyclone", "tropical storm", "landslide", "deslizamiento", "mudslide",
                "wildfire", "bushfire", "forest fire", "incendio forestal", "volcano",
                "eruption", "erupción", "volcán"]
    configs = load_config()
    all_articles = []
    for config in configs:
        try:
            html = requests.get(config["base_url"]).text
            articles = find_articles(html, config, keywords)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Failed to scrape {config['name']}: {e}")
    save_to_csv(all_articles)

if __name__ == "__main__":
    run_scraper()
