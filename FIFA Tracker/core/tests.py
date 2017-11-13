from django.test import TestCase
from django.core.urlresolvers import reverse
from django.urls import resolve
from .views import home

# Create your tests here.

class HomePageTests(TestCase):
    def test_homepage_view_status_code(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_homepage_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func, home)

