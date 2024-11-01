# from django.test import TestCase
# from django.utils import timezone
# from collections import defaultdict
# from todo.models import List, ListItem, User
# from todo.views import user_analytics
# from datetime import timedelta

# class UserAnalyticsTest(TestCase):
#     def setUp(self):
#         # Set up sample user and list items
#         self.user = User.objects.create(username="testuser", password="password")
#         self.list = List.objects.create(user_id=self.user)
        
#         # Create sample list items
#         self.task1 = ListItem.objects.create(list=self.list, item_name="Task 1", due_date=timezone.now().date(), is_done=False)
#         self.task2 = ListItem.objects.create(list=self.list, item_name="Task 2", due_date=timezone.now().date() + timedelta(days=1), is_done=False)
#         self.task3 = ListItem.objects.create(list=self.list, item_name="Task 3", due_date=timezone.now().date() - timedelta(days=1), is_done=True)
    
#     def test_total_tasks_count(self):
#         response = user_analytics(self.client.request)
#         self.assertEqual(response.context['total_tasks'], 3)
    
#     def test_overdue_tasks_count(self):
#         response = user_analytics(self.client.request)
#         self.assertEqual(response.context['overdue_count'], 1)
    
#     def test_due_soon_tasks_count(self):
#         response = user_analytics(self.client.request)
#         self.assertEqual(response.context['due_soon_count'], 1)
    
#     def test_overdue_percentage(self):
#         response = user_analytics(self.client.request)
#         self.assertEqual(response.context['overdue_percentage'], 33.33)

#     def test_procrastination_count(self):
#         response = user_analytics(self.client.request)
#         self.assertTrue('avg_procrastination_hours' in response.context)

#     # Add more tests based on various edge cases
#     # (e.g., no due date, all completed, tasks scheduled for next month)
    
#     # Additional test cases to reach 20 test cases for this function
#     # Include cases for busy days, different completion rates, different counts for daily, weekly, monthly completions.

from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User
from todo.models import List, ListItem
from datetime import timedelta
from django.urls import reverse

class UserAnalyticsTest(TestCase):
    def setUp(self):
        # Set up client and user for authentication
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        
        # Set up sample list with a 'created_on' field
        self.list = List.objects.create(user_id=self.user, created_on=timezone.now())
        
        # Create sample list items
        self.task1 = ListItem.objects.create(list=self.list, item_name="Task 1", due_date=timezone.now().date(), is_done=False)
        self.task2 = ListItem.objects.create(list=self.list, item_name="Task 2", due_date=timezone.now().date() + timedelta(days=1), is_done=False)
        self.task3 = ListItem.objects.create(list=self.list, item_name="Task 3", due_date=timezone.now().date() - timedelta(days=1), is_done=True)
    
    def test_total_tasks_count(self):
        response = self.client.get(reverse('user_analytics'))
        self.assertEqual(response.context['total_tasks'], 3)
    
    # def test_overdue_tasks_count(self):
    #     response = self.client.get(reverse('user_analytics'))
    #     self.assertEqual(response.context['overdue_count'], 1)
    
    # def test_due_soon_tasks_count(self):
    #     response = self.client.get(reverse('user_analytics'))
    #     self.assertEqual(response.context['due_soon_count'], 1)
    
    # def test_overdue_percentage(self):
    #     response = self.client.get(reverse('user_analytics'))
    #     self.assertEqual(response.context['overdue_percentage'], 33.33)

    # def test_procrastination_count(self):
    #     response = self.client.get(reverse('user_analytics'))
    #     self.assertTrue('avg_procrastination_hours' in response.context)

    # Add more tests for various edge cases as needed
