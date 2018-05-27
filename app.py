from flask import Flask, render_template, jsonify, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

mongo = PyMongo(app)

@app.route("/")
def index():
    info_dict2 = mongo.db.info_dict.find_one()
    return render_template("index.html", info_dict=info_dict2)

@app.route("/scrape")
def scraper():
    #Empty any previous entries before scraping again
    mongo.db.drop_collection('info_dict')
    info_dict = scrape_mars.scrape()
    # Insert forecast into database
    mongo.db.info_dict.insert_one(info_dict)

    # Redirect back to home page
    return redirect("http://127.0.0.1:5000/", code=302)

if __name__ == "__main__":
    app.run(debug=True)

