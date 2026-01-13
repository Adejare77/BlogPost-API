from app.comment.models import Comment
from api.v2.tests.factories.user_factory import UserFactory
from api.v2.tests.factories.post_factory import PostFactory
import factory


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    content = factory.Faker("sentence")
    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
