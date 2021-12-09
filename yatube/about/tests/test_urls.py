from http import HTTPStatus

from django.test import Client, TestCase

AUTHOR_PAGE = '/about/author/'
TECH_PAGE = '/about/tech/'
OK = HTTPStatus.OK


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_public_pages(self):
        """Проверка общедоступных страниц для неавторизованного клиента."""
        excepted_status_codes = {
            AUTHOR_PAGE: OK,
            TECH_PAGE: OK
        }
        for adress, excepted_code in excepted_status_codes.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(
                    response.status_code,
                    excepted_code,
                    'Ответ сервера не соответствует ожидаемому')
