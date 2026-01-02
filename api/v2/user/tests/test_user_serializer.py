from rest_framework.test import force_authenticate
from django.urls import reverse
from api.v2.user.views import UserListAPIView, UserRetrieveAPIView
from api.v2.user.serializer import UserSerializer

def test_user_serializer_when_retrieving_returns_expected_fields(api_rf, users):
    """GET -> retrieve user-profile: id, email, full_name"""
    user_2 = users['user_2']
    url = reverse('user-profile', args=[user_2.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user_2)
    view = UserRetrieveAPIView.as_view()

    response = view(request, user_id=user_2.id)

    assert set(response.data.keys()) == {'id', 'email', 'full_name'}

def test_user_serializer_for_all_users_returns_expected_fields(api_rf, users):
    """GET -> all users: [{id, email, full_name}, {...}]"""
    admin = users['admin']
    url = reverse('all-users')
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = UserListAPIView.as_view()

    response = view(request)

    assert isinstance(response.data['results'], list)
    assert response.data['results']

    for item in response.data['results']:
        assert isinstance(item, dict)
        assert {'id', 'email', 'full_name'}.issubset(item.keys())

def test_user_serializer_is_read_only(api_rf, users):
    serializer = UserSerializer()
    assert serializer.fields['id'].read_only
    assert serializer.fields['email'].read_only
    assert serializer.fields['full_name'].read_only
