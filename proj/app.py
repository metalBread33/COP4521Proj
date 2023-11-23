"""This is a webapp for a project for a python class. Pylint requires a docstring for
what ever reason"""
import sqlite3
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from flask import Flask, render_template, jsonify, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

APP = Flask(__name__, static_url_path='/static')
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

APP.secret_key = env.get("APP_SECRET_KEY")

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hackernews_data.db'

DATABASE = SQLAlchemy(APP)

OAUTH = OAuth(APP)

OAUTH.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@APP.route("/")
@APP.route("/home")
def home():
    """Allows users to go to home page"""
    return render_template("home.html", session=session.get('user'),
                           pretty=json.dumps(session.get('user'), indent=4))

@APP.route("/newsfeed")
def newsfeed():
    """For using the curl cmd to get articles in json format"""
    con = sqlite3.connect("hackernews_data.db")
    cursor = con.cursor()
    articles = " SELECT * FROM hackernews_data ORDER BY likes DESC LIMIT 30"
    cursor.execute(articles)
    items = cursor.fetchall()
    item_fields = ['id', 'by', 'descendants', 'kids', 'score', 'text', 'time', 'title', 'type',
                   'url', 'likes', 'dislikes']
    data = [dict(zip(item_fields, news)) for news in items]
    con.close()
    return jsonify(data)

@APP.route("/news")
def news():
    """For presenting new articles to the user"""
    con = sqlite3.connect("hackernews_data.db")
    cursor = con.cursor()
    articles = " SELECT * FROM hackernews_data ORDER BY likes DESC LIMIT 30"
    cursor.execute(articles)
    items = cursor.fetchall()
    item_fields = ['id', 'by', 'descendants', 'kids', 'score', 'text', 'time', 'title', 'type',
                   'url', 'likes', 'dislikes']
    data = [dict(zip(item_fields, news)) for news in items]
    con.close()
    return render_template('newsfeed.html', data=data)

@APP.route("/admin")
def admin():
    """For allowing appropriate users to access admin page"""
    con = sqlite3.connect("hackernews_data.db")
    cursor = con.cursor()
    articles = " SELECT * FROM hackernews_data ORDER BY time DESC LIMIT 30"
    cursor.execute(articles)
    items = cursor.fetchall()
    item_fields = ['id', 'by', 'descendants', 'kids', 'score', 'text', 'time', 'title', 'type',
                   'url', 'likes', 'dislikes']
    data = [dict(zip(item_fields, news)) for news in items]
    con.close()
    return render_template('admin.html', session=session.get('user'), data=data)

@APP.route("/profile")
def profile():
    """For presenting user info"""
    return render_template('profile.html', session=session.get('user'))

@APP.route("/login")
def login():
    """For allowing users to login with auth0"""
    return OAUTH.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@APP.route("/callback", methods=["GET", "POST"])
def callback():
    """Where user returns after using auth0"""
    token = OAUTH.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@APP.route("/logout")
def logout():
    """Allow user to logout using auth0"""
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

@APP.route("/like/<item_id>", methods=["GET", "POST"])
def like(item_id):
    """Allow user to like an item"""
    con = sqlite3.connect("hackernews_data.db")
    cursor = con.cursor()

    item_to_like_query = "SELECT * FROM hackernews_data WHERE id = ?"
    cursor.execute(item_to_like_query, (item_id,))

    item_to_like = cursor.fetchone()
    if item_to_like:
        updated_likes = item_to_like[10] + 1
        update_query = "UPDATE hackernews_data SET likes = ? WHERE id = ?"
        cursor.execute(update_query, (updated_likes, item_id))
        con.commit()
        return redirect(url_for("newsfeed"))
    return "Item not found", 404

@APP.route("/dislike/<item_id>", methods=["GET", "POST"])
def dislike(item_id):
    """Allow user to dislike an item"""
    con = sqlite3.connect("hackernews_data.db")
    cursor = con.cursor()

    item_to_dislike_query = "SELECT * FROM hackernews_data WHERE id = ?"
    cursor.execute(item_to_dislike_query, (item_id,))

    item_to_dislike = cursor.fetchone()
    if item_to_dislike:
        updated_dislikes = item_to_dislike[10] + 1
        update_query = "UPDATE hackernews_data SET dislikes = ? WHERE id = ?"
        cursor.execute(update_query, (updated_dislikes, item_id))
        con.commit()
        return redirect(url_for("newsfeed"))
    return "Item not found", 404


@APP.route("/delete/<item_id>", methods=["GET", "POST"])
def delete(item_id):
    """Allows admin to delete an item"""
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
    con.close()   # Close the connection
    return "Item not found", 404

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=env.get("PORT", 3000), debug=True)
