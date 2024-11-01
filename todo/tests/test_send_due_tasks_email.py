from django.test import TestCase
from django.core import mail
from django.utils import timezone
from todo.models import User, List, ListItem
from todo.views import send_due_tasks_email

from django.utils import timezone

class SendDueTasksEmailTest(TestCase):
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='patilharshvardhan0508@gmail.com'  
        )        
        # Create a list using the correct field name
        now = timezone.now()
        self.list = List.objects.create(
            title_text="Test List",
            created_on=now,
            updated_on=now,
            list_tag="none",
            user_id=self.user,  
            is_shared=False
        )

        # Create a due task with created_on set
        self.due_task = ListItem.objects.create(
            list=self.list,
            item_name="Task 1",
            due_date=timezone.now().date(),
            created_on=now,  # Add created_on field
        )

    def test_send_due_email_content(self):
        send_due_tasks_email(self.user, [self.due_task])
        if len(mail.outbox) > 0:
            self.assertIn("Task 1", mail.outbox[0].body)
        else:
            self.fail("No email was sent.")

    def test_send_email_to_correct_recipient(self):
        send_due_tasks_email(self.user, [self.due_task])
        self.assertEqual(mail.outbox[0].to, [self.user.email])
    
    def test_send_email_subject(self):
        send_due_tasks_email(self.user, [self.due_task])
        self.assertEqual(mail.outbox[0].subject, "Tasks Due Notification")
    
    def test_send_email_with_no_tasks(self):
        send_due_tasks_email(self.user, [])
        self.assertIn("Here are your tasks that are due:", mail.outbox[0].body)
    
    # Additional cases
    # 5 test cases: including edge cases like missing email address,
    # multiple tasks, task without a due date, task due in the future