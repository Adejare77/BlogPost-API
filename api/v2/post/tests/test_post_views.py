from app.post.models import Post
from api.v2.post.views import (
    PostListCreateAPIView,
    PostRetrieveUpdateDestroyAPIView,
    PopularPostListAPIView
)
from django.urls import reverse
from rest_framework import status
from rest_framework.test import force_authenticate
from api.v2.post.tests.constants import UNAUTHORIZED, FORBIDDEN

# =================== PostListCreateAPIView ========================

def test_get_posts_when_unauthenticated_returns_200(api_rf, posts):
    url = reverse('posts')
    request = api_rf.get(path=url)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK

def test_get_posts_as_user_returns_200(api_rf, users):
    user = users['user_1']
    url = reverse('posts')
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK

def test_get_posts_as_admin_returns_200(api_rf, users):
    admin = users['admin']
    url = reverse('posts')
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK

def test_create_post_when_unauthenticated_returns_401(api_rf):
    url = reverse('posts')
    data = {
        'content': 'This is a sample Content',
        'title': "This is a title"
    }
    request = api_rf.post(path=url, data=data)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED

def test_create_post_as_user_returns_201(api_rf, users):
    user = users['user_1']
    url = reverse('posts')
    data = {
        'content': 'This is a sample Content',
        'title': "This is a title"
    }
    request = api_rf.post(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED

def test_get_drafts_when_unauthenticated_returns_401(api_rf, users):
    url = reverse('posts') + "?status=draft"
    request = api_rf.get(path=url)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED

def test_get_own_drafts_as_user_returns_200(api_rf, users):
    user = users['user_1']
    url = reverse('posts') + "?status=draft"
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK

def test_get_drafts_as_non_owner_returns_403(api_rf, users):
    user = users['user_1']
    url = reverse('posts') + "?status=draft&author=user2"
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_get_drafts_as_admin_returns_200(api_rf, users):
    admin = users['admin']
    url = reverse('posts') + "?status=draft&author=user1"
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK

def test_get_posts_and_drafts_when_unauthenticated_returns_401(api_rf):
    url = reverse('posts') + "?status=all"
    request = api_rf.get(path=url)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED

def test_get_own_posts_and_drats_as_user_returns_200(api_rf, users):
    user = users['user_1']
    url = reverse('posts') + "?status=all"
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK

def test_get_posts_and_drafts_as_non_owner_returns_403(api_rf, users):
    user = users['user_1']
    url = reverse('posts') + "?status=all&author=user1"
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_get_posts_by_author_when_unauthenticated_returns_200(api_rf, users, posts):
    user = users['user_1']
    url = reverse('posts') + "?author=user1"
    request = api_rf.get(path=url)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['results']  # Not empty

    for items in response.data['results']:
        assert items['author'] == user.id

def test_get_posts_by_author_as_user_returns_200(api_rf, users, posts):
    user = users['user_1']
    url = reverse('posts') + "?author=user1"
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['results']

    for items in response.data['results']:
        assert items['author'] == user.id

def test_get_posts_by_author_as_admin_returns_200(api_rf, users, posts):
    admin = users['admin']
    user = users['user_1']
    url = reverse('posts') + "?author=user1"
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = PostListCreateAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['results']

    for items in response.data['results']:
        assert items['author'] == user.id

def test_no_n_plus_one_queries(posts, api_rf, django_assert_num_queries):
    with django_assert_num_queries(3):
        url = reverse('posts')
        request = api_rf.get(path=url)
        view = PostListCreateAPIView.as_view()

        response = view(request)

        assert response.status_code == status.HTTP_200_OK


# ===================== PostRetrieveUpdateDestroyAPIView =========================

def test_get_post_by_id_when_unauthenticated_returns_200(api_rf, users, posts):
    post = posts['post_2']
    url = reverse('post-detail', args=[post.id])
    request = api_rf.get(path=url)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data

def test_get_post_by_id_as_user_returns_200(api_rf, users, posts):
    user = users['user_1']
    post = posts['post_2']
    url = reverse('post-detail', args=[post.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data

def test_get_post_by_id_as_admin_returns_200(api_rf, users, posts):
    admin = users['admin']
    post = posts['post_1']
    url = reverse('post-detail', args=[post.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data

def test_get_draft_by_id_when_unauthenticated_returns_401(api_rf, posts):
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id]) + "?status=draft"
    request = api_rf.get(path=url)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED


def test_get_own_draft_by_id_as_user_returns_200(api_rf, users, posts):
    user = users['user_2']
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id]) + "?status=draft"
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data

def test_get_draft_by_id_as_non_owner_returns_403(api_rf, users, posts):
    user = users['user_1']
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id]) + "?status=draft"
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_get_draft_by_id_as_admin_returns_200(api_rf, users, posts):
    admin = users['admin']
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id]) + "?status=draft"
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data


