import pytest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIRequestFactory

from app.comment.models import Comment
from app.like.models import Like
from app.post.models import Post


@pytest.fixture
def users(db):
    user_1 = get_user_model().objects.create_user(
        full_name="user1", password="HashTesting", email="Testing1@gmail.com"
    )
    user_2 = get_user_model().objects.create_user(
        full_name="user2", password="HashTesting", email="Testing2@gmail.com"
    )
    user_3 = get_user_model().objects.create_user(
        full_name="user3", password="HashTesting", email="Testing3@gmail.com"
    )
    admin = get_user_model().objects.create_superuser(
        full_name="Admin", password="HashTestingAdmin", email="admin@gmail.com"
    )
    admin_2 = get_user_model().objects.create_superuser(
        full_name="Admin_2", password="HashTestingAdmin_2", email="admin_2@gmail.com"
    )

    return {
        "user_1": user_1,
        "user_2": user_2,
        "user_3": user_3,
        "admin": admin,
        "admin_2": admin_2,
    }


@pytest.fixture
def posts(db, users):
    post_1 = Post.objects.create(
        title="Introduction to Python Programming",
        content="Python language is one of the easiest language of all",
        author=users.get("user_1"),
        is_published=True,
    )
    draft_1 = Post.objects.create(
        title="Why learning at least 2 languages is Important",
        content="The choice of choosing more than one language is becoming of importance",
        author=users.get("user_1"),
    )
    post_2 = Post.objects.create(
        title="Introduction to JavaScript Programming",
        content="JavaScript is consider to be the mother of all languages",
        author=users["user_1"],
        is_published=True,
    )
    draft_2 = Post.objects.create(
        title="My Journey to Programming language",
        content="Becoming a SW Engineer was probably the least thing I ever thought about",
        author=users["user_2"],
    )
    draft_3 = Post.objects.create(
        title="Politics in my Country",
        content="It is an unfortunate that Religion and Ethnicity has become a political tools",
        author=users["user_2"],
    )
    post_3 = Post.objects.create(
        title="Introduction to JavaScript Programming",
        content="JavaScript is consider to be the mother of all languages",
        author=users["admin_2"],
        is_published=True,
    )
    draft_4 = Post.objects.create(
        title="Introduction to Go Programming",
        content="Go is consider to be one of the fastests of all languages",
        author=users["admin_2"],
    )

    return {
        "post_1": post_1,
        "post_2": post_2,
        "draft_1": draft_1,
        "draft_2": draft_2,
        "draft_3": draft_3,
        "post_3": post_3,
        "draft_4": draft_4,
    }


@pytest.fixture
def comments(db, users, posts):
    comment_1 = Comment.objects.create(
        content="This is a comment by user_1",
        post=posts["post_1"],
        author=users["user_1"],
    )
    comment_2 = Comment.objects.create(
        content="This is a comment by user_2",
        post=posts["post_1"],
        author=users["user_2"],
    )
    comment_3 = Comment.objects.create(
        content="This is another comment by user_1",
        post=posts["post_1"],
        author=users["user_1"],
    )
    comment_4 = Comment.objects.create(
        content="This is another comment by user_2",
        post=posts["post_1"],
        author=users["user_2"],
    )
    comment_5 = Comment.objects.create(
        content="This is a comment by user_3",
        post=posts["post_2"],
        author=users["user_3"],
    )

    reply_1 = Comment.objects.create(
        content="This is a reply by user_2",
        post=posts["post_1"],
        parent=comment_1,
        author=users["user_2"],
    )
    reply_2 = Comment.objects.create(
        content="This is a reply by user_3",
        post=posts["post_1"],
        parent=comment_1,
        author=users["user_3"],
    )
    reply_3 = Comment.objects.create(
        content="This is a reply by user_3",
        post=posts["post_2"],
        parent=comment_5,
        author=users["user_1"],
    )

    return {
        "comment_1": comment_1,
        "comment_2": comment_2,
        "comment_3": comment_3,
        "comment_4": comment_4,
        "comment_5": comment_5,
        "reply_1": reply_1,
        "reply_2": reply_2,
        "reply_3": reply_3,
    }


@pytest.fixture
def likes(db, users, posts, comments):
    post_like = Like.objects.create(
        user=users["user_3"],
        content_type=ContentType.objects.get_for_model(Post),
        object_id=posts["post_1"].id,
    )
    comment_like = Like.objects.create(
        user=users["user_2"],
        content_type=ContentType.objects.get_for_model(Comment),
        object_id=comments["comment_5"].id,
    )
    return {
        "post_like": post_like,
        "comment_like": comment_like,
    }


@pytest.fixture
def api_rf():
    return APIRequestFactory()
