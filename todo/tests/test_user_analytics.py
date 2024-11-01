from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from todo.models import List, ListItem
from django.urls import reverse
import datetime

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

    def test_list_association(self):
        # Check if the tasks are associated with the correct list
        self.assertEqual(self.task1.list, self.list)
        self.assertEqual(self.task2.list, self.list)
        self.assertEqual(self.task3.list, self.list)

    def test_user_analytics_view(self):
        response = self.client.get(reverse('todo:user_analytics'))  # Ensure 'user_analytics' is the correct URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/user_analytics.html')
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 2")
        self.assertContains(response, "Task 3")
        self.assertIn('due_soon_count', response.context)
        self.assertIn('overdue_count', response.context)
        self.assertIn('completed_count', response.context)
        self.assertIn('overdue_percentage', response.context)
        self.assertIn('avg_procrastination_hours', response.context)
        self.assertIn('busy_days', response.context)
        self.assertIn('today', response.context)

    def test_due_soon_items(self):
        response = self.client.get(reverse('todo:user_analytics'))
        due_soon_items = response.context['due_soon_items']
        self.assertEqual(len(due_soon_items), 1)  # Only task2 is due soon

    def test_average_procrastination_hours(self):
    # Create tasks with specific due dates and completion times
        ListItem.objects.all().delete()
        now = timezone.now()
        
        # Task completed 2 hours after due date
        # Set due_date to start of day and finished_on to 2 hours after start of day
        due_date1 = now.date()
        finished_on1 = timezone.make_aware(
            datetime.datetime.combine(due_date1, datetime.datetime.min.time())
        ) + timedelta(hours=2)
        
        late_task1 = ListItem.objects.create(
            list=self.list,
            item_name="Late Task 1",
            item_text="Completed 2 hours late",
            is_done=True,
            created_on=now - timedelta(days=1),
            due_date=due_date1,
            finished_on=finished_on1,
            tag_color="red"
        )
        
        # Task completed 4 hours after due date
        due_date2 = now.date()
        finished_on2 = timezone.make_aware(
            datetime.datetime.combine(due_date2, datetime.datetime.min.time())
        ) + timedelta(hours=4)
        
        late_task2 = ListItem.objects.create(
            list=self.list,
            item_name="Late Task 2",
            item_text="Completed 4 hours late",
            is_done=True,
            created_on=now - timedelta(days=1),
            due_date=due_date2,
            finished_on=finished_on2,
            tag_color="blue"
        )
        
        # Task completed before due date (should not affect average)
        on_time_task = ListItem.objects.create(
            list=self.list,
            item_name="On Time Task",
            item_text="Completed on time",
            is_done=True,
            created_on=now - timedelta(days=1),
            due_date=(now + timedelta(days=1)).date(),  # Due tomorrow
            finished_on=now,  # Finished now (before due date)
            tag_color="green"
        )
        
        # Get the analytics page
        response = self.client.get(reverse('todo:user_analytics'))
        
        # The average should be 3 hours ((2 + 4) / 2)
        self.assertAlmostEqual(
            response.context['avg_procrastination_hours'],
            3.0,
            places=1,
            msg="Average procrastination hours should be approximately 3.0"
        )
        
        # Test with only one late task
        late_task2.delete()
        response = self.client.get(reverse('todo:user_analytics'))
        
        # Now the average should be 2 hours
        self.assertAlmostEqual(
            response.context['avg_procrastination_hours'],
            2.0,
            places=1,
            msg="Average procrastination hours should be approximately 2.0 with single task"
        )
        
        # Test with no late tasks
        late_task1.delete()
        response = self.client.get(reverse('todo:user_analytics'))
        
        # Average should be 0 when there are no late tasks
        self.assertEqual(
            response.context['avg_procrastination_hours'],
            0.0,
            msg="Average procrastination hours should be 0.0 with no late tasks"
        )


    def test_busy_days(self):
        # Delete all tasks
        ListItem.objects.all().delete()

        # Create tasks with specific due dates to categorize days
        today = timezone.now().date()
        
        # Add tasks for different busy levels
        # Moderately Busy - 1 task
        ListItem.objects.create(
            list=self.list,
            item_name="Task A",
            item_text="Description for Task A",
            is_done=False,
            created_on=timezone.now(),
            due_date=today,
            tag_color="red"
        )

        # Busy - 3 tasks
        for i in range(3):
            ListItem.objects.create(
                list=self.list,
                item_name=f"Task B{i + 1}",
                item_text=f"Description for Task B{i + 1}",
                is_done=False,
                created_on=timezone.now(),
                due_date=today + timedelta(days=1),  # Due tomorrow
                tag_color="blue"
            )

        # Very Busy - 5 tasks
        for i in range(5):
            ListItem.objects.create(
                list=self.list,
                item_name=f"Task C{i + 1}",
                item_text=f"Description for Task C{i + 1}",
                is_done=False,
                created_on=timezone.now(),
                due_date=today + timedelta(days=2),  # Due in two days
                tag_color="green"
            )

        # Access user analytics page
        response = self.client.get(reverse('todo:user_analytics'))
        
        # Fetch busy_days from the context
        busy_days = response.context['busy_days']

        # Assert the categories for each due date
        self.assertEqual(busy_days.get(today), 'Moderately Busy', "Expected 'Moderately Busy' for today")
        self.assertEqual(busy_days.get(today + timedelta(days=1)), 'Busy', "Expected 'Busy' for tomorrow")
        self.assertEqual(busy_days.get(today + timedelta(days=2)), 'Very Busy', "Expected 'Very Busy' for the day after tomorrow")
