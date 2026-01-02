from api.v2.comment.views import (
    CommentListCreateAPIView,
    CommentRetrieveUpdateDestroyAPIView,
    ReplyListCreateAPIView,
    ReplyRetrieveUpdateDestroyAPIView
)
from app.post.models import Post
from app.comment.models import Comment
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate
from django.urls import reverse
from rest_framework import status
from api.v2.comment.tests.constants import UNAUTHORIZED, FORBIDDEN
import uuid


# ============================ CommentListCreateAPIView ===================

def test_get_comments_with_invalid_post_id_returns_404(posts, api_rf):
    id = uuid.uuid4()
    url = reverse('comments', args=[id])
    request = api_rf.get(path=url)
    view = CommentListCreateAPIView.as_view()

    response = view(request, post_id=id)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'Post not found.'


def test_get_comments_when_unauthenticated_returns_200(posts, comments, api_rf):
    post = posts['post_1']
    url = reverse('comments', args=[post.id])
    request = api_rf.get(path=url)
    view = CommentListCreateAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_200_OK

    assert response.data['results']


def test_get_comments_as_user_returns_200(users, posts, comments, api_rf):
    user = users['user_1']
    post = posts['post_1']
    url = reverse('comments', args=[post.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = CommentListCreateAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['results']


def test_get_comments_as_admin_returns_200(users, posts, comments, api_rf):
    admin = users['admin']
    post = posts['post_1']
    url = reverse('comments', args=[post.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = CommentListCreateAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['results']


def test_create_comments_when_unauthenticated_returns_401(users, posts, comments, api_rf):
    post = posts['post_1']
    url = reverse('comments', args=[post.id])
    data = {'content': "This is a new comment"}
    request = api_rf.post(path=url, data=data, format='json')
    view = CommentListCreateAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED


def test_create_comments_as_user_returns_201(users, posts, comments, api_rf):
    user = users['user_1']
    post = posts['post_1']
    url = reverse('comments', args=[post.id])
    data = {'content': "This is a new comment"}
    request = api_rf.post(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = CommentListCreateAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['content'] == data['content']


def test_create_comments_as_admin_returns_201(users, posts, comments, api_rf):
    admin = users['admin']
    post = posts['post_1']
    url = reverse('comments', args=[post.id])
    data = {'content': "This is a new comment"}
    request = api_rf.post(path=url, data=data, format='json')
    force_authenticate(request=request, user=admin)
    view = CommentListCreateAPIView.as_view()

    response = view(request, post_id=post.id)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['content'] == data['content']


def test_create_comments_with_invalid_post_id_returns_404(users, comments, api_rf):
    user = users['user_1']
    invalid_id = uuid.uuid4()
    url = reverse('comments', args=[invalid_id])
    data = {'content': "This is a new comment"}
    request = api_rf.post(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = CommentListCreateAPIView.as_view()

    response = view(request, post_id=invalid_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'Post not found.'

def test_no_n_plus_one_queries(self, comments, api_rf, django_assert_num_queries):
        with django_assert_num_queries(3):
            url = reverse('comments')
            request = api_rf.get(path=url)
            view = CommentListCreateAPIView.as_view()

            response = view(request)

            assert response.status_code == status.HTTP_200_OK

# ========================= CommentRetrieveUpdateDestroyAPIView =======================

def test_retrieve_comment_with_invalid_comment_id_returns_404(users, comments, api_rf):
    invalid_comment_id = uuid.uuid4()
    url = reverse('comment-detail', args=[invalid_comment_id])
    request = api_rf.get(path=url)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=invalid_comment_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'Comment not found.'


def test_retrieve_comment_when_unauthenticated_returns_200(users, comments, api_rf):
    comment = comments['comment_1']
    user = users['user_1']
    url = reverse('comment-detail', args=[comment.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_200_OK


def test_retrieve_comment_as_user_returns_200(users, comments, api_rf):
    comment = comments['comment_1']
    user = users['user_1']
    url = reverse('comment-detail', args=[comment.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_200_OK


def test_retrieve_comment_as_admin_returns_200(users, comments, api_rf):
    comment = comments['comment_1']
    admin = users['admin']
    url = reverse('comment-detail', args=[comment.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_200_OK


def test_update_comment_when_unauthenticated_returns_401(users, comments, api_rf):
    comment = comments['comment_1']
    url = reverse('comment-detail', args=[comment.id])
    data = {'content': 'This is the updated comment'}
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED


def test_update_comment_as_user_returns_200(db, users, comments, api_rf):
    comment = comments['comment_1']
    user = users['user_1']
    url = reverse('comment-detail', args=[comment.id])
    data = {'content': 'This is the updated comment'}
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_200_OK

    comment.refresh_from_db()
    assert comment.content == data['content']

def test_update_comment_as_non_owner_returns_403(users, comments, api_rf):
    comment = comments['comment_1']
    user = users['user_2']
    url = reverse('comment-detail', args=[comment.id])
    data = {'content': 'This is the updated comment'}
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN


def test_update_user_comments_as_admin_returns_403(users, comments, api_rf):
    comment = comments['comment_1']
    admin = users['admin']
    url = reverse('comment-detail', args=[comment.id])
    data = {'content': 'This is the updated comment'}
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=admin)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN


def test_update_comment_with_invalid_comment_id_returns_404(users, comments, api_rf):
    invalid_comment_id = uuid.uuid4()
    user = users['user_1']
    url = reverse('comment-detail', args=[invalid_comment_id])
    data = {'content': 'This is the updated comment'}
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=invalid_comment_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_comment_when_unauthenticated_returns_401(users, comments, api_rf):
    comment = comments['comment_1']
    url = reverse('comment-detail', args=[comment.id])
    request = api_rf.delete(path=url)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED


def test_delete_comment_as_user_returns_204(users, comments, api_rf):
    comment = comments['comment_1']
    user = users['user_1']
    url = reverse('comment-detail', args=[comment.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_comment_as_non_owner_returns_403(users, comments, api_rf):
    comment = comments['comment_1']
    user = users['user_2']
    url = reverse('comment-detail', args=[comment.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN


def test_delete_users_comment_as_admin_returns_403(users, comments, api_rf):
    comment = comments['comment_1']
    admin = users['admin']
    url = reverse('comment-detail', args=[comment.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=admin)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_comment_with_invalid_comment_id_returns_404(users, comments, api_rf):
    invalid_comment_id = uuid.uuid4()
    admin = users['admin']
    url = reverse('comment-detail', args=[invalid_comment_id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=admin)
    view = CommentRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, comment_id=invalid_comment_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'Comment not found.'


# ===================== ReplyListCreateAPIView =======================

def test_get_replies_with_invalid_comment_id_returns_404(comments, api_rf):
    invalid_comment_id = uuid.uuid4()
    url = reverse('replies', args=[invalid_comment_id])
    request = api_rf.get(path=url)
    view = ReplyListCreateAPIView.as_view()

    response = view(request, comment_id=invalid_comment_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    pass

def test_get_replies_when_unauthenticated_returns_200(api_rf, comments):
    comment = comments['comment_1']
    url = reverse('replies', args=[comment.id])
    request = api_rf.get(path=url)
    view = ReplyListCreateAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['results']

def test_get_replies_as_user_returns_200(users, comments, api_rf):
    user = users['user_1']
    comment = comments['comment_1']
    url = reverse('replies', args=[comment.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = ReplyListCreateAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['results']


def test_get_replies_as_admin_returns_200(users, comments, api_rf):
    admin = users['admin']
    comment = comments['comment_1']
    url = reverse('replies', args=[comment.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = ReplyListCreateAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_200_OK


def test_create_replies_when_unauthenticated_returns_401(comments, api_rf):
    comment = comments['comment_1']
    url = reverse('replies', args=[comment.id])
    data = {'content': 'This is a reply'}
    request = api_rf.post(path=url, data=data, format='json')
    view = ReplyListCreateAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED


def test_create_replies_as_user_returns_201(users, comments, api_rf):
    user = users['user_1']
    comment = comments['comment_2']
    url = reverse('replies', args=[comment.id])
    data = {'content': 'This is a reply'}
    request = api_rf.post(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = ReplyListCreateAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_201_CREATED


def test_create_replies_as_admin_returns_201(users, comments, api_rf):
    admin = users['admin']
    comment = comments['comment_1']
    url = reverse('replies', args=[comment.id])
    data = {'content': 'This is a reply'}
    request = api_rf.post(path=url, data=data, format='json')
    force_authenticate(request=request, user=admin)
    view = ReplyListCreateAPIView.as_view()

    response = view(request, comment_id=comment.id)

    assert response.status_code == status.HTTP_201_CREATED


def test_create_replies_with_invalid_comment_id_returns_404(users, comments, api_rf):
    admin = users['admin']
    invalid_comment_id = uuid.uuid4()

    url = reverse('replies', args=[invalid_comment_id])
    data = {'content': 'This is a reply'}
    request = api_rf.post(path=url, data=data, format='json')
    force_authenticate(request=request, user=admin)
    view = ReplyListCreateAPIView.as_view()

    response = view(request, comment_id=invalid_comment_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND



# ========================= ReplyRetrieveUpdateDestroyAPIView =======================

def test_retrieve_reply_with_invalid_reply_id_returns_404(comments, api_rf):
    invalid_comment_id = uuid.uuid4()
    url = reverse('reply-detail', args=[invalid_comment_id])
    request = api_rf.get(path=url)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=invalid_comment_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_retrieve_reply_when_unauthenticated_returns_200(comments, api_rf):
    reply = comments['reply_3']
    url = reverse('reply-detail', args=[reply.id])
    request = api_rf.get(path=url)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_200_OK


def test_retrieve_reply_as_user_returns_200(users, comments, api_rf):
    user = users['user_1']
    reply = comments['reply_1']
    url = reverse('reply-detail', args=[reply.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=user)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_200_OK


def test_retrieve_reply_as_admin_returns_200(users, comments, api_rf):
    admin = users['admin']
    reply = comments['reply_2']
    url = reverse('reply-detail', args=[reply.id])
    request = api_rf.get(path=url)
    force_authenticate(request=request, user=admin)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_200_OK


def test_update_reply_when_unauthenticated_returns_401(comments, api_rf):
    reply = comments['reply_1']
    url = reverse('reply-detail', args=[reply.id])
    data = {'content': 'This is an updated reply'}
    request = api_rf.patch(path=url, data=data, format='json')
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED


def test_update_reply_as_user_returns_200(users, comments, api_rf):
    user = users['user_2']
    reply = comments['reply_1']
    url = reverse('reply-detail', args=[reply.id])
    data = {'content': 'This is an updated reply'}
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_200_OK

    reply.refresh_from_db()
    assert reply.content == data['content']


def test_update_reply_as_non_owner_returns_403(users, comments, api_rf):
    user = users['user_1']
    reply = comments['reply_2']
    url = reverse('reply-detail', args=[reply.id])
    data = {'content': 'This is an updated reply'}
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN


def test_update_user_reply_as_admin_returns_403(users, comments, api_rf):
    admin = users['admin']
    reply = comments['reply_3']
    url = reverse('reply-detail', args=[reply.id])
    data = {'content': 'This is an updated reply'}
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=admin)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN


def test_update_reply_with_invalid_reply_id_returns_404(users, comments, api_rf):
    user = users['user_1']
    invalid_reply_id = uuid.uuid4()
    url = reverse('reply-detail', args=[invalid_reply_id])
    data = {'content': 'This is an updated reply'}
    request = api_rf.patch(path=url, data=data, format='json')
    force_authenticate(request=request, user=user)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=invalid_reply_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_reply_when_unauthenticated_returns_401(comments, api_rf):
    reply = comments['reply_2']
    url = reverse('reply-detail', args=[reply.id])
    request = api_rf.delete(path=url)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == UNAUTHORIZED

def test_delete_reply_as_user_returns_204(users, comments, api_rf):
    user = users['user_3']
    reply = comments['reply_2']
    url = reverse('reply-detail', args=[reply.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_reply_as_non_owner_returns_403(users, comments, api_rf):
    user = users['user_1']
    reply = comments['reply_2']
    url = reverse('reply-detail', args=[reply.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=user)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data['detail'] == FORBIDDEN

def test_delete_users_reply_as_admin_returns_204(users, comments, api_rf):
    admin = users['admin']
    reply = comments['reply_2']
    url = reverse('reply-detail', args=[reply.id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=admin)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=reply.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_reply_with_invalid_reply_id_returns_404(users, comments, api_rf):
    admin = users['admin']
    invalid_reply_id = uuid.uuid4()
    url = reverse('reply-detail', args=[invalid_reply_id])
    request = api_rf.delete(path=url)
    force_authenticate(request=request, user=admin)
    view = ReplyRetrieveUpdateDestroyAPIView.as_view()

    response = view(request, reply_id=invalid_reply_id)

    assert response.status_code == status.HTTP_404_NOT_FOUND


