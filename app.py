from flask import Flask

from config import Config
from extensions import db, jwt, bcrypt
from models import User, Post
from routes.auth import auth_bp
from routes.posts import posts_bp
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt.init_app(app)
bcrypt.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)


@app.route("/")
def home():
    return {"message": "Welcome to the Blog API"}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)