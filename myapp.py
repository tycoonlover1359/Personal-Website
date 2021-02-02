import sys
import boto3
import os
import dotenv
import json
import re
import sys
from datetime import datetime

# Initialization Stuff
dotenv.load_dotenv()

from flask import Flask, __version__, abort, render_template, redirect, url_for, request, render_template_string, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "<MYSQL_DATBASE_URI>"
db = SQLAlchemy(app)

# SQLAlchemy Classes
class BlogPost(db.Model):
    __tablename__ = "entries"
    post_uuid = db.Column(db.String(36), primary_key=True, unique=True)
    post_id = db.Column(db.Text)
    title = db.Column(db.Text)
    author = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    s3_object_key = db.Column(db.Text)

# Routes
@app.route("/tempdiscord", methods=["POST"])
def slack():
    with open("discord.txt", "wb") as f:
        f.write(request.data)
    return "Saved", 200
    
@app.route("/testingpage", methods=["GET"])
def testing():
    return render_template("testing.html")

@app.route("/", methods=["GET", "POST"])
def site_home():
    if request.method == "GET":
        return render_template("home.html")
    elif request.method == "POST":
        time = datetime.utcnow().isoformat()
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        with open(f"{time}-{name}-{subject}.txt", "w") as f:
            try:
                f.write(f"Time: {time}\nName: {name}\nEmail: {email}\nSubject: {subject}\nMessage:\n{message}")
            except Exception:
                return render_template("home.html", submit_success=False)
            else:
                payload = json.dumps({
                    "name": str(name),
                    "email": str(email),
                    "message": str(message),
                    "subject": str(subject)
                }).encode("utf-8")
                aws_lambda = boto3.client("lambda", region_name="us-west-2")
                response = aws_lambda.invoke(
                    FunctionName="arn:aws:lambda:us-west-2:<ACCOUNT_ID>:function:Website-Send_Message_Confirmation",
                    Payload=payload
                )
                return render_template("home.html", submit_success=True)

@app.route("/blog/home")
def blog_home():
    result = BlogPost.query.limit(5).all()
    return render_template("/Blog/blog_home.html", entries=result)

@app.route("/blog/post/<string:post_id>")
def blog_post(post_id=None):
    if post_id is None:
        return redirect("/blog/home")
    result = BlogPost.query.filter_by(post_id=post_id).first()
    if not result:
        return render_template("/Errors/404.html"), 404
    try:
        f = open(f"./blog post cache/{result.post_uuid}.html", "r")
    except FileNotFoundError as e:
        post_id = result.post_id
        title = result.title
        author = result.author
        created_at = result.created_at
        object_key = result.s3_object_key
        s3 = boto3.resource("s3", region_name="us-west-2")
        try:
            obj = s3.Object("tycoon-website", f"{object_key}")
        except boto3.client("s3").exceptions.NoSuchBucket:
            return render_template("/Errors/404.html"), 404
        except boto3.client("s3").exceptions.NoSuchKey:
            return render_template("/Errors/404.html"), 404
        except Exception as e:
            return render_template("/Errors/500.html", error_message=e), 500
        else:
            article_content = obj.get()["Body"].read().decode("utf-8")
            rendered_page = render_template("/Blog/blog_post.html", article=article_content, post_id=post_id, title=title, author=author, created_at=created_at)
            with open(f"./blog post cache/{result.post_uuid}.html", "w") as f:
                f.write(rendered_page)
            return rendered_page
    except Exception as e:
        return render_template("/Errors/500.html", error_message=e), 500
    else:
        rendered_page = f.read()
        f.close()
        return rendered_page
        
# Redirects
@app.route("/blog")
@app.route("/blog/")
def blog_redir():
    return redirect("/blog/home")

@app.route("/home")
def home_redir():
    return redirect("/")

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return render_template("/Errors/404.html"), 404

@app.errorhandler(500)
def ise(error):
    original = getattr(error, "original_exception", None)
    return render_template("/Errors/500.html", error_message=original), 500

if __name__ == "__main__":
    app.run()