def test_full_update_post_by_id_when_unauthenticated_returns_401(api_rf, posts):
    post = posts['post_2']
    url = reverse('post-detail', args=[post.id])
    data = {
        "content": "This is an updated content",
        "title": "This is an updated title"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED

def test_full_update_own_post_by_id_as_user_returns_200(api_rf, users, posts):
    user = users['user_1']
    post = posts['post_2']
    url = reverse('post-detail', args=[post.id])
    data = {
        "content": "This is an updated content",
        "title": "This is an updated title"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_200_OK

    post.refresh_from_db()
    assert post.content == data['content']
    assert post.title == data['title']

def test_full_update_post_by_id_as_non_owner_return_403(api_rf, users, posts):
    user = users['user_2']
    post = posts['post_2']
    url = reverse('post-detail', args=[post.id])
    data = {
        "content": "This is an updated content",
        "title": "This is an updated title"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_full_update_post_by_id_as_admin_returns_403(api_rf, users, posts):
    admin = users['admin']
    post = posts['post_1']
    url = reverse('post-detail', args=[post.id])
    data = {
        "content": "This is an updated content",
        "title": "This is an updated title"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=admin)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN


def test_full_update_draft_by_id_when_unauthenticated_returns_401(api_rf, posts):
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id])
    data = {
        "content": "This is an updated content",
        "title": "This is an updated title"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED

def test_full_update_own_draft_by_id_as_user_returns_200(api_rf, users, posts):
    user = users['user_2']
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id])
    data = {
        "content": "This is an updated content",
        "title": "This is an updated title",
        "is_published": True
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_200_OK

    draft.refresh_from_db()
    assert draft.content == data['content']
    assert draft.title == data['title']
    assert draft.is_published == data['is_published']

def test_full_update_draft_by_id_as_non_owner_return_403(api_rf, users, posts):
    user = users['user_1']
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id])
    data = {
        "content": "This is an updated content",
        "title": "This is an updated title"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_full_update_draft_by_id_as_admin_returns_403(api_rf, users, posts):
    admin = users['admin']
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id])
    data = {
        "content": "This is an updated content",
        "title": "This is an updated title"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=admin)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN


