from django.test import TestCase

from api.models import Order, User

from django.urls import reverse

from rest_framework import status

# Create your tests here.
class UserOrderTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='pass1234')
        user2 = User.objects.create_user(username='user2', password='pass1234')
        Order.objects.create(user=user1)
        Order.objects.create(user=user1)
        Order.objects.create(user=user2)
        Order.objects.create(user=user2)


    def test_user_order_retrieves_only_authenticated_user_orders(self):
       user = User.objects.get(username='user1')
       self.client.force_login(user)
       response = self.client.get(reverse('user_order_list'))

       assert response.status_code == status.HTTP_200_OK
       data = response.json()
       self.assertTrue(all(order['user'] == user.id for order in data))

    def test_user_order_list_unauthenticated_access(self):
         response = self.client.get(reverse('user_order_list'))
         assert self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)