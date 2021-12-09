from django.test import TestCase

from posts.models import Comment, Group, Post, User

from .test_views import TEST_GROUP_SLUG


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        excepted_text = PostModelTest.post
        self.assertEqual(str(excepted_text), 'Test post text')
        excepted_name = PostModelTest.group
        self.assertEqual(str(excepted_name), 'Test group title')
        excepted_comment = PostModelTest.comment
        self.assertEqual(str(excepted_comment), 'Test_comment')
