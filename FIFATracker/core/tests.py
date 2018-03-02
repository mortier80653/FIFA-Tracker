from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from .views import home, privacypolicy, about, contact, donate, upload_career_save_file

# Create your tests here.

class HomePageTests(TestCase):
    def test_homepage_view_status_code(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_homepage_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func, home)

class PrivacyPolicyTests(TestCase):
    def test_privaypolicy_view_status_code(self):
        url = reverse('privacypolicy')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_privaypolicy_url_resolves_home_view(self):
        view = resolve('/privacy-policy/')
        self.assertEquals(view.func, privacypolicy)

class AboutTests(TestCase):
    def test_about_view_status_code(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_about_url_resolves_home_view(self):
        view = resolve('/about/')
        self.assertEquals(view.func, about)

class ContactTests(TestCase):
    def test_contact_view_status_code(self):
        url = reverse('contact')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
    
    def test_contact_url_resolves_home_view(self):
        view = resolve('/contact/')
        self.assertEquals(view.func, contact)

class DonateTests(TestCase):
    def test_donate_view_status_code(self):
        url = reverse('donate')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
    
    def test_donate_url_resolves_home_view(self):
        view = resolve('/donate/')
        self.assertEquals(view.func, donate)

class UploadCareerSaveFileTests(TestCase):
    def setUp(self):
        # Create User
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

    def test_upload_career_save_file_not_authenticated_view_status_code(self):
        url = reverse('upload_career_save_file')
        response = self.client.get(url)
        # should redirect to home page
        self.assertEquals(response.status_code, 302)
        self.assertTrue( response.url == '/' )

    def test_upload_career_save_file_authenticated_view_status_code(self):
        login = self.client.login(username='testuser1', password='12345')

        url = reverse('upload_career_save_file')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    
    def test_upload_career_save_file_url_resolves_home_view(self):
        view = resolve('/upload/')
        self.assertEquals(view.func, upload_career_save_file)