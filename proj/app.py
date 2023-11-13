from flask import Flask, render_template, jsonify, render_template
import sqlite3
import requests

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home(): 
    return render_template('home.html')

@app.route("/newsfeed")
def newsfeed():
    con = sqlite3.connect("hackernews_data.db")
    cursor = con.cursor()
    news = " SELECT * FROM hackernews_data ORDER BY time DESC LIMIT 30"
    cursor.execute(news)
    items = cursor.fetchall()
    item_fields = ['id', 'by', 'descendants', 'kids', 'score', 'text', 'time', 'title', 'type', 'url']
    data = [dict(zip(item_fields, news)) for news in items]
    con.close()
    return jsonify(data)

@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/login")
def login():
    return render_template('login.html')
   

@app.route("/signup")
def signup():
    return render_template('signup.html')



if __name__ == '__main__':
    app.run(debug=True)
