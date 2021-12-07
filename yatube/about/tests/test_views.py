from django.test import Client, TestCase
from django.urls import reverse

AUTHOR_PAGE = reverse('about:author')
TECH_PAGE = reverse('about:tech')


class AboutPagesTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            AUTHOR_PAGE: 'about/author.html',
            TECH_PAGE: 'about/tech.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Проверьте правильность шаблона')
