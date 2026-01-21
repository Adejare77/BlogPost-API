from django.db.models import Q
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from api.v2.tests.constants import FORBIDDEN, UNAUTHORIZED
from app.comment.models import Comment
from app.post.models import Post


class TestPostListCreateAPIView:
    def test_get_posts_when_unauthenticated_returns_200(self, published_posts, api_cl):
        url = reverse("v2:posts")
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_drafts_when_unauthenticated_returns_401(self, draft_posts, api_cl):
        url = reverse("v2:posts") + "?status=draft"
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_get_posts_n_drafts_when_unauthenticated_returns_401(
        self, published_posts, draft_posts, api_cl
    ):
        url = reverse("v2:posts") + "?status=all"
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_get_post_by_author_when_unauthenticated_returns_200(
        self, published_posts, api_cl
    ):
        author_full_name = published_posts[0].author.full_name
        url = reverse("v2:posts") + f"?author={author_full_name}"
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_draft_by_author_when_unauthenticated_returns_401(
        self, draft_posts, api_cl
    ):
        author_full_name = draft_posts[0].author.full_name
        url = reverse("v2:posts") + f"?status=draft&author={author_full_name}"
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_get_posts_n_drafts_by_author_when_unauthenticated_returns_401(
        self, published_posts, draft_posts, api_cl
    ):
        author_full_name = published_posts[0].author.full_name
        url = reverse("v2:posts") + f"?status=all&author={author_full_name}"
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_get_my_posts_when_unauthenticated_returns_401(
        self, published_posts, api_cl
    ):
        url = reverse("v2:posts") + "?author=me"
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_get_my_drafts_when_unauthenticated_returns_401(self, draft_posts, api_cl):
        url = reverse("v2:posts") + "?status=draft&author=me"
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_get_my_posts_n_drafts_when_unauthenticated_returns_401(
        self, published_posts, draft_posts, api_cl
    ):
        url = reverse("v2:posts") + "?status=all&author=me"
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_get_posts_by_user_returns_200(self, published_posts, user_client):
        url = reverse("v2:posts")
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_drafts_as_user_returns_200(self, draft_posts, users, user_client):
        url = reverse("v2:posts") + "?status=draft"
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

        for data in response.data["results"]:
            assert data["author"] == users[0].id

    def test_get_posts_n_drafts_as_user_returns_200(
        self, published_posts, draft_posts, users, user_client
    ):
        url = reverse("v2:posts") + "?status=all"
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

        for data in response.data["results"]:
            assert data["author"] == users[0].id

    def test_get_post_by_author_as_user_returns_200(self, published_posts, user_client):
        author_full_name = published_posts[0].author.full_name
        url = reverse("v2:posts") + f"?author={author_full_name}"
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_draft_by_author_as_user_returns_403(self, draft_posts, user_client):
        author_full_name = draft_posts[0].author.full_name
        url = reverse("v2:posts") + f"?status=draft&author={author_full_name}"
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_get_posts_n_drafts_by_author_as_user_returns_403(
        self, published_posts, draft_posts, user_client
    ):
        author_full_name = published_posts[0].author.full_name
        url = reverse("v2:posts") + f"?status=all&author={author_full_name}"
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_get_my_posts_as_user_returns_200(
        self, published_posts, users, user_client
    ):
        url = reverse("v2:posts") + "?author=me"
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

        for data in response.data["results"]:
            assert data["author"] == users[0].id

    def test_get_my_drafts_as_user_returns_200(self, draft_posts, users, user_client):
        url = reverse("v2:posts") + "?status=draft&author=me"
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

        for data in response.data["results"]:
            assert data["author"] == users[0].id

    def test_get_my_posts_n_drafts_as_user_returns_200(
        self, published_posts, draft_posts, users, user_client
    ):
        url = reverse("v2:posts") + "?status=all&author=me"
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

        for data in response.data["results"]:
            assert data["author"] == users[0].id

    def test_get_posts_by_admin_returns_200(self, published_posts, admin_client):
        url = reverse("v2:posts")
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_drafts_as_admin_returns_200(self, draft_posts, admin_client):
        url = reverse("v2:posts") + "?status=draft"
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_posts_n_drafts_as_admin_returns_200(
        self, published_posts, draft_posts, admin_client
    ):
        url = reverse("v2:posts") + "?status=all"
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_post_by_author_as_admin_returns_200(
        self, published_posts, admin_client
    ):
        author_full_name = published_posts[0].author.full_name
        url = reverse("v2:posts") + f"?author={author_full_name}"
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_draft_by_author_as_admin_returns_200(self, draft_posts, admin_client):
        author_full_name = draft_posts[0].author.full_name
        url = reverse("v2:posts") + f"?status=draft&author={author_full_name}"
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_posts_n_drafts_by_author_as_admin_returns_200(
        self, published_posts, draft_posts, admin_client
    ):
        author_full_name = published_posts[0].author.full_name
        url = reverse("v2:posts") + f"?status=all&author={author_full_name}"
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_my_posts_as_admin_returns_200(self, published_posts, admin_client):
        url = reverse("v2:posts") + "?author=me"
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK

    def test_get_my_drafts_as_admin_returns_200(self, draft_posts, admin_client):
        url = reverse("v2:posts") + "?status=draft&author=me"
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK

    def test_get_my_posts_n_drafts_as_admin_returns_200(
        self, published_posts, draft_posts, admin_client
    ):
        url = reverse("v2:posts") + "?status=all&author=me"
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK

    def test_create_post_when_unauthenticated_returns_401(
        self, published_posts, draft_posts, api_cl
    ):
        url = reverse("v2:posts")
        data = {"title": "This is a title", "content": "This is a Content"}
        response = api_cl.post(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_post_as_user_returns_201(db, user_client):
        url = reverse("v2:posts")
        data = {
            "title": "This is a title",
            "content": "This is a content",
            "is_published": True,
        }
        response = user_client.post(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.count() == 1

        post = Post.objects.get()
        assert post.title == data["title"]
        assert post.content == data["content"]
        assert post.is_published is True

    def test_create_post_as_admin_returns_201(db, admin_client):
        url = reverse("v2:posts")
        data = {"title": "This is a title", "content": "This is a content"}
        response = admin_client.post(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.count() == 1

        post = Post.objects.get()
        assert post.title == data["title"]
        assert post.content == data["content"]
        assert post.is_published is False


class TestPostRetrieveUpdateDestroyAPIView:
    def test_retrieve_post_when_unauthenticated_returns_200(
        self, published_posts, api_cl
    ):
        url = reverse("v2:post-detail", args=[published_posts[0].id])
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_draft_when_unauthenticated_returns_401(self, draft_posts, api_cl):
        url = reverse("v2:post-detail", args=[draft_posts[0].id])
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_update_post_when_uanuthenticated_returns_401(
        self, published_posts, api_cl
    ):
        url = reverse("v2:post-detail", args=[published_posts[0].id])
        data = {"content": "This is an edited content"}
        response = api_cl.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_update_draft_when_uanuthenticated_returns_401(self, draft_posts, api_cl):
        url = reverse("v2:post-detail", args=[draft_posts[0].id])
        data = {"content": "This is an edited content"}
        response = api_cl.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_delete_post_when_unauthenticated_returns_401(
        self, published_posts, api_cl
    ):
        url = reverse("v2:post-detail", args=[published_posts[0].id])
        response = api_cl.delete(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_delete_draft_when_unauthenticated_returns_401(self, draft_posts, api_cl):
        url = reverse("v2:post-detail", args=[draft_posts[0].id])
        response = api_cl.delete(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_retrieve_post_as_user_client_returns_200(
        self, published_posts, user_client
    ):
        url = reverse("v2:post-detail", args=[published_posts[0].id])
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_draft_as_user_client_returns_200(self, draft_posts, user_client):
        url = reverse("v2:post-detail", args=[draft_posts[0].id])
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data

    def test_retrieve_non_owner_draft_returns_403(self, draft_posts, user_client):
        url = reverse("v2:post-detail", args=[draft_posts[1].id])
        response = user_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_retireve_non_owner_draft_as_admin_returns_200(
        self, draft_posts, admin_client
    ):
        url = reverse("v2:post-detail", args=[draft_posts[1].id])
        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_update_post_as_user_client_returns_401(self, published_posts, user_client):
        url = reverse("v2:post-detail", args=[published_posts[0].id])
        data = {"content": "This is an edited content"}
        response = user_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_200_OK
        published_posts[0].refresh_from_db()

        assert published_posts[0].content == data["content"]

    def test_update_non_owner_post_returns_403(self, published_posts, user_client):
        url = reverse("v2:post-detail", args=[published_posts[1].id])
        data = {"content": "This is an edited content"}
        response = user_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_update_non_owner_post_as_admin_returns_403(
        self, published_posts, admin_client
    ):
        url = reverse("v2:post-detail", args=[published_posts[1].id])
        data = {"content": "This is an edited content"}
        response = admin_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_update_draft_as_user_client_returns_200(self, draft_posts, user_client):
        url = reverse("v2:post-detail", args=[draft_posts[0].id])
        data = {"title": "This is a title", "content": "This is an edited content"}
        response = user_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_200_OK
        draft_posts[0].refresh_from_db()

        assert draft_posts[0].title == data["title"]
        assert draft_posts[0].content == data["content"]

    def test_update_non_owner_draft_returns_403(self, draft_posts, user_client):
        url = reverse("v2:post-detail", args=[draft_posts[1].id])
        data = {"title": "This is a title", "content": "This is an edited content"}
        response = user_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_update_non_owner_draft_as_admin_returns_403(
        self, draft_posts, admin_client
    ):
        url = reverse("v2:post-detail", args=[draft_posts[0].id])
        data = {"title": "This is a title", "content": "This is an edited content"}
        response = admin_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_delete_post_as_user_client_returns_204(self, published_posts, user_client):
        url = reverse("v2:post-detail", args=[published_posts[0].id])
        response = user_client.delete(path=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_non_owner_post_as_user_returns_403(
        self, published_posts, user_client
    ):
        url = reverse("v2:post-detail", args=[published_posts[1].id])
        response = user_client.delete(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_non_owner_post_as_admin_returns_204(
        self, published_posts, admin_client
    ):
        url = reverse("v2:post-detail", args=[published_posts[1].id])
        response = admin_client.delete(path=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_draft_as_user_client_returns_204(self, draft_posts, user_client):
        url = reverse("v2:post-detail", args=[draft_posts[0].id])
        response = user_client.delete(path=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_non_owner_draft_as_user_returns_403(self, draft_posts, user_client):
        url = reverse("v2:post-detail", args=[draft_posts[1].id])
        response = user_client.delete(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_non_owner_draft_as_admin_returns_204(
        self, draft_posts, admin_client
    ):
        url = reverse("v2:post-detail", args=[draft_posts[1].id])
        response = admin_client.delete(path=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestCommentListCreateAPIView:
    def test_get_comments_when_unauthenticated_returns_200(
        self, comments, published_posts, api_cl
    ):
        url = reverse("v2:comments", args=[published_posts[0].id])
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_comments_as_user_returns_200(
        self, comments, published_posts, user_client
    ):
        url = reverse("v2:comments", args=[published_posts[0].id])
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_comments_as_admin_returns_200(
        self, comments, published_posts, admin_client
    ):
        url = reverse("v2:comments", args=[published_posts[0].id])
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_create_comment_when_unauthenticated_returns_401(
        self, comments, published_posts, api_cl
    ):
        url = reverse("v2:comments", args=[published_posts[0].id])
        data = {"content": "This is a comment"}
        response = api_cl.post(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_create_comment_as_user_returns_201(
        self, comments, published_posts, user_client
    ):
        url = reverse("v2:comments", args=[published_posts[0].id])
        comment_count = Comment.objects.count()
        data = {"content": "This is a comment"}
        response = user_client.post(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.count() == comment_count + 1

    def test_create_comment_as_admin_returns_201(
        self, comments, published_posts, admin_client
    ):
        url = reverse("v2:comments", args=[published_posts[0].id])
        comment_count = Comment.objects.count()
        data = {"content": "This is a comment"}
        response = admin_client.post(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.count() == comment_count + 1


class TestCommentRetrieveUpdateDestroyAPIView:
    def test_retrieve_comment_when_unauthenticated_returns_200(self, comments, api_cl):
        url = reverse("v2:comment-detail", args=[comments[0].id])
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data

    def test_retrieve_comment_as_user_returns_200(self, comments, user_client):
        url = reverse("v2:comment-detail", args=[comments[0].id])
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data

    def test_retrieve_comment_as_admin_returns_200(self, comments, admin_client):
        url = reverse("v2:comment-detail", args=[comments[0].id])
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data

    def test_update_comment_when_unauthenticated_returns_401(self, comments, api_cl):
        url = reverse("v2:comment-detail", args=[comments[0].id])
        data = {"content": "Update this comment"}
        response = api_cl.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_update_comment_as_user_returns_200(self, comments, user_client):
        url = reverse("v2:comment-detail", args=[comments[0].id])
        data = {"content": "Update this comment"}
        response = user_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_200_OK
        comments[0].refresh_from_db()

        assert comments[0].content == data["content"]

    def test_update_non_owner_comment_as_user_returns_403(self, comments, user_client):
        url = reverse("v2:comment-detail", args=[comments[2].id])
        data = {"content": "Update this comment"}
        response = user_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_update_non_owner_comment_as_admin_returns_403(
        self, comments, admin_client
    ):
        url = reverse("v2:comment-detail", args=[comments[0].id])
        data = {"content": "Update this comment"}
        response = admin_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_delete_comment_when_unauthenticated_returns_401(self, comments, api_cl):
        url = reverse("v2:comment-detail", args=[comments[0].id])
        response = api_cl.delete(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_delete_comment_as_user_returns_204(self, comments, user_client):
        url = reverse("v2:comment-detail", args=[comments[0].id])
        response = user_client.delete(path=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_non_owner_comment_as_user_returns_403(self, comments, user_client):
        url = reverse("v2:comment-detail", args=[comments[1].id])
        response = user_client.delete(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_delete_non_owner_comment_as_admin_returns_204(
        self, comments, admin_client
    ):
        url = reverse("v2:comment-detail", args=[comments[0].id])
        response = admin_client.delete(path=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestReplyListCreateAPIView:
    def test_get_replies_when_unauthenticated_returns_200(
        self, comments, replies, api_cl
    ):
        url = reverse("v2:replies", args=[comments[0].id])
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_replies_as_user_returns_200(self, comments, replies, user_client):
        url = reverse("v2:replies", args=[comments[0].id])
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_get_replies_as_admin_returns_200(self, comments, replies, admin_client):
        url = reverse("v2:replies", args=[comments[0].id])
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]

    def test_create_reply_when_unauthenticated_returns_401(
        self, comments, replies, api_cl
    ):
        url = reverse("v2:replies", args=[comments[0].id])
        data = {"content": "This is a reply"}
        response = api_cl.post(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_create_reply_as_user_returns_201(self, comments, replies, user_client):
        url = reverse("v2:replies", args=[comments[0].id])
        reply_count = Comment.objects.filter(Q(parent__isnull=False)).count()
        data = {"content": "This is a reply"}
        response = user_client.post(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert (
            Comment.objects.filter(Q(parent__isnull=False)).count() == reply_count + 1
        )

    def test_create_reply_as_admin_returns_201(self, comments, replies, admin_client):
        url = reverse("v2:replies", args=[comments[0].id])
        reply_count = Comment.objects.filter(Q(parent__isnull=False)).count()
        data = {"content": "This is a reply"}
        response = admin_client.post(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert (
            Comment.objects.filter(Q(parent__isnull=False)).count() == reply_count + 1
        )


class TestReplyRetrieveUpdateDestroyAPIView:
    def test_retrieve_reply_when_unauthenticated_returns_200(self, replies, api_cl):
        url = reverse("v2:reply-detail", args=[replies[0].id])
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data

    def test_retrieve_reply_as_user_returns_200(self, replies, user_client):
        url = reverse("v2:reply-detail", args=[replies[0].id])
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data

    def test_retrieve_reply_as_admin_returns_200(self, replies, admin_client):
        url = reverse("v2:reply-detail", args=[replies[0].id])
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data

    def test_update_reply_when_unauthenticated_returns_401(self, replies, api_cl):
        url = reverse("v2:reply-detail", args=[replies[0].id])
        data = {"content": "Update this reply"}
        response = api_cl.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_update_reply_as_user_returns_200(self, replies, user_client):
        url = reverse("v2:reply-detail", args=[replies[0].id])
        data = {"content": "Update this reply"}
        response = user_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_200_OK
        replies[0].refresh_from_db()

        assert replies[0].content == data["content"]

    def test_update_non_owner_reply_as_user_returns_403(self, replies, user_client):
        url = reverse("v2:reply-detail", args=[replies[2].id])
        data = {"content": "Update this reply"}
        response = user_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_update_non_owner_reply_as_admin_returns_403(self, replies, admin_client):
        url = reverse("v2:reply-detail", args=[replies[0].id])
        data = {"content": "Update this reply"}
        response = admin_client.patch(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_delete_reply_when_unauthenticated_returns_401(self, replies, api_cl):
        url = reverse("v2:reply-detail", args=[replies[0].id])
        response = api_cl.delete(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_delete_reply_as_user_returns_204(self, replies, user_client):
        url = reverse("v2:reply-detail", args=[replies[0].id])
        response = user_client.delete(path=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_non_owner_reply_as_user_returns_403(self, replies, user_client):
        url = reverse("v2:reply-detail", args=[replies[1].id])
        response = user_client.delete(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_delete_non_owner_reply_as_admin_returns_204(self, replies, admin_client):
        url = reverse("v2:reply-detail", args=[replies[0].id])
        response = admin_client.delete(path=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestUserListAPIView:
    def test_get_users_when_authenticated_returns_401(self, api_cl, users):
        url = reverse("v2:all-users")
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_get_users_as_user_returns_403(self, users, user_client):
        url = reverse("v2:all-users")
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_get_users_as_admin_returns_200(self, users, admin_client):
        url = reverse("v2:all-users")
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"]


class TestUserRetrieveAPIView:
    def test_retrieve_user_profile_when_authenticated_returns_401(self, users, api_cl):
        url = reverse("v2:user-profile", args=[users[0].id])
        response = api_cl.get(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_retrieve_user_profile_as_user_returns_200(self, users, user_client):
        url = reverse("v2:user-profile", args=[users[0].id])
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data

    def test_retrieve_non_owner_profile_as_user_returns_403(self, users, user_client):
        url = reverse("v2:user-profile", args=[users[1].id])
        response = user_client.get(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_retrieve_user_profile_as_admin_returns_200(self, users, admin_client):
        url = reverse("v2:user-profile", args=[users[0].id])
        response = admin_client.get(path=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data


class TestDisableUserAPIView:
    def test_disable_user_when_unauthenticated_returns_401(self, users, api_cl):
        url = reverse("v2:disable-account", args=[users[0].id])
        response = api_cl.post(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_disable_user_as_user_returns_403(self, users, user_client):
        url = reverse("v2:disable-account", args=[users[0].id])
        response = user_client.post(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_disable_non_owner_user_as_user_returns_403(self, users, user_client):
        url = reverse("v2:disable-account", args=[users[2].id])
        response = user_client.post(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_disable_user_as_admin_returns_204(self, users, admin_client):
        url = reverse("v2:disable-account", args=[users[0].id])
        response = admin_client.post(path=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestEnableUserAPIView:
    def test_enable_user_when_unauthenticated_returns_401(self, users, api_cl):
        url = reverse("v2:enable-account", args=[users[0].id])
        response = api_cl.post(path=url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == UNAUTHORIZED

    def test_enable_user_as_user_returns_403(self, users, user_client):
        url = reverse("v2:enable-account", args=[users[0].id])
        response = user_client.post(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_enable_non_owner_user_as_user_returns_403(self, users, user_client):
        url = reverse("v2:enable-account", args=[users[2].id])
        response = user_client.post(path=url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == FORBIDDEN

    def test_enable_user_as_admin_returns_204(self, users, admin_client):
        url = reverse("v2:enable-account", args=[users[0].id])
        response = admin_client.post(path=url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestCreateUserAPIView:
    def test_register_user_returns_201(self, db, api_cl):
        url = reverse("v2:sign-up")
        data = {
            "full_name": "TESTING",
            "email": "testing@gmail.com",
            "password": "testing123",
        }
        response = api_cl.post(path=url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED


class TestLogoutAPIView:
    def test_logout_blacklist_refresh_token(self, api_cl, users):
        user = users[3]

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        api_cl.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("v2:logout")
        response = api_cl.post(
            path=url, data={"refresh_token": str(refresh)}, format="json"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists()

        assert "access_token" in response.cookies
        assert response.cookies["access_token"]["max-age"] == 0

        assert "refresh_token" in response.cookies
        assert response.cookies["refresh_token"]["max-age"] == 0
