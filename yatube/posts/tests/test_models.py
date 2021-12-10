from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

TEST_GROUP_SLUG = 'test-slug'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.user2 = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Test group title',
            slug=TEST_GROUP_SLUG,
            description='Test description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post text'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Test_comment'
        )
        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        excepted_text = PostModelTest.post
        self.assertEqual(str(excepted_text), 'Test post text')
        excepted_name = PostModelTest.group
        self.assertEqual(str(excepted_name), 'Test group title')
        excepted_comment = PostModelTest.comment
        self.assertEqual(str(excepted_comment), 'Test_comment')
        excepted_follow = PostModelTest.follow
        self.assertEqual(
            str(excepted_follow),
            f'{PostModelTest.user2} подписан на {PostModelTest.user}'
        )
