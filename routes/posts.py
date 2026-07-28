from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Post, User

posts_bp = Blueprint("posts", __name__)


@posts_bp.route("/posts", methods=["POST"])
@jwt_required()
def create_post():
    data = request.get_json()

    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return {"error": "Title and content are required"}, 400

    post = Post(
        title=title,
        content=content,
        user_id=int(get_jwt_identity())
    )

    db.session.add(post)
    db.session.commit()

    return {
        "message": "Post created successfully"
    }, 201



@posts_bp.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()

    result = []

    for post in posts:
        result.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "author": post.author.username
        })

    return result, 200


@posts_bp.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = db.session.get(Post, post_id)

    if not post:
        return {"error": "Post not found"}, 404

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at,
        "author": post.author.username
    }, 200

@posts_bp.route("/posts/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    post = db.session.get(Post, post_id)

    if not post:
        return {"error": "Post not found"}, 404

    current_user_id = int(get_jwt_identity())

    current_user = db.session.get(User, current_user_id)

    if not current_user:
        return {"error": "User not found"}, 404

    if post.user_id != current_user.id and current_user.role != "admin":
        return {"error": "You are not allowed to delete this post"}, 403

    db.session.delete(post)
    db.session.commit()

    return {
        "message": "Post deleted successfully"
    }, 200




# New protected route to update a post
@posts_bp.route("/posts/<int:post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id):
    post = db.session.get(Post, post_id)

    if not post:
        return {"error": "Post not found"}, 404

    current_user_id = int(get_jwt_identity())

    if post.user_id != current_user_id:
        return {"error": "You are not allowed to update this post"}, 403

    data = request.get_json()

    post.title = data.get("title", post.title)
    post.content = data.get("content", post.content)

    db.session.commit()

    return {
        "message": "Post updated successfully"
    }, 200