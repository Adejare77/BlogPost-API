import factory

from api.v2.tests.factories.user_factory import UserFactory
from app.post.models import Post


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker("text", max_nb_chars=50)
    content = factory.Faker("sentence")
    author = factory.SubFactory(UserFactory)
