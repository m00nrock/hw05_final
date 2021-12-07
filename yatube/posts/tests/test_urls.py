from django.test import Client, TestCase
from posts.models import Group, Post, User

TEST_GROUP_SLUG = 'test-slug'
TEST_USERNAME = 'TestUser'
INDEX_PAGE = '/'
CREATE_PAGE = '/create/'
GROUP_PAGE = f'/group/{TEST_GROUP_SLUG}/'
PROFILE_PAGE = f'/profile/{TEST_USERNAME}/'
PAGE_404 = '/blah-blah-blah/'


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.user2 = User.objects.create_user(username='NotAuthor')
        cls.group = Group.objects.create(
            title='Тестовое имя группы',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста'
        )
        cls.TEST_POST = cls.post.id
        cls.POST_PAGE = f'/posts/{cls.TEST_POST}/'
        cls.POST_EDIT_PAGE = f'/posts/{cls.TEST_POST}/edit/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_urls_templates(self):
        """Проверка соответствия шаблонов."""
        client = Client()
        template_url = {
            INDEX_PAGE: ('posts/index.html', 200),
            GROUP_PAGE: ('posts/group_list.html', 200),
            PROFILE_PAGE: ('posts/profile.html', 200),
            PostsURLTests.POST_PAGE: ('posts/post_detail.html', 200),
            PostsURLTests.POST_EDIT_PAGE: ('posts/create_post.html', 200),
            CREATE_PAGE: ('posts/create_post.html', 200),
            PAGE_404: ('core/404.html', 404),
        }

        for adress, excepted in template_url.items():
            with self.subTest(adress=adress):
                response_guest = client.get(adress)
                response_authorized = self.authorized_client.get(adress)
                template = excepted[0]
                excepted_code = excepted[1]
                if (adress == PostsURLTests.POST_PAGE
                   or adress == PostsURLTests.POST_EDIT_PAGE
                   or adress == CREATE_PAGE):
                    self.assertTemplateUsed(
                        response_authorized,
                        template,
                        'Ожидался другой шаблон')
                    self.assertEqual(
                        response_authorized.status_code,
                        excepted_code,
                        'Ответ сервера не соответствует ожидаемому')
                else:
                    self.assertTemplateUsed(
                        response_guest,
                        template,
                        'Ожидался другой шаблон')
                    self.assertEqual(
                        response_guest.status_code,
                        excepted_code,
                        'Ответ сервера не соответствует ожидаемому')

    def test_post_edit_non_author_redirect(self):
        """
        Проверка редиректа не автора поста на страницу /posts/<post_pk>/.
        """
        not_author_client = Client()
        not_author_client.force_login(PostsURLTests.user2)
        response = not_author_client.get(PostsURLTests.POST_EDIT_PAGE)
        excepted_link = PostsURLTests.POST_PAGE
        self.assertRedirects(response, excepted_link)

    def test_post_edit_anonymous_user(self):
        """Проверка редиректа анонимного пользователя на страницу логина."""
        excepted_redirect = {
            PostsURLTests.POST_EDIT_PAGE: '/auth/login/?next=/posts/1/edit/',
            CREATE_PAGE: '/auth/login/?next=/create/',
        }
        for adress, excepted in excepted_redirect.items():
            with self.subTest(adress=adress):
                response_guest = self.guest_client.get(adress)
                self.assertRedirects(
                    response_guest,
                    excepted)
