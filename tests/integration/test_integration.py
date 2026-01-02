from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from app.comment.models import Comment
from app.like.models import Like
from app.post.models import Post


class BlogAPIIntegrationTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(
            full_name="ABC", email="abc@gmail.com", password="abc"
        )
        cls.user2 = get_user_model().objects.create_user(
            full_name="DEF", email="def@gmail.com", password="def"
        )
        cls.admin = get_user_model().objects.create_superuser(
            full_name="ADMIN",
            email="admin@gmail.com",
            password="admin",
            username="Paper",
        )
        cls.post = Post.objects.create(
            author=cls.user1,
            title="Introduction to Politics",
            content=(
                "Perhaps the greatest issue we are facing in world"
                "has everything to do with politics"
            ),
            is_published=True,
        )
        cls.draft = Post.objects.create(
            author=cls.user1,
            title="Introduction to Mathematics",
            content="The century of learning was as old as the start of life",
        )
        cls.comment = Comment.objects.create(
            author=cls.user2,
            content=(
                "I couldn't agree more to this. The number of gullible "
                "people in this country is beyond comprehension"
            ),
            post=cls.post,
        )
        cls.reply = Comment.objects.create(
            author=cls.user1,
            parent=cls.comment,
            post=cls.post,
            content=(
                "Of course. It's unfortunate that people's intelligence "
                "couldn't be tested before voting"
            ),
        )
        cls.like_post = Like.objects.create(
            user=cls.user2,
            content_type=ContentType.objects.get_for_model(Post),
            object_id=cls.post.id,
        )
        cls.like_comment = Like.objects.create(
            user=cls.user1,
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=cls.comment.id,
        )

    def setUp(self):
        self.client = APIClient()

    # --- Users / Auth ---
    def test_register_user_success(self):
        """POST register -> 201."""
        url = reverse("sign-up")
        data = {
            "full_name": "example",
            "email": "example@gmail.com",
            "password": "example",
        }

        response = self.client.post(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertSetEqual(set(response.data.keys()), {"full_name", "email"})

    def test_register_user_invalid_email_returns_400(self):
        """Representative invalid-case: invalid email -> 400."""
        url = reverse("sign-up")
        data = {"full_name": "example", "email": "invalidemailaddress"}

        response = self.client.post(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invalid email address", response.data["email"][0])

    def test_login_with_valid_credentials_returns_token(self):
        """POST login -> 200 + token."""
        url = reverse("login")
        data = {"email": "abc@gmail.com", "password": "abc"}

        response = self.client.post(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual(set(response.data.keys()), {"access", "user_id", "email"})

    def test_login_with_invalid_credentials_returns_401(self):
        """Wrong creds -> 401"""
        url = reverse("login")
        data = {"email": "invalid@gmail.com", "password": "invalid"}

        response = self.client.post(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid email or password")

    def test_get_own_profile_requires_auth_and_returns_profile(self):
        """GET own profile -> 200 when auth; 401 otherwise (if applicable)."""
        # anonymous user -> 401
        url = reverse("user-profile", args=[self.user1.id])

        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # authenticated user -> 200
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": str(self.user1.id),
                "full_name": self.user1.full_name,
                "email": self.user1.email,
            },
        )

    # def test_update_own_profile_succeeds(self):
    #     """PATCH/PUT profile -> 200"""
    #     url = reverse('user-profile', args=[self.user2.id])
    #     self.client.force_authenticate(user=self.user1)
    #     data = {}
    #     response = self.

    def test_admin_can_disable_user_account(self):
        """
        Admin disables user -> user.is_active False (or flag), and effect observed.
        """
        # Anonymous user -> Unauthorized
        url = reverse("disable-account", args=[self.user2.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Regular authenticated user -> forbidden
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin -> success
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("account disabled", response.data["message"])

    def test_disabled_user_cannot_authenticate(self):
        """Disabled user cannot log in / obtain token."""
        # First disable account using admin
        url = reverse("disable-account", args=[self.user2.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try logging in
        url = reverse("login")
        self.client.force_authenticate(user=self.user2)
        data = {"email": "def@gmail.com", "password": "def"}
        response = self.client.post(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual("Invalid email or password", response.data["detail"])

    # --- Posts ---
    def test_create_post_with_auth_returns_201(self):
        """POST create -> 201"""
        url = reverse("posts")
        data = {
            "title": "An introduction Post",
            "content": "This is the first Introduction to Quantum Mechanics",
        }
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])
        self.assertEqual(response.data["content"], data["content"])

    def test_create_post_without_auth_returns_401(self):
        """POST create wihout Auth -> 401"""
        url = reverse("posts")
        data = {
            "title": "An introduction Post",
            "content": "This is the first Introduction to Quantum Mechanics",
        }
        response = self.client.post(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_posts_public_returns_200(self):
        """GET posts -> 200"""
        # Anonymous user -> 200
        url = reverse("posts")
        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Authenticated user -> 200
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_post_public_view(self):
        # Anonymous user -> 200
        url = reverse("post-detail", args=[self.post.id])
        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Authenticated user -> 200
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pass

    def test_update_own_post_with_auth_succeeds(self):
        """PATCH post -> 200"""
        # Authenticated user -> 200
        url = reverse("post-detail", args=[self.post.id])
        self.client.force_authenticate(user=self.user1)
        data = {"title": "This is a new Title"}
        response = self.client.patch(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], data["title"])

        data = {"content": "This is a new content"}
        response = self.client.patch(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], data["content"])

        data = {"content": "This is a new content", "title": "This is the new title"}
        response = self.client.patch(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], data["title"])
        self.assertEqual(response.data["content"], data["content"])

    def test_update_other_users_post_with_auth_returns_403(self):
        """PATCH others post -> 403"""
        # Anonymous user -> 401
        url = reverse("post-detail", args=[self.post.id])
        data = {"title": "This is a new Title"}
        response = self.client.patch(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Regular authenticated user -> 403
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = {"content": "This is a new content"}
        response = self.client.patch(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_post_with_auth_succeeds(self):
        """DELETE own post -> 204"""
        # anonymous user -> 201
        url = reverse("post-detail", args=[self.post.id])
        response = self.client.delete(path=url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # authenticated user -> 204
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(path=url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_users_post_with_auth_returns_403(self):
        """DELETE others post -> 403"""
        url = reverse("post-detail", args=[self.post.id])
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(path=url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "You do not have permission to perform this action", response.data["detail"]
        )

    def test_get_user_posts_returns_only_user_posts(self):
        """GET posts -> 200"""
        # anonymous users
        url = reverse("posts", query={"author": "me"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # authenticated users
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_drafts_only_for_owner_or_admin(self):
        """GET Drafts -> 200/401/403"""
        # anonymous user
        url = reverse("posts", query={"status": "draft", "author": "me"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            "Authentication credentials were not provided", response.data["detail"]
        )

        # other authenticated user
        url = reverse("posts", query={"status": "draft", "author": "ABC"})
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "You do not have permission to perform this action", response.data["detail"]
        )

        # authenticated owner
        url = reverse("posts", query={"status": "draft", "author": "me"})
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_popular_posts_ordered_by_likes(self):
        """GET popular posts -> 200"""
        # anonymous user
        url = reverse("popular")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # authenticated user
        url = reverse("popular")
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_posts_includes_comment_count_like_and_preview(self):
        """GET posts -> 200"""
        # anonymous user
        url = reverse("posts")
        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual(
            set(response.data["results"][0].keys()),
            {
                "id",
                "title",
                "excerpt",
                "author",
                "likes",
                "comment_count",
                "is_published",
                "created_at",
            },
        )

    # --- Comments & Replies ---
    def test_comment_on_post_with_auth_creates_comment(self):
        """POST comment -> 201/401"""
        # anonymous user -> 401
        data = {"content": "I love your write-ups. Nice"}
        url = reverse("comments", args=[self.post.id])
        response = self.client.post(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            "Authentication credentials were not provided", response.data["detail"]
        )

        # authenticated user -> 201
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data["content"])

    def test_get_post_comments_includes_comment_count_and_preview(self):
        """GET post_comments -> 200"""
        url = reverse("comments", args=[self.post.id])
        # anonymous user
        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            (response.data["results"][0].keys()),
            {"id", "author", "post", "excerpt", "reply_count", "likes", "created_at"},
        )

        # authenticated user
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            (response.data["results"][0].keys()),
            {"id", "author", "post", "excerpt", "reply_count", "likes", "created_at"},
        )

    def test_update_own_comment_succeeds(self):
        """PATCH comment -> 200/401"""
        url = reverse("comment-detail", args=[self.comment.id])
        data = {"content": "this is an edited commet"}

        # anonymous user
        response = self.client.patch(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            "Authentication credentials were not provided", response.data["detail"]
        )

        # authenticated user
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], data["content"])

    def test_update_other_users_comment_returns_403(self):
        """PATCH comment -> 403"""
        # authenticated user
        url = reverse("comment-detail", args=[self.comment.id])
        data = {"content": "this is an edited commet"}
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(path=url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_comment_detail_includes_full_content_and_top_replies(self):
        """GET specific comment -> 200"""
        url = reverse("comment-detail", args=[self.comment.id])

        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual(
            set(response.data.keys()),
            {
                "id",
                "author",
                "post",
                "content",
                "top_replies",
                "reply_count",
                "likes",
                "created_at",
            },
        )
        self.assertEqual(response.data["content"], self.comment.content)

    def test_get_comment_replies_returns_top_three_and_reply_count(self):
        """GET comment replies -> 200"""
        Comment.objects.create(
            parent=self.comment, content="reply 1", author=self.user2, post=self.post
        )
        Comment.objects.create(
            parent=self.comment, content="reply 2", author=self.user1, post=self.post
        )
        Comment.objects.create(
            parent=self.comment, content="reply 3", author=self.user1, post=self.post
        )

        url = reverse("comment-detail", args=[self.comment.id])
        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["top_replies"]), 3)
        self.assertEqual(response.data["reply_count"], 4)
        self.assertEqual(response.data["likes"], 1)

    def test_get_replies_returns_excerpt_and_likes(self):
        """GET comment replies -> 200"""
        url = reverse("replies", args=[self.comment.id])
        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data["results"], list))

    # --- Likes ---
    def test_like_post_with_auth_creates_like(self):
        """POST like-post: 201"""
        url = reverse("like-post", args=[self.post.id])
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.count(), 2)

    def test_like_post_without_auth_returns_401(self):
        """POST like-post: 401"""
        # anonymous user
        url = reverse("like-post", args=[self.post.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.count(), 1)

    def test_like_comment_with_auth_creates_like(self):
        """POST like-comment: 201"""
        url = reverse("like-comment", args=[self.comment.id])
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likes.count(), 2)

    def test_like_reply_with_auth_creates_like(self):
        """POST like-reply: 201"""
        url = reverse("like-comment", args=[self.comment.id])
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likes.count(), 2)

    def test_like_idempotency_or_toggle_behavior(self):
        """Like Post/Comment multiple times -> 400"""
        # --- for Post ----
        url = reverse("like-post", args=[self.post.id])
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Post already liked")

        # --- for Comment ---
        url = reverse("like-comment", args=[self.comment.id])
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Comment already liked")

    # --- Cross-cutting / misc ---
    def test_pagination_and_filters_on_post_list(self):
        """Test filtes and Pagination -> 200"""
        url = reverse("posts", query={"status": "draft", "author": "me"})
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["results"][0]["is_published"])
        self.assertIn("count", response.data.keys())

    # def test_permissions_for_sensitive_endpoints(self):
    #     pass

    # def test_prefetch_select_related_avoid_n_plus_one(self):
    #     """Optional: assert query count if you want to detect N+1 regressions."""
    #     pass
