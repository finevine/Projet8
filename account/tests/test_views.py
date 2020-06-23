from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from account import views, forms
from products.models import Product, Category, Favourite


#########################
#  TEST PROFILE
#########################
class TestProfile(TestCase):

    @classmethod  # <- setUpTestData must be a class method
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            'user1name',
            'user1@email.com',
            'user1password')

    def test_profile(self):
        ''' Access to profile '''
        # Connected user
        self.client.force_login(self.user1)
        # Access to his profile
        url = reverse('account:profile')
        response = self.client.get(url)

        # it is resolved to a function
        self.assertEqual(response.resolver_match.func, views.index)


    def test_unregistered(self):
        url = reverse('account:profile')
        response = self.client.get(url)

        # it is resolved to a function
        self.assertEqual(response.resolver_match.func, views.index)

        # And get redirected to the same origin page
        self.assertRedirects(
            response,
            '/account/login/?next=/account/profile/',
            fetch_redirect_response=False,
            status_code=302,
            target_status_code=200)


#########################
#     TEST SIGNUP
#########################
class TestSignup(TestCase):

    @classmethod  # <- setUpTestData must be a class method
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            'user1name',
            'user1@email.com',
            'GG56mm8=password')

    def test_signup_page_url(self):
        url = reverse('account:signup')
        response = self.client.get(url)
        self.assertEquals(url, '/account/signup/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='account/signup.html')

    def test_signup_form_already_exist(self):
        response = self.client.post(reverse('account:signup'), data={
            'username': self.user1.username,
            'email': self.user1.email,
            'password1': self.user1.password,
            'password2': self.user1.password
        })
        self.assertEquals(response.status_code, 200)

    def test_form(self):
        data={
            'username': 'user2name',
            'email': 'user2@mail.com',
            'password1': 'nPSDY@Mn$47v',
            'password2': 'nPSDY@Mn$47v'
        }
        form = forms.SignUpForm(data)
        # print(form.errors)
        self.assertTrue(form.is_valid())

    def test_signup_new(self):
        response = self.client.post(reverse('account:signup'), data={
            'username': 'user2name',
            'email': 'user2@mail.com',
            'password1': 'nPSDY@Mn$47v',
            'password2': 'nPSDY@Mn$47v'
        })
        self.assertRedirects(
            response,
            reverse('products:index'),
            status_code=302,
            target_status_code=200)


#########################
#    TEST LOGIN
#########################
class TestLogin(TestCase):

    @classmethod  # <- setUpTestData must be a class method
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            'user1name',
            'user1@email.com',
            'GG56mm8=password')

    def test_login_page_url(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEquals(url, '/account/login/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='registration/login.html')


#########################
#    TEST RESET PASS
#########################
class TestPasswordReset(TestCase):

    pass