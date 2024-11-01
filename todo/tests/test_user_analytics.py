# from django.test import TestCase
# from django.utils import timezone
# from datetime import timedelta
# from django.contrib.auth.models import User
# from todo.models import List, ListItem

# class UserAnalyticsTest(TestCase):
#     def setUp(self):
#         # Create a sample list with the current time for created and updated fields
#         now = timezone.now()
#         self.list = List.objects.create(
#             title_text="Test List",
#             created_on=now,
#             updated_on=now,
#             list_tag="none",
#             user_id=None,  # Adjust this if needed
#             is_shared=False
#         )

#         # Create sample list items with different states
#         self.task1 = ListItem.objects.create(
#             list=self.list,
#             item_name="Task 1",
#             item_text="Description for Task 1",
#             is_done=False,
#             created_on=now,
#             finished_on=None,
#             due_date=timezone.now().date(),
#             tag_color="red"
#         )
#         self.task2 = ListItem.objects.create(
#             list=self.list,
#             item_name="Task 2",
#             item_text="Description for Task 2",
#             is_done=False,
#             created_on=now,
#             finished_on=None,
#             due_date=timezone.now().date() + timedelta(days=1),
#             tag_color="blue"
#         )
#         self.task3 = ListItem.objects.create(
#             list=self.list,
#             item_name="Task 3",
#             item_text="Description for Task 3",
#             is_done=True,
#             created_on=now,
#             finished_on=now,
#             due_date=timezone.now().date() - timedelta(days=1),
#             tag_color="green"
#         )

#     def test_total_tasks_count(self):
#         total_tasks = ListItem.objects.count()
#         self.assertEqual(total_tasks, 3)

#     def test_completed_tasks_count(self):
#         completed_tasks = ListItem.objects.filter(is_done=True).count()
#         self.assertEqual(completed_tasks, 1)

#     def test_incomplete_tasks_count(self):
#         incomplete_tasks = ListItem.objects.filter(is_done=False).count()
#         self.assertEqual(incomplete_tasks, 2)

#     def test_tasks_due_today(self):
#         today_due_tasks = ListItem.objects.filter(due_date=timezone.now().date()).count()
#         self.assertEqual(today_due_tasks, 1)  # Only task1 should be due today

#     def test_tasks_due_overdue(self):
#         overdue_tasks = ListItem.objects.filter(due_date__lt=timezone.now().date()).count()
#         self.assertEqual(overdue_tasks, 1)  # Only task3 should be overdue

#     def test_task_creation(self):
#         # Verify that a new task can be created
#         new_task = ListItem.objects.create(
#             list=self.list,
#             item_name="Task 4",
#             item_text="Description for Task 4",
#             is_done=False,
#             created_on=timezone.now(),
#             finished_on=None,
#             due_date=timezone.now().date() + timedelta(days=2),
#             tag_color="yellow"
#         )
#         self.assertIsNotNone(new_task.id)
#         self.assertEqual(ListItem.objects.count(), 4)

#     def test_task_deletion(self):
#         # Verify that a task can be deleted
#         self.task1.delete()
#         self.assertEqual(ListItem.objects.count(), 2)

#     def test_list_association(self):
#         # Check if the tasks are associated with the correct list
#         self.assertEqual(self.task1.list, self.list)
#         self.assertEqual(self.task2.list, self.list)
#         self.assertEqual(self.task3.list, self.list)

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from todo.models import List, ListItem
from django.urls import reverse

class UserAnalyticsTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='patilharshvardhan0508@gmail.com'
        )

        # Log the user in
        self.client.login(username='testuser', password='testpassword')

        # Create a sample list with the current time for created and updated fields
        now = timezone.now()
        self.list = List.objects.create(
            title_text="Test List",
            created_on=now,
            updated_on=now,
            list_tag="none",
            user_id=self.user,  # Associate list with the user
            is_shared=False
        )

        # Create sample list items with different states
        self.task1 = ListItem.objects.create(
            list=self.list,
            item_name="Task 1",
            item_text="Description for Task 1",
            is_done=False,
            created_on=now,
            finished_on=None,
            due_date=timezone.now().date(),
            tag_color="red"
        )
        self.task2 = ListItem.objects.create(
            list=self.list,
            item_name="Task 2",
            item_text="Description for Task 2",
            is_done=False,
            created_on=now,
            finished_on=None,
            due_date=timezone.now().date() + timedelta(days=1),
            tag_color="blue"
        )
        self.task3 = ListItem.objects.create(
            list=self.list,
            item_name="Task 3",
            item_text="Description for Task 3",
            is_done=True,
            created_on=now,
            finished_on=now,
            due_date=timezone.now().date() - timedelta(days=1),
            tag_color="green"
        )

    def test_total_tasks_count(self):
        total_tasks = ListItem.objects.count()
        self.assertEqual(total_tasks, 3)

    def test_completed_tasks_count(self):
        completed_tasks = ListItem.objects.filter(is_done=True).count()
        self.assertEqual(completed_tasks, 1)

    def test_incomplete_tasks_count(self):
        incomplete_tasks = ListItem.objects.filter(is_done=False).count()
        self.assertEqual(incomplete_tasks, 2)

    def test_tasks_due_today(self):
        today_due_tasks = ListItem.objects.filter(due_date=timezone.now().date()).count()
        self.assertEqual(today_due_tasks, 1)  # Only task1 should be due today

    def test_tasks_due_overdue(self):
        overdue_tasks = ListItem.objects.filter(due_date__lt=timezone.now().date()).count()
        self.assertEqual(overdue_tasks, 1)  # Only task3 should be overdue

    def test_task_creation(self):
        # Verify that a new task can be created
        new_task = ListItem.objects.create(
            list=self.list,
            item_name="Task 4",
            item_text="Description for Task 4",
            is_done=False,
            created_on=timezone.now(),
            finished_on=None,
            due_date=timezone.now().date() + timedelta(days=2),
            tag_color="yellow"
        )
        self.assertIsNotNone(new_task.id)
        self.assertEqual(ListItem.objects.count(), 4)

    def test_task_deletion(self):
        # Verify that a task can be deleted
        self.task1.delete()
        self.assertEqual(ListItem.objects.count(), 2)
