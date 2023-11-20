from flask import Flask, render_template, jsonify, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy 
import sqlite3
import requests
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

app = Flask(__name__, static_url_path='/static')
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app.secret_key = env.get("APP_SECRET_KEY")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hackernews_data.db'

db = SQLAlchemy(app)

oauth = OAuth(app)  

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/")
@app.route("/home")
def home(): 
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/newsfeed")
def newsfeed():
    con = sqlite3.connect("hackernews_data.db")
    cursor = con.cursor()
    news = " SELECT * FROM hackernews_data ORDER BY time DESC LIMIT 30"
    cursor.execute(news)
    items = cursor.fetchall()
    item_fields = ['id', 'by', 'descendants', 'kids', 'score', 'text', 'time', 'title', 'type', 'url', 'likes', 'dislikes']
    data = [dict(zip(item_fields, news)) for news in items]
    con.close()
    return render_template('newsfeed.html', data=data)

@app.route("/admin")
def admin():
    con = sqlite3.connect("hackernews_data.db")
    cursor = con.cursor()
    news = " SELECT * FROM hackernews_data ORDER BY time DESC LIMIT 30"
    cursor.execute(news)
    items = cursor.fetchall()
    item_fields = ['id', 'by', 'descendants', 'kids', 'score', 'text', 'time', 'title', 'type', 'url', 'likes', 'dislikes']
    data = [dict(zip(item_fields, news)) for news in items]
    con.close()
    return render_template('admin.html', session=session.get('user'), data=data)

@app.route("/profile")
def profile():
    return render_template('profile.html', session=session.get('user'))

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/like")
def like(likeCount):
    return""    

@app.route ("/dislike")
def dislike():
    return ""


@app.route("/delete/<item_id>", methods=["GET", "POST"])
def delete(item_id):
    con = sqlite3.connect("hackernews_data.db")
    cursor = con.cursor()

    # Use placeholders in the query to avoid SQL injection
    item_to_delete_query = "SELECT * FROM hackernews_data WHERE id = ?"
    cursor.execute(item_to_delete_query, (item_id,))
    
    # Fetch one row from the result
    item_to_delete = cursor.fetchone()

    if item_to_delete:
        # Use the correct syntax for DELETE statement
        delete_query = "DELETE FROM hackernews_data WHERE id = ?"
        cursor.execute(delete_query, (item_id,))
        
        con.commit()  # Commit the changes to the database
        con.close()   # Close the connection
        
        return redirect("/admin")
    else:
        con.close()   # Close the connection
        return "Item not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000), debug=True)