def test_partial_update_post_by_id_when_unauthenticated_returns_401(api_rf, posts):
    post = posts['post_2']
    url = reverse('post-detail', args=[post.id])
    data = {
        "content": "This is an updated content"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED

def test_partial_update_own_post_by_id_as_user_returns_200(api_rf, users, posts):
    user = users['user_1']
    post = posts['post_2']
    original_post = {
        'title': post.title,
        'content': post.content
    }
    url = reverse('post-detail', args=[post.id])
    data = {
        "content": "This is an updated content"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_200_OK

    post.refresh_from_db()
    assert post.content == data['content']
    assert post.title == original_post['title']

def test_partial_update_post_by_id_as_non_owner_return_403(api_rf, users, posts):
    user = users['user_2']
    post = posts['post_2']
    url = reverse('post-detail', args=[post.id])
    data = {
        "content": "This is an updated content"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_partial_update_post_by_id_as_admin_returns_403(api_rf, users, posts):
    admin = users['admin']
    post = posts['post_1']
    url = reverse('post-detail', args=[post.id])
    data = {
        "content": "This is an updated content"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=admin)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN


def test_partial_update_draft_by_id_when_unauthenticated_returns_401(api_rf, posts):
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id])
    data = {
        "content": "This is an updated content"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED

def test_partial_update_own_draft_by_id_as_user_returns_200(api_rf, users, posts):
    user = users['user_2']
    draft = posts['draft_2']
    original_post = {
        'title': draft.title,
        'content': draft.content
    }
    url = reverse('post-detail', args=[draft.id])
    data = {
        "content": "This is an updated content"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    draft.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert draft.content == data['content']
    assert draft.title == original_post['title']

def test_partial_update_draft_by_id_as_non_owner_return_403(api_rf, users, posts):
    user = users['user_1']
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id])
    data = {
        "content": "This is an updated content"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_partial_update_draft_by_id_as_admin_returns_403(api_rf, users, posts):
    admin = users['admin']
    draft = posts['draft_2']
    url = reverse('post-detail', args=[draft.id])
    data = {
        "content": "This is an updated content"
    }
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=admin)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_delete_post_by_id_when_unauthenticated_returns_401(api_rf, posts):
    post = posts['post_1']
    url = reverse('post-detail', args=[post.id])
    request = api_rf.delete(path=url)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED

def test_delete_own_post_by_id_as_user_returns_204(api_rf, users, posts):
    user = users['user_1']
    post = posts['post_1']
    url = reverse('post-detail', args=[post.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_post_by_id_as_non_owner_returns_403(api_rf, users, posts):
    user = users['user_2']
    post = posts['post_1']
    url = reverse('post-detail', args=[post.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_delete_post_by_id_as_admin_returns_204(api_rf, users, posts):
    admin = users['admin']
    post = posts['post_1']
    url = reverse('post-detail', args=[post.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=admin)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_admin_post_by_id_as_non_owner_admin_returns_204(api_rf, users, posts):
    admin = users['admin']
    post = posts['post_3']
    url = reverse('post-detail', args=[post.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=admin)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_draft_by_id_when_unauthenticated_returns_401(api_rf, posts):
    draft = posts['draft_3']
    url = reverse('post-detail', args=[draft.id])
    request = api_rf.delete(path=url)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED

def test_delete_own_draft_by_id_as_user_returns_204(api_rf, users, posts):
    user = users['user_2']
    draft = posts['draft_3']
    url = reverse('post-detail', args=[draft.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_draft_by_id_as_non_owner_returns_403(api_rf, users, posts):
    user = users['user_1']
    draft = posts['draft_3']
    url = reverse('post-detail', args=[draft.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_delete_draft_by_id_as_admin_returns_204(api_rf, users, posts):
    admin = users['admin']
    draft = posts['draft_3']
    url = reverse('post-detail', args=[draft.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=admin)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_admin_draft_by_id_as_non_owner_admin_returns_204(api_rf, users, posts):
    admin = users['admin']
    draft = posts['draft_4']
    url = reverse('post-detail', args=[draft.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=admin)
    view = PostRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, post_id=draft.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


# ======================= PopularPostListAPIView ==========================
def test_get_popular_posts_when_unauthenticated_returns_200(api_rf, users, posts):
    url = reverse('popular')
    request = api_rf.get(url)
    view = PopularPostListAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK

def test_get_popular_posts_as_user_returns_200(api_rf, users, posts):
    user = users['user_2']
    url = reverse('popular')
    request = api_rf.get(url)
    force_authenticate(request=request, user=user)
    view = PopularPostListAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK

def test_get_popular_posts_as_admin_returns_200(api_rf, users, posts):
    admin = users['admin']
    url = reverse('popular')
    request = api_rf.get(url)
    force_authenticate(request=request, user=admin)
    view = PopularPostListAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
