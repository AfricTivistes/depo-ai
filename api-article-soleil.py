from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

KEYWORDS = ["élection présidentielle", "présidentielle", "élections présidentielles",
            "élection législative", "législative", "élections législatives"]


def get_articles():
    url = "https://lesoleil.sn/rubriques/actualites/politique/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Récupérer la page
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Erreur lors de la récupération de la page principale: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        article_links = []

        # Trouver tous les liens d'articles
        link_elements = soup.select("a.elementor-cta")
        for link in link_elements:
            href = link.get('href')
            if href and href not in article_links:
                article_links.append(href)

        print(f"Nombre de liens trouvés: {len(article_links)}")

        results = []

        for link in article_links:
            try:
                article_response = requests.get(link, headers=headers, timeout=10)
                if article_response.status_code != 200:
                    print(f"Erreur lors de la récupération de l'article {link}: {article_response.status_code}")
                    continue

                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                # Essayer différentes sélections pour trouver le titre
                title_element = article_soup.select_one("h1.td-page-title") or article_soup.select_one("h1")
                if not title_element:
                    print(f"Pas de titre trouvé pour {link}")
                    continue

                title = title_element.text.strip()

                # Essayer différentes sélections pour trouver le contenu
                content_div = article_soup.select_one("div.td-post-content") or article_soup.select_one(
                    "div.elementor-widget-theme-post-content")
                if not content_div:
                    print(f"Pas de contenu trouvé pour {link}")
                    continue

                content = content_div.text.strip()
                combined_text = f"{title.lower()} {content.lower()}"

                # Vérifier si le contenu est lié aux élections
                if any(keyword in combined_text for keyword in KEYWORDS):
                    paragraphs = content.split("\n")
                    description = paragraphs[0] if paragraphs else ""
                    results.append({
                        "title": title,
                        "description": description,
                        "content": content,
                        "url": link
                    })
                    print(f"Article trouvé sur les élections: {title}")

                # Attendre un peu pour ne pas surcharger le serveur
                time.sleep(1)

            except Exception as e:
                print(f"Erreur pour {link}: {str(e)}")

        print(f"Nombre total d'articles sur les élections trouvés: {len(results)}")
        return results

    except Exception as e:
        print(f"Erreur générale: {str(e)}")
        return []


@app.route('/', methods=['GET'])
def index():
    return """
    <html>
    <head>
        <title>API d'articles sur les élections</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #333; }
            .endpoint { background: #f4f4f4; padding: 10px; border-radius: 5px; }
            .description { margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>API d'articles sur les élections</h1>
        <div class="description">
            Cette API extrait des articles liés aux élections du site LeSOLEIL.sn
        </div>
        <div class="endpoint">
            Endpoint: <a href="/api/election-articles">/api/election-articles</a> - Récupérer tous les articles sur les élections
        </div>
    </body>
    </html>
    """


@app.route('/api/election-articles', methods=['GET'])
def get_election_articles():
    articles = get_articles()
    return jsonify(articles)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)