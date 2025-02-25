from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup as bs

app = Flask(__name__)
CORS(app)

# Function to scrape Flipkart product reviews
def scrape_flipkart_reviews(search_query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    flipkart_url = f"https://www.flipkart.com/search?q={search_query}"
    response = requests.get(flipkart_url, headers=headers)
    flipkart_page = response.text
    flipkart_html = bs(flipkart_page, "html.parser")
    
    bigbox = flipkart_html.findAll("div", {"class": "tUxRFH"})
    if len(bigbox) > 3:
        del bigbox[0:3]
    elif not bigbox:
        return {"error": "No product found"}
    
    box = bigbox[0]
    link_element = box.find("a", href=True)
    if not link_element:
        return {"error": "Product link not found"}
    
    product_link = "https://www.flipkart.com" + link_element['href']
    product_request = requests.get(product_link, headers=headers)
    product_html = bs(product_request.text, "html.parser")
    
    commentbox = product_html.findAll('div', {"class": "col EPCmJX"})
    if not commentbox:
        return {"error": "No reviews found"}
    
    reviews = []
    for comment in commentbox[:5]:  # Get top 5 reviews
        try:
            name = comment.find('p', {"class": "_2NsDsF AwS1CA"}).text.strip()
            rating = comment.find('div', {"class": "XQDdHH Ga3i8K"}).text.strip()
            comment_head = comment.find('p', {"class": "z9E0IG"}).text.strip()
            comment_text = comment.find('div', {"class": "ZmyHeo"}).text.strip()
            reviews.append({"name": name, "rating": rating, "comment_head": comment_head, "comment": comment_text})
        except AttributeError:
            continue
    
    return {"product_link": product_link, "reviews": reviews}

@app.route('/')
def home():
    return render_template("index.html")  # Create a simple HTML UI (index.html)

@app.route('/scrape', methods=['POST'])
def scrape():
    search_query = request.json.get("query")
    if not search_query:
        return jsonify({"error": "Query parameter missing"})
    
    result = scrape_flipkart_reviews(search_query)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
