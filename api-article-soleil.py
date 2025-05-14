from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

app = Flask(__name__)

KEYWORDS = ["élection présidentielle", "présidentielle", "élections présidentielles",
            "élection législative", "législative", "élections législatives"]


def scrap_articles():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(options=options)

    url = "https://lesoleil.sn/rubriques/actualites/politique/"
    driver.get(url)
    time.sleep(5)

    article_elements = driver.find_elements(By.CSS_SELECTOR, "a.elementor-cta")
    article_links = list({el.get_attribute("href") for el in article_elements if el.get_attribute("href")})

    results = []

    for link in article_links:
        try:
            driver.get(link)
            time.sleep(3)

            try:
                title = driver.find_element(By.CSS_SELECTOR, "h1.td-page-title").text.strip()
            except:
                try:
                    title = driver.find_element(By.TAG_NAME, "h1").text.strip()
                except:
                    continue

            try:
                content_div = driver.find_element(By.CSS_SELECTOR, "div.td-post-content")
            except:
                try:
                    content_div = driver.find_element(By.CSS_SELECTOR, "div.elementor-widget-theme-post-content")
                except:
                    continue

            content = content_div.text.strip()
            combined_text = f"{title.lower()} {content.lower()}"

            if any(keyword in combined_text for keyword in KEYWORDS):
                paragraphs = content.split("\n")
                description = paragraphs[0] if paragraphs else ""
                results.append({
                    "title": title,
                    "description": description,
                    "content": content,
                    "url": link
                })

        except Exception as e:
            print(f"Erreur pour {link}: {e}")

    driver.quit()
    return results


@app.route('/', methods=['GET'])
def index():
    # Redirige vers l'API ou affiche un message simple
    return "API d'articles sur les élections. Utilisez /api/election-articles pour obtenir les données."


@app.route('/api/election-articles', methods=['GET'])
def get_election_articles():
    articles = scrap_articles()
    return jsonify(articles)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)