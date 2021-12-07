from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

TEST_GROUP_SLUG = 'test-slug'
TEST_USERNAME = 'TestUser'
CREATE_PAGE = reverse('posts:post_create')
PROFILE_PAGE = reverse('posts:profile', kwargs={'username': TEST_USERNAME})


class PostsFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.group = Group.objects.create(
            title='Тестовое имя группы',
            slug=TEST_GROUP_SLUG,
            description='Тестовое описание группы'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст редактируемого поста',
            group=cls.group,
        )
        cls.TEST_POST = Post.objects.last().id
        cls.POST_PAGE = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.TEST_POST})
        cls.POST_EDIT_PAGE = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.TEST_POST})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsFormTests.user)

    def test_post_create(self):
        """
        При отправке валидной формы создаётся пост и сохраняется запись в БД.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'А вот и новый контент',
            'image': PostsFormTests.uploaded,
        }
        response = self.authorized_client.post(
            CREATE_PAGE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PROFILE_PAGE)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(Post.objects.first().text, 'А вот и новый контент')
        self.assertIsNotNone(Post.objects.first().image)

    def test_post_edit(self):
        """
        При отправке валидной формы изменяется пост и запись в БД.
        """
        form_data = {
            'text': 'Теперь этот пост изменен'
        }
        response = self.authorized_client.post(
            PostsFormTests.POST_EDIT_PAGE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PostsFormTests.POST_PAGE)
        self.assertEqual(Post.objects.last().text, 'Теперь этот пост изменен')
