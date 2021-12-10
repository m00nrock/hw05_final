from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User

PAGINATOR_CONTEXT = 'page_obj'
TEST_GROUP_SLUG = 'test-slug'
TEST_GROUP_SLUG2 = 'test2'
TEST_USERNAME = 'TestUser'
INDEX_PAGE = reverse('posts:index')
CREATE_PAGE = reverse('posts:post_create')
GROUP_PAGE = reverse('posts:group_list', kwargs={'slug': TEST_GROUP_SLUG})
GROUP_PAGE2 = reverse('posts:group_list', kwargs={'slug': TEST_GROUP_SLUG2})
PROFILE_PAGE = reverse('posts:profile', kwargs={'username': TEST_USERNAME})
FOLLOWS_PAGE = reverse('posts:follow_index')
TEST_IMAGE = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.user2 = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='Тестовое имя группы',
            slug=TEST_GROUP_SLUG,
            description='Тестовое описание группы'
        )
        cls.group2 = Group.objects.create(
            title='Тест2',
            slug=TEST_GROUP_SLUG2,
            description='Тестовое2'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=TEST_IMAGE,
            content_type='image/gif'
        )
        Post.objects.bulk_create([
            Post(
                text='Тестовый текст поста с группой',
                author=cls.user,
                group=cls.group,
                image=cls.uploaded,
            ) for i in range(13)
        ])
        cls.post = Post.objects.last()
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
        self.authorized_client.force_login(PostsPagesTests.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(PostsPagesTests.user2)

    def test_pages_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            INDEX_PAGE: 'posts/index.html',
            GROUP_PAGE: 'posts/group_list.html',
            PROFILE_PAGE: 'posts/profile.html',
            PostsPagesTests.POST_PAGE: 'posts/post_detail.html',
            PostsPagesTests.POST_EDIT_PAGE: 'posts/create_post.html',
            CREATE_PAGE: 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Проверьте правильность шаблона')

    def test_index_correct_context(self):
        """
        Шаблон index сформирован с правильным контекстом.
        Paginator выводит 10 записей на страницу.
        """
        response = self.authorized_client.get(INDEX_PAGE)
        second_page = self.client.get(INDEX_PAGE + '?page=2')
        first_post = response.context[PAGINATOR_CONTEXT][0]
        last_post = response.context[PAGINATOR_CONTEXT][9]
        post_image = response.context.get(PAGINATOR_CONTEXT)[0].image
        self.assertEqual(first_post.text, 'Тестовый текст поста с группой')
        self.assertEqual(last_post.text, 'Тестовый текст поста с группой')
        self.assertEqual(first_post.author.username, self.user.username)
        self.assertEqual(len(
            response.context[PAGINATOR_CONTEXT]), 10, 'Ожидалось 10 постов')
        self.assertEqual(len(
            second_page.context[PAGINATOR_CONTEXT]), 3, 'Ожидалось 3 поста')
        self.assertIsNotNone(post_image)

    def test_group_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(GROUP_PAGE)
        second_page = self.guest_client.get(GROUP_PAGE + '?page=2')
        another_group_response = self.authorized_client.get(GROUP_PAGE2)
        post = response.context[PAGINATOR_CONTEXT][0]
        post_image = response.context.get(PAGINATOR_CONTEXT)[0].image
        self.assertIsNotNone(post_image)
        self.assertEqual(post.group.title, 'Тестовое имя группы')
        self.assertEqual(post.group.description, 'Тестовое описание группы')
        self.assertEqual(len(
            response.context[PAGINATOR_CONTEXT]), 10, 'Ожидалось 10 постов')
        self.assertEqual(len(
            second_page.context[PAGINATOR_CONTEXT]), 3, 'Ожидалось 3 поста')
        self.assertFalse(another_group_response.context.get(PAGINATOR_CONTEXT))

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_PAGE)
        second_page = self.authorized_client.get(PROFILE_PAGE + '?page=2')
        post_image = response.context.get(PAGINATOR_CONTEXT)[0].image
        self.assertIsNotNone(post_image)
        self.assertEqual(response.context.get('name').username, TEST_USERNAME)
        self.assertEqual(len(
            response.context[PAGINATOR_CONTEXT]), 10, 'Ожидалось 10 постов')
        self.assertEqual(len(
            second_page.context[PAGINATOR_CONTEXT]), 3, 'Ожидалось 3 поста')

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(PostsPagesTests.POST_PAGE)
        text = response.context.get('post').text
        post_author = response.context.get('post').author
        post_image = response.context.get('post').image
        self.assertIsNotNone(post_image)
        self.assertEqual(text, 'Тестовый текст поста с группой')
        self.assertEqual(post_author.username, 'TestUser')

    def test_post_edit_correct_context(self):
        """Шаблон post_edit/post_create сформирован с правильным контекстом."""
        response_edit = self.authorized_client.get(
            PostsPagesTests.POST_EDIT_PAGE)
        response_create = self.authorized_client.get(CREATE_PAGE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, excepted in form_fields.items():
            with self.subTest(value=value):
                form_field_edit = response_edit.context.get(
                    'form').fields.get(value)
                form_field_create = response_create.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field_edit, excepted)
                self.assertIsInstance(form_field_create, excepted)

    def test_follow_unfollow(self):
        """
        Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок.
        """
        self.authorized_client2.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': TEST_USERNAME}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=PostsPagesTests.user2,
                author=PostsPagesTests.user
            ).exists()
        )
        self.authorized_client2.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': TEST_USERNAME}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=PostsPagesTests.user2,
                author=PostsPagesTests.user
            ).exists()
        )

    def test_follow_new_post(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на него подписан.
        """
        self.authorized_client2.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': TEST_USERNAME}
            )
        )
        Post.objects.create(
            text='Test_text1',
            author=PostsPagesTests.user,
            group=PostsPagesTests.group,
        )
        response = self.authorized_client2.get(FOLLOWS_PAGE)
        post = response.context[PAGINATOR_CONTEXT][0]
        self.assertEqual(post.text, 'Test_text1')

    def test_unfollow_new_post(self):
        """
        Новая запись пользователя не появляется в ленте тех,
        кто на него не подписан.
        """
        Post.objects.create(
            text='Test_text2',
            author=PostsPagesTests.user,
            group=PostsPagesTests.group,
        )
        response = self.authorized_client2.get(FOLLOWS_PAGE)
        posts = response.context.get(PAGINATOR_CONTEXT)
        self.assertEqual(len(posts), 0)

    def test_no_img_new_post(self):
        """После загрузки неподдерживаемого файла, пост не создаётся."""
        txt = SimpleUploadedFile(
            name='text.txt',
            content=b'test_text',
            content_type='text/plain'
        )
        self.authorized_client.post(
            CREATE_PAGE,
            {'text': 'test', 'group': PostsPagesTests.group, 'image': txt})
        response = self.authorized_client.get(INDEX_PAGE)
        self.assertNotContains(response, self.authorized_client.post)


class CacheTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.group = Group.objects.create(
            title='Тестовое имя группы',
            slug=TEST_GROUP_SLUG,
            description='Тестовое описание группы'
        )
        Post.objects.create(
            text='Test_text1',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(CacheTest.user)

    def test_cache(self):
        """Проверка кеширования """
        response = self.client.get(INDEX_PAGE)
        Post.objects.last().delete()
        response2 = self.client.get(INDEX_PAGE)
        self.assertHTMLEqual(str(response.content), str(response2.content))
        cache.clear()
        response3 = self.client.get(INDEX_PAGE)
        self.assertHTMLNotEqual(str(response2.content), str(response3.content))
