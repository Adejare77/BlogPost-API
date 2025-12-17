from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from api.v1.comment import views
from app.comment.models import Comment
from app.post.models import Post


class CommentListViewTests(APITestCase):
    def setUp(self):
        """Set up user, post, and comments"""
        self.user1 = get_user_model().objects.create_user(
            full_name="ABCD", email="testing1@gmail.com", password="testing123"
        )
        self.user2 = get_user_model().objects.create_user(
            full_name="RSTU", email="testing2@gmail.com", password="testing456"
        )

        self.post1 = Post.objects.create(
            title="This is a Sample Title A",
            content="""
            The debate on whether mathematics should be made compulsory in
            schools shouldn't be controversial in the first place
            """,
            is_published=True,
            author=self.user1,
        )

        self.post2 = Post.objects.create(
            title="This is a Sample Title B",
            content="""
            The debate on whether English should be made compulsory in
            schools shouldn't be controversial in the first place
            """,
            is_published=True,
            author=self.user2,
        )

        self.factory = APIRequestFactory()

        self.post3 = Post.objects.create(
            title="This is a Sample Title C",
            content="""
            The debate on whether immigration into Nigeria raise a lot of
             questions that needed to be answered. It's about time we don't
             shy from it
            """,
            author=self.user1,
        )

    def test_create_comment_without_auth(self):
        """Test creating a comment without authentication"""
        url = reverse("comments", args=[self.post1.isbn])
        data = {"content": "This is a very nice Post. Please, keep it up!"}
        request = self.factory.post(url, data=data)

        response = views.post_comments(request, self.post1.isbn)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    def test_create_comment_with_auth(self):
        """Create a comment after authentication"""
        url = reverse("comments", args=[self.post1.isbn])
        data = {"content": "This is a very nice Post. Please, keep it up!"}
        request = self.factory.post(url, data=data, format="json")
        force_authenticate(request=request, user=self.user2)

        response = views.post_comments(request, self.post1.isbn)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data["content"])

    def test_create_empty_comment(self):
        """Test creating an empty comment with authentication"""
        url = reverse("comments", args=[self.post2.isbn])
        data = {"content": ""}
        request = self.factory.post(path=url, data=data, format="json")
        force_authenticate(request=request, user=self.user1)

        response = views.post_comments(request, self.post2.isbn)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content field cannot be empty", response.data["content"][0])

    def test_create_comment_on_draft_post(self):
        """Test commenting on a draft with authentication"""
        url = reverse("comments", args=[self.post3.isbn])
        data = {"content": "Very good write up"}
        request = self.factory.post(path=url, data=data, format="json")
        force_authenticate(request=request, user=self.user1)

        response = views.post_comments(request, self.post3.isbn)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Post not found")

    def test_get_comments_without_auth(self):
        """Test getting comments without authentication"""
        url = reverse("comments", args=[self.post2.isbn])
        request = self.factory.get(url)

        response = views.post_comments(request, self.post2.isbn)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_with_auth(self):
        """Test getting comments with authentication"""
        url = reverse("comments", args=[self.post2.isbn])
        request = self.factory.get(path=url)
        force_authenticate(request=request, user=self.user2)

        response = views.post_comments(request, self.post2.isbn)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CommentDetailViewTests(APITestCase):
    def setUp(self):
        """Set up user, post, and comments"""
        self.user1 = get_user_model().objects.create_user(
            full_name="ABCD", email="testing1@gmail.com", password="testing123"
        )
        self.user2 = get_user_model().objects.create_user(
            full_name="RSTU", email="testing2@gmail.com", password="testing456"
        )
        self.admin = get_user_model().objects.create_superuser(
            full_name="LMN", email="admin@gmail.com", password="adminPriviledge"
        )

        self.post1 = Post.objects.create(
            title="This is a Sample Title A",
            content="""
            The debate on whether mathematics should be made compulsory in
            schools shouldn't be controversial in the first place
            """,
            is_published=True,
            author=self.user1,
        )

        self.post2 = Post.objects.create(
            title="This is a Sample Title B",
            content="""
            The debate on whether English should be made compulsory in
            schools shouldn't be controversial in the first place
            """,
            is_published=True,
            author=self.user2,
        )

        self.post3 = Post.objects.create(
            title="This is a Sample Title C",
            content="""
            The debate on whether immigration into Nigeria raise a lot of
             questions that needed to be answered. It's about time we don't
             shy from it
            """,
            author=self.user1,
        )

        self.comment1 = Comment.objects.create(
            post=self.post1,
            author=self.user2,
            content="Nice blog. Thanks for the heads-up",
        )
        self.comment2 = Comment.objects.create(
            post=self.post2,
            author=self.user2,
            content="Wow. I didn't know this. I'll definitely try it out",
        )

        self.factory = APIRequestFactory()

    def test_delete_comment_without_auth(self):
        """Test deleting other's comment without authentication"""
        url = reverse("comment-detail", args=[self.comment1.id])
        request = self.factory.delete(path=url)

        response = views.post_comment_detail(request, self.comment1.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    def test_delete_own_comment_with_auth(self):
        """Test deleting created comment after authentication"""
        url = reverse("comment-detail", args=[self.comment1.id])
        request = self.factory.delete(path=url)
        force_authenticate(request=request, user=self.user2)

        response = views.post_comment_detail(request, self.comment1.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_others_comment_with_auth(self):
        """Test deleting other users comment after authentication"""
        url = reverse("comment-detail", args=[self.comment2.id])
        request = self.factory.delete(url)
        force_authenticate(request=request, user=self.user1)

        response = views.post_comment_detail(request, self.comment1.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_any_comment(self):
        """Test deleting users comment with admin authentitcation"""
        url = reverse("comment-detail", args=[self.comment2.id])
        request = self.factory.delete(path=url)
        force_authenticate(request=request, user=self.admin)

        response = views.post_comment_detail(request, self.comment2.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_comment_without_auth(self):
        """Test updating user's comment without authentication"""
        url = reverse("comment-detail", args=[self.comment1.id])
        data = {"content": "Wow, I'm very famous, thanks for the likes"}
        request = self.factory.patch(path=url, data=data)

        response = views.post_comment_detail(request, self.comment1.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_own_comment_with_auth(self):
        """Test updating my comment with authentication"""
        url = reverse("comment-detail", args=[self.comment1.id])
        data = {"content": "Wow, I'm very famous, thanks for the likes"}
        request = self.factory.patch(path=url, data=data)
        force_authenticate(request=request, user=self.user2)

        response = views.post_comment_detail(request, self.comment1.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], data["content"])

    def test_update_others_comment_with_auth(self):
        """Test updating other's' comment with authentication"""
        url = reverse("comment-detail", args=[self.comment2.id])
        data = {"content": "This isn't meant to work"}
        request = self.factory.patch(path=url, data=data)
        force_authenticate(request=request, user=self.user1)

        response = views.post_comment_detail(request, self.comment2.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_comment_without_auth(self):
        """Test getting a detail comment without authentication"""
        url = reverse("comment-detail", args=[self.comment1.id])
        request = self.factory.get(url)

        response = views.post_comment_detail(request, self.comment1.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_comment_with_auth(self):
        """Test getting a detail comment with authentication"""
        url = reverse("comment-detail", args=[self.comment2.id])
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user1)

        response = views.post_comment_detail(request, self.comment2.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ReplyListViewTests(APITestCase):
    def setUp(self):
        """set-up for reply to comment"""
        self.user1 = get_user_model().objects.create_user(
            full_name="ABCD", email="testing1@gmail.com", password="testing123"
        )
        self.user2 = get_user_model().objects.create_user(
            full_name="RSTU", email="testing2@gmail.com", password="testing456"
        )
        self.admin = get_user_model().objects.create_superuser(
            full_name="LMN", email="admin@gmail.com", password="adminPriviledge"
        )

        self.post1 = Post.objects.create(
            title="This is a Sample Title A",
            content="""
            The debate on whether mathematics should be made compulsory in
            schools shouldn't be controversial in the first place
            """,
            is_published=True,
            author=self.user1,
        )

        self.post2 = Post.objects.create(
            title="This is a Sample Title B",
            content="""
            The debate on whether English should be made compulsory in
            schools shouldn't be controversial in the first place
            """,
            is_published=True,
            author=self.user2,
        )

        self.post3 = Post.objects.create(
            title="This is a Sample Title C",
            content="""
            The debate on whether immigration into Nigeria raise a lot of
             questions that needed to be answered. It's about time we don't
             shy from it
            """,
            author=self.user1,
        )

        self.comment1 = Comment.objects.create(
            post=self.post1,
            author=self.user2,
            content="Nice blog. Thanks for the heads-up",
        )
        self.comment2 = Comment.objects.create(
            post=self.post2,
            author=self.user2,
            content="Wow. I didn't know this. I'll definitely try it out",
        )

        self.factory = APIRequestFactory()

    def test_create_reply_without_auth(self):
        """Test creating a reply withou authentication"""
        url = reverse("replies", args=[self.comment1.id])
        data = {"content": "This is a reply to your comment"}
        request = self.factory.post(path=url, data=data, format="json")

        response = views.comment_replies(request, self.comment1.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    def test_create_reply_with_auth(self):
        """Test creating a reply with authentication"""
        url = reverse("replies", args=[self.comment1.id])
        data = {"content": "This is a reply to your comment"}
        request = self.factory.post(path=url, data=data, format="json")
        force_authenticate(request=request, user=self.user1)

        response = views.comment_replies(request, self.comment1.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["parent"], self.comment1.id)
        self.assertEqual(response.data["content"], data["content"])

    def test_create_reply_with_empty_content(self):
        """Test creating a empty content reply with authentication"""
        url = reverse("replies", args=[self.comment2.id])
        data = {"content": ""}
        request = self.factory.post(path=url, data=data)
        force_authenticate(request=request, user=self.user1)

        response = views.comment_replies(request, self.comment2.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content field cannot be empty", response.data["content"][0])

    def test_create_reply_with_missing_content(self):
        """Test creating reply with authentication and missing content"""
        url = reverse("replies", args=[self.comment2.id])
        data = {}
        request = self.factory.post(path=url, data=data)
        force_authenticate(request=request, user=self.user1)

        response = views.comment_replies(request, self.comment2.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content field is required", response.data["content"][0])

    # def test_create_reply_with_invalid_comment_id(self):
    #     """ test creating reply with invalid comment Id """
    #     url = reverse('replies', args=['5471-8751-sqd7-fdse'])
    #     data = {'content': 'This is not meant to work'}
    #     request = self.factory.post(path=url, data=data)
    #     force_authenticate(request=request, user=self.user2)

    #     response = views.comment_replies(request, '5471-8751-sqd7-fdse')

    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #     self.assertEqual(response.data['detail'], 'Reply not found')

    def test_get_replies_without_auth(self):
        """Test getting replies to comment without authentication"""
        url = reverse("replies", args=[self.comment1.id])
        request = self.factory.get(url)

        response = views.comment_replies(request, self.comment1.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ReplyDetailViewTests(APITestCase):
    def setUp(self):
        """set-up for a specififc reply"""
        self.user1 = get_user_model().objects.create_user(
            full_name="ABCD", email="testing1@gmail.com", password="testing123"
        )
        self.user2 = get_user_model().objects.create_user(
            full_name="RSTU", email="testing2@gmail.com", password="testing456"
        )
        self.admin = get_user_model().objects.create_superuser(
            full_name="LMN", email="admin@gmail.com", password="adminPriviledge"
        )

        self.post1 = Post.objects.create(
            title="This is a Sample Title A",
            content="""
            The debate on whether mathematics should be made compulsory in
            schools shouldn't be controversial in the first place
            """,
            is_published=True,
            author=self.user1,
        )

        self.post2 = Post.objects.create(
            title="This is a Sample Title B",
            content="""
            The debate on whether English should be made compulsory in
            schools shouldn't be controversial in the first place
            """,
            is_published=True,
            author=self.user2,
        )

        self.post3 = Post.objects.create(
            title="This is a Sample Title C",
            content="""
            The debate on whether immigration into Nigeria raise a lot of
             questions that needed to be answered. It's about time we don't
             shy from it
            """,
            author=self.user1,
        )

        self.comment1 = Comment.objects.create(
            post=self.post1,
            author=self.user2,
            content="Nice blog. Thanks for the heads-up",
        )
        self.comment2 = Comment.objects.create(
            post=self.post2,
            author=self.user2,
            content="Wow. I didn't know this. I'll definitely try it out",
        )

        self.reply1 = Comment.objects.create(
            post=self.post1,
            author=self.user1,
            content="This is the first reply",
            parent=self.comment1,
        )

        self.reply2 = Comment.objects.create(
            post=self.post1,
            author=self.user2,
            content="This is the second reply",
            parent=self.comment1,
        )

        self.reply3 = Comment.objects.create(
            post=self.post1,
            author=self.user1,
            content="This is the third reply",
            parent=self.comment1,
        )

        self.reply4 = Comment.objects.create(
            post=self.post1,
            author=self.admin,
            content="This is the fourth reply",
            parent=self.comment1,
        )
        self.factory = APIRequestFactory()

    def test_retrieve_a_reply_without_auth(self):
        """Test getting a reply detail without authentication"""
        url = reverse("reply-detail", args=[self.reply1.id])
        request = self.factory.get(url)

        response = views.comment_reply_details(request, self.reply1.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_a_reply_with_auth(self):
        """Test getting a detailed reply with authentication"""
        url = reverse("reply-detail", args=[self.reply1.id])
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user1)

        response = views.comment_reply_details(request, self.reply1.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_reply_without_auth(self):
        """Test updating a reply without authentication"""
        url = reverse("reply-detail", args=[self.reply2.id])
        data = {"content": "This is the updated reply"}
        request = self.factory.patch(path=url, data=data, format="json")

        response = views.comment_reply_details(request, self.reply2.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    def test_update_own_reply_with_auth(self):
        """Test updating own reply with authentication"""
        url = reverse("reply-detail", args=[self.reply2.id])
        data = {"content": "This is the updated reply"}
        request = self.factory.patch(path=url, data=data, format="json")
        force_authenticate(request=request, user=self.user2)

        response = views.comment_reply_details(request, self.reply2.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], data["content"])

    def test_update_others_reply_with_auth(self):
        """Test updating other's reply with authentication"""
        url = reverse("reply-detail", args=[self.reply3.id])
        data = {"content": "This is the new update on reply"}
        request = self.factory.patch(path=url, data=data, format="json")
        force_authenticate(request=request, user=self.user2)

        response = views.comment_reply_details(request, self.reply3.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "You do not have permission to perform this action"
        )

    def test_update_reply_with_empty_content(self):
        """Test updating with empty content"""
        url = reverse("reply-detail", args=[self.reply1.id])
        data = {"content": ""}
        request = self.factory.patch(path=url, data=data, format="json")
        force_authenticate(request=request, user=self.user1)

        response = views.comment_reply_details(request, self.reply1.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content field cannot be empty", response.data["content"][0])

    def test_update_reply_with_missing_content_field(self):
        """Test updating wiht a missing content field"""
        url = reverse("reply-detail", args=[self.reply2.id])
        data = {}
        request = self.factory.patch(path=url, data=data, format="json")
        force_authenticate(request=request, user=self.user2)

        response = views.comment_reply_details(request, self.reply2.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_reply_without_auth(self):
        """Test deleting a reply without authentication"""
        url = reverse("reply-detail", args=[self.reply3.id])
        request = self.factory.delete(path=url)

        response = views.comment_reply_details(request, self.reply3.id)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    def test_delete_own_reply_with_authentication(self):
        """Test deleting own reply after authentication"""
        url = reverse("reply-detail", args=[self.reply3.id])
        request = self.factory.delete(path=url)
        force_authenticate(request=request, user=self.user1)

        response = views.comment_reply_details(request, self.reply3.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_others_reply_with_auth(self):
        """Test deleting other's reply with authentication"""
        url = reverse("reply-detail", args=[self.reply2.id])
        request = self.factory.delete(path=url)
        force_authenticate(request=request, user=self.user1)

        response = views.comment_reply_details(request, self.reply2.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "You do not have permission to perform this action"
        )

    def test_admin_can_delete_any_reply(self):
        """Test admin can delete user's reply"""
        url = reverse("reply-detail", args=[self.reply2.id])
        request = self.factory.delete(path=url)
        force_authenticate(request=request, user=self.admin)

        response = views.comment_reply_details(request, self.reply2.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
