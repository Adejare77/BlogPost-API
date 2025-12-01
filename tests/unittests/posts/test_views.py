from django.contrib.auth import get_user_model
from django.urls import reverse
from parameterized import parameterized
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from post import views
from post.models import Post

User = get_user_model()


class PostListViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            **{"full_name": "ABC", "email": "testing1@gmail.com", "password": "123"}
        )
        self.post1 = Post.objects.create(
            title="User 1 First Post",
            content="This is my first post",
            is_published=True,
            author=self.user,
        )
        Post.objects.create(
            title="User 1 First Post",
            content="This is my first post",
            is_published=False,
            author=self.user,
        )

        self.admin = User.objects.create_user(
            **{"full_name": "CDE", "email": "testing2@gmail.com", "password": "123"}
        )

    def test_create_post_with_authentication(self):
        """Test creating a post"""
        url = reverse("posts")
        data = {"title": "Linear Curve", "content": "A mathematical Concept ..."}
        request = self.factory.post(url, data=data, format="json")
        force_authenticate(request, user=self.user)
        response = views.post_list(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("title"), data["title"])

    def test_create_post_without_authentication(self):
        """Test creating a post"""
        url = reverse("posts")
        data = {"title": "Linear Curve", "content": "A mathematical Concept ..."}
        request = self.factory.post(url, data=data, format="json")
        response = views.post_list(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            "Authentication credentials were not provided",
            str(response.data.get("detail")),
        )

    def test_get_published_posts_without_authentication(self):
        """Test getting posts"""
        url = reverse("posts")
        request = self.factory.get(url)
        response = views.post_list(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_published_posts_with_authentication(self):
        """Test getting posts with authentication"""
        url = reverse("posts")
        request = self.factory.get(url)
        force_authenticate(request, user=self.user)
        response = views.post_list(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_get_drafts(self):
        """Test getting draft post by unauthenticated user"""
        url = reverse("posts") + "?status=draft"
        request = self.factory.get(url)
        response = views.post_list(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            "Authentication credentials were not provided",
            str(response.data.get("detail")),
        )

    def test_authenticated_user_can_get_own_drafts(self):
        """Test getting own draft posts"""
        url = reverse("posts") + "?status=draft"
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user)
        response = views.post_list(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['results'][0]['is_published'])

    def test_unautheticated_user_get_draft(self):
        """Test attempt to get drafts"""
        url = reverse("posts") + "?status=draft"
        request = self.factory.get(url)
        response = views.post_list(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_get_others_drafts(self):
        """Test getting other's draft posts"""
        url = reverse("posts") + "?status=draft&author=CDE"
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user)
        response = views.post_list(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "You do not have permission to perform this action"
        )

    def test_auth_user_can_get_both_own_draft_and_published_posts(self):
        """Test get both drafts and published posts
        user1 has both True and False posts
        """
        url = reverse("posts") + "?status=all"
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user)
        response = views.post_list(request)
        result = [fields["is_published"] for fields in response.data["results"]]

        self.assertIn(True, result)
        self.assertIn(False, result)

    @parameterized.expand(
        [
            ("missing_status_param", None),
            ("empty_status_param", "published"),
            ("invalid_status_param", "invalid_val"),
            ("Published_val_status_param", "Published"),
            ("published_val_status_param", "published"),
        ]
    )
    def test_status_param_get_published_posts(self, test_name, input_data):
        """Test status param gets all published posts for all users"""
        base = reverse("posts")
        if input_data is None:
            url = base
        elif input_data == "":
            url = base + "?status="
        else:
            url = base + f"?status={input_data}"

        request = self.factory.get(url)
        response = views.post_list(request)

        result = [x["is_published"] for x in response.data["results"]]
        self.assertTrue(all(result))

    @parameterized.expand(
        [("Draft_val_status_param", "Draft"), ("draft_val_status_param", "draft")]
    )
    def test_status_param_get_draft_for_own_auth_user(self, test_name, input_data):
        """Test status param gets all draft posts for authenticated users"""
        base = reverse("posts")
        if input_data is None:
            url = base
        elif input_data == "":
            url = base + "?status="
        else:
            url = base + f"?status={input_data}"

        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user)
        response = views.post_list(request)
        result = [x["is_published"] for x in response.data["results"]]

        self.assertFalse(any(result))

    @parameterized.expand(
        [("Draft_val_status_param", "Draft"), ("draft_val_status_param", "draft")]
    )
    def test_status_param_cannot_get_draft_for_unauth_user(self, test_name, input_data):
        """Test status param gets all draft posts for authenticated users"""
        url = reverse("posts") + f"?status={input_data}"
        request = self.factory.get(url)
        response = views.post_list(request)

        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    @parameterized.expand(
        [
            # (test_name, input_data, expected_result)
            ("missing_author_param", None),
            ("empty_author_param", ""),
            ("me_val_author_param", "me"),
        ]
    )
    def test_author_param_for_drafts(self, test_name, input_data):
        """Test author's param for drafts"""
        base = reverse("posts") + "?status=draft"
        if not input_data:
            url = base
        else:
            url = base + f"&author={input_data}"

        request = self.factory.get(url)
        force_authenticate(user=self.user, request=request)
        response = views.post_list(request)
        result = [fields["is_published"] for fields in response.data["results"]]

        self.assertFalse(any(result))


class PostDetailViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user1 = User.objects.create_user(
            **{"full_name": "ABC", "email": "testing1@gmail.com", "password": "123"}
        )
        self.post1 = Post.objects.create(
            title="User 1 First Post",
            content="This is my first post",
            is_published=True,
            author=self.user1,
        )
        Post.objects.create(
            title="User 1 First Post",
            content="This is my first post",
            is_published=False,
            author=self.user1,
        )

        self.user2 = User.objects.create_user(
            **{"full_name": "CDE", "email": "testing2@gmail.com", "password": "123"}
        )
        self.post2 = Post.objects.create(
            title="User 2 First Post",
            content="This is my first post",
            is_published=False,
            author=self.user2,
        )
        Post.objects.create(
            title="The Lord of the Rings",
            content="A movie about 5 rings of Power",
            is_published=True,
            author=self.user2,
        )

        self.admin1 = User.objects.create_superuser(
            **{
                "full_name": "LMN",
                "email": "testingadmin1@gmail.com",
                "password": "123",
            }
        )
        Post.objects.create(
            title="Admin 1 First Post",
            content="This is my first post",
            author=self.admin1,
        )

        self.admin2 = User.objects.create_superuser(
            **{
                "full_name": "XYZ",
                "email": "testingadmin2@gmail.com",
                "password": "123",
            }
        )
        self.post4 = Post.objects.create(
            title="Admin 2 First Post",
            content="This is my first post",
            author=self.admin2,
            is_published=False,
        )

    def test_get_published_post_by_isbn_without_auth(self):
        """Test getting post by id without credentials"""
        url = reverse("post-detail", args=[self.post1.isbn])
        request = self.factory.get(url)
        response = views.post_detail(request, self.post1.isbn)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["isbn"], str(self.post1.isbn))

    def test_get_published_post_by_isbn_with_auth(self):
        """Test getting post by id with credentials"""
        url = reverse("post-detail", args=[self.post1.isbn])
        request = self.factory.get(url)
        response = views.post_detail(request, self.post1.isbn)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["isbn"], str(self.post1.isbn))

    def test_get_draft_without_auth(self):
        """Testing getting a draft without credentials"""
        url = reverse("post-detail", args=[self.post2.isbn])
        request = self.factory.get(url)
        response = views.post_detail(request, self.post2.isbn)

        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    def test_get_own_draft_with_auth(self):
        """Testing getting a draft with credentials"""
        url = reverse("post-detail", args=[self.post2.isbn])
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user2)
        response = views.post_detail(request, self.post2.isbn)

        self.assertFalse(response.data["is_published"])

    def test_get_others_draft_with_auth(self):
        """Testing getting other's draft with credentials"""
        url = reverse("post-detail", args=[self.post2.isbn])
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user1)
        response = views.post_detail(request, self.post2.isbn)

        self.assertEqual(
            response.data["detail"], "You do not have permission to perform this action"
        )

    def test_admin_can_get_user_draft(self):
        """Get users drafts"""
        url = reverse("posts") + "?status=draft"
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.admin1)
        response = views.post_detail(request, self.post2.isbn)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_published"])

    def test_updating_own_post_using_isbn_with_auth(self):
        """Test updating post by isbn with credentials"""
        data = {"is_published": True, "content": "This is the new content"}
        url = reverse("post-detail", args=[self.post2.isbn])

        request = self.factory.patch(url, data=data, format="json")
        force_authenticate(request=request, user=self.user2)
        response = views.post_detail(request, self.post2.isbn)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_published"], True)
        self.assertEqual(response.data["content"], "This is the new content")

    def test_updating_post_using_isbn_without_auth(self):
        """Test updating post by isbn without credentials"""
        data = {"is_published": True, "content": "This is the new content"}
        url = reverse("post-detail", args=[self.post2.isbn])

        request = self.factory.patch(url, data=data, format="json")
        response = views.post_detail(request, self.post2.isbn)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    def test_updating_others_post_using_isbn_with_auth(self):
        """Test updating other's post"""
        data = {"is_published": True, "content": "This is the new content"}
        url = reverse("post-detail", args=[self.post2.isbn])
        request = self.factory.patch(url, data=data, format="json")
        force_authenticate(request=request, user=self.user1)
        response = views.post_detail(request, self.post2.isbn)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "You do not have permission to perform this action"
        )

    def test_deleting_post_by_isbn_with_auth(self):
        """Test deleting post by isbn with credentials"""
        url = reverse("post-detail", args=[self.post2.isbn])
        request = self.factory.delete(url)
        force_authenticate(request=request, user=self.user2)
        response = views.post_detail(request, self.post2.isbn)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(isbn=self.post2.isbn).exists())

    def test_deleting_post_by_isbn_without_auth(self):
        """Test deleting post by isbn without credentials"""
        url = reverse("post-detail", kwargs={"post_id": self.post2.isbn})
        request = self.factory.delete(url)
        force_authenticate(request=request, user=self.user1)
        response = views.post_detail(request, self.post2.isbn)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "You do not have permission to perform this action"
        )

    def test_user_cannnot_delete_others_posts(self):
        """Test deleting post by isbn without credentials"""
        url = reverse("post-detail", kwargs={"post_id": self.post2.isbn})
        request = self.factory.delete(url)
        response = views.post_detail(request, self.post2.isbn)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided"
        )

    def test_admin_can_delete_users_posts(self):
        """Test admin can delete a user's post"""
        url = reverse("post-detail", args=[self.post1.isbn])
        request = self.factory.delete(url)
        force_authenticate(request=request, user=self.admin1)

        response = views.post_detail(request, self.post1.isbn)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(isbn=self.post1.isbn).exists())

    def test_admin_cannot_delete_staff_posts(self):
        """Test admin cannot delete other admin posts"""
        url = reverse("post-detail", args=[self.post4.isbn])
        request = self.factory.delete(url)
        force_authenticate(request=request, user=self.admin1)
        response = views.post_detail(request, self.post4.isbn)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "You do not have permission to perform this action"
        )
