import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    full_name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"user_{n}@test.com")
    password = factory.django.Password("testPassword")
