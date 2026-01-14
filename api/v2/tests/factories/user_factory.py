import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    full_name = factory.Faker("name", max_nb_chars=20)
    email = factory.Sequence(lambda n: f"user_{n}@gmail.com")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        pwd = extracted or "default Password"
        self.set_password(pwd)
        if create:
            self.save()
