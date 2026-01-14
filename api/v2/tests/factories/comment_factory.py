import factory

from api.v2.tests.factories.post_factory import PostFactory
from api.v2.tests.factories.user_factory import UserFactory
from app.comment.models import Comment


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    content = factory.Faker("sentence")
    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
