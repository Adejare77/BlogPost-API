import factory
import pytest
from rest_framework.test import APIClient

from api.v2.tests.factories.comment_factory import CommentFactory
from api.v2.tests.factories.post_factory import PostFactory
from api.v2.tests.factories.user_factory import UserFactory


@pytest.fixture
def users(db):
    return UserFactory.create_batch(5)


@pytest.fixture
def admin_client(db):
    admin = UserFactory(is_staff=True, is_superuser=True)
    client = APIClient()
    client.force_authenticate(admin)
    return client


@pytest.fixture
def user_client(users):
    client = APIClient()
    client.force_authenticate(users[0])
    return client


@pytest.fixture
def published_posts(db, users):
    return PostFactory.create_batch(
        10, author=factory.Iterator(users), is_published=True
    )


@pytest.fixture
def draft_posts(db, users):
    return PostFactory.create_batch(6, author=factory.Iterator(users))


@pytest.fixture
def comments(db, users, published_posts):
    return CommentFactory.create_batch(
        15, author=factory.Iterator(users), post=factory.Iterator(published_posts)
    )


@pytest.fixture
def replies(db, users, published_posts, comments):
    return CommentFactory.create_batch(
        30,
        author=factory.Iterator(users),
        post=factory.Iterator(published_posts),
        parent=factory.Iterator(comments),
    )


@pytest.fixture
def api_cl():
    return APIClient()
