from api.v2.user.serializer import UserSerializer


def test_user_serialization_when_retrieving_returns_expected_fields(users):
    user = users["user_2"]
    ser = UserSerializer(instance=user)
    expected_fields = {"id", "email", "full_name"}

    assert expected_fields == set(ser.fields)


def test_user_serializer_for_all_users_returns_expected_fields(users):
    users = users.values()
    ser = UserSerializer(instance=users, many=True)
    expected_fields = {"id", "email", "full_name"}

    for data in ser.data:
        assert expected_fields == set(data.keys())


def test_serializer_read_only_fields(api_rf, users):
    ser = UserSerializer()
    writable_fields = {
        name for name, field in ser.fields.items() if not field.read_only
    }

    assert writable_fields == set()
