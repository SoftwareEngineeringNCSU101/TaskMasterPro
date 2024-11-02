from django.urls import reverse
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from todo.views import login_request, template_from_todo, template, delete_todo, index, get_list_tags_by_userid, remove_list_item, add_new_list_item, update_list_item, create_new_todo_list, register_request, get_list_item_by_name, get_list_item_by_id, mark_list_item, todo_from_template
from django.utils import timezone
from todo.models import List, ListItem, Template, TemplateItem, ListTags, SharedList
from todo.forms import NewUserForm
from django.contrib.messages.storage.fallback import FallbackStorage

import json


class TestViews(TestCase):
    def setUp(self):
        # Every test needs access to the client and request factory.
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        
        self.client.login(username='jacob', password='top_secret')
        


    def testLogin(self):
        request = self.factory.get('/login/')
        request.user = self.user
        post = request.POST.copy()  # to make it mutable
        post['todo'] = 1
        print(request)
        request.POST = post
        response = login_request(request)
        self.assertEqual(response.status_code, 200)


    def test_delete_todo_list(self):
        request = self.factory.get('/todo/')
        request.user = self.user
        todo = List.objects.create(
            title_text="test list",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id_id=self.user.id,
        )
        ListItem.objects.create(
            item_name="test item",
            item_text="This is a test item on a test list",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now(),
            list=todo,
            is_done=False,
        )
        post = request.POST.copy()
        post['todo'] = 1
        request.POST = post
        response = delete_todo(request)
        self.assertEqual(response.status_code, 302)

    def test_getListTagsByUserid(self):
        request = self.factory.get('/todo/')
        request.user = self.user
        ListTags.objects.create(
            user_id_id = self.user.id,
            tag_name = 'test',
            created_on = timezone.now()
        )
        post = request.POST.copy()
        post['todo'] = 1
        request.POST = post
        request.method = "POST"
        response = get_list_tags_by_userid(request)
        print('response:')
        print(response)
        self.assertIsNotNone(response)

    def test_index(self):
        request = self.factory.get('/todo/')
        request.user = self.user
        response = index(request)
        self.assertEqual(response.status_code, 200)


    def test_template_from_todo_function(self):
        request = self.factory.get('/todo/')
        request.user = self.user
        todo = List.objects.create(
            title_text="test list",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id_id=request.user.id,
        )
        item = ListItem.objects.create(
            item_name="test item",
            item_text="This is a test item on a test list",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now(),
            list=todo,
            is_done=True,
        )
        post = request.POST.copy()  # to make it mutable
        post['todo'] = 1
        request.POST = post
        response = template_from_todo(request)
        self.assertEqual(response.status_code, 302)

    def test_template_display(self):
        request = self.factory.get('/todo/')
        request.user = self.user
        new_template = Template.objects.create(
            title_text="test template",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id_id=request.user.id
        )
        template_item = TemplateItem.objects.create(
            item_text="test item",
            created_on=timezone.now(),
            template=new_template,
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now()
        )
        post = request.POST.copy()  # to make it mutable
        post['todo'] = 1
        request.POST = post
        response = template(request, 1)
        self.assertEqual(response.status_code, 200)
        
    def test_removeListItem(self):
        request = self.factory.get('/todo/')
        request.user = self.user

        todo = List.objects.create(
        title_text="test list",
        created_on=timezone.now(),
        updated_on=timezone.now(),
        user_id_id=self.user.id,
        )

        ListItem.objects.create(
            item_name="test item",
            item_text="This is a test item on a test list",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now(),
            list=todo,
            is_done=False,
        )

        post = request.POST.copy()
        # post['list_item_id'] = 1
        request.method = "POST"
        request._body = json.dumps({ "list_item_id": 1 }).encode('utf-8')
        response = remove_list_item(request)
        print(response)
        self.assertIsNotNone(response)
        
        
    def test_NewUserForm(self):
        form_data = { 'email': '123@123.com', 'username': '123', 'password1': 'K!35EGL&g7#U', 'password2': 'K!35EGL&g7#U'}
        form = NewUserForm(form_data)
        self.assertTrue(form.is_valid())
        
    def test_addNewListItem(self):

        todo = List.objects.create(
        title_text="test list",
        created_on=timezone.now(),
        updated_on=timezone.now(),
        user_id_id=self.user.id,
        )

        params = { 
            'list_id': todo.id,
            'list_item_name': "random", 
            "create_on": 1670292391,
            "due_date": "2023-01-01",
            "tag_color": "#f9f9f9",
            "item_text": "",
            "is_done": False
            }

        request = self.factory.post(f'/todo/', data=params, 
                                content_type="application/json")
        request.user = self.user
        # request.method = "POST"
        print(type(params))
        # param = json.dumps(param,cls=DateTimeEncoder)
        # request._body = json.dumps(params, separators=(',', ':')).encode('utf-8')
        temp = add_new_list_item(request)
        response = index(request)
        self.assertEqual(response.status_code, 200)
        
        
    def test_createNewTodoList(self):
        test_data = {'list_name' : 'test',
                     'create_on' : 1670292391,
                     'list_tag' : 'test_tag',
                     'shared_user' : None,
                     'create_new_tag' : True}
        request = self.factory.post(f'/todo/', data=test_data, 
                                content_type="application/json")
        request.user = self.user
        temp = create_new_todo_list(request)
        response = index(request)
        self.assertEqual(response.status_code, 200)
        
    def test_getListItemByName(self):
        todo = List.objects.create(
            title_text="test list",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id_id=self.user.id,
        )
        ListItem.objects.create(
            item_name="test item",
            item_text="This is a test item on a test list",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now(),
            list=todo,
            is_done=False,
        )
        test_data = {'list_id' : '1',
                     'list_item_name' : "test item"
                     }
        request = self.factory.post(f'/todo/', data=test_data,
                                content_type="application/json")
        request.user = self.user
        response = get_list_item_by_name(request)
        self.assertEqual(response.status_code, 200)
    
    def test_getListItemById(self):
        todo = List.objects.create(
            title_text="test list 3",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id_id=self.user.id,
        )
        item = ListItem.objects.create(
            item_name="test item 3",
            item_text="This is a test item on a test list",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now(),
            list=todo,
            is_done=False,
        )
        test_data = {'list_id' : str(todo.id),
                     'list_item_name': 'test item 3',
                     'list_item_id': str(item.id)
                     }
        request = self.factory.post(f'/todo/', data=test_data, 
                                content_type="application/json")
        request.user = self.user
        temp = get_list_item_by_id(request)
        response = index(request)
        self.assertEqual(response.status_code, 200)
        
    def test_markListItem(self):
        todo = List.objects.create(
            title_text="test list",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id_id=self.user.id,
        )

        listItem = ListItem.objects.create(
            item_name="test item",
            item_text="This is a test item on a test list",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now(),
            list=todo,
            is_done=False,
        )

        params = { 
            'list_id': todo.id,
            'list_item_name': listItem.item_name, 
            "create_on": 1670292391,
            "due_date": "2023-01-01",
            "finish_on": 1670292392,
            "is_done": True,
            "list_item_id": listItem.id,
            }

        request = self.factory.post(f'/todo/', data=params, 
                                content_type="application/json")
        request.user = self.user
        temp = mark_list_item(request)
        response = index(request)
        self.assertEqual(response.status_code, 200)
    
    def test_createNewTodoList2(self):
        test_data = {'list_name' : 'test',
                     'create_on' : 1670292391,
                     'list_tag' : 'test_tag',
                     'shared_user' : 'someone',
                     'create_new_tag' : True}
        request = self.factory.post(f'/todo/', data=test_data, 
                                content_type="application/json")
        request.user = self.user
        temp = create_new_todo_list(request)
        response = index(request)
        self.assertEqual(response.status_code, 200)
    
    def test_createNewTodoList3(self):
        sharedUser = User.objects.create_user(
            username='share', email='share@…', password='top_secret')
        sharedList = SharedList.objects.create(
            user = sharedUser,
            shared_list_id = ""
        )
        
        test_data = {'list_name' : 'test',
                     'create_on' : 1670292391,
                     'list_tag' : 'test_tag',
                     'shared_user' : 'share',
                     'create_new_tag' : True}
        request = self.factory.post(f'/todo/', data=test_data, 
                                content_type="application/json")
        request.user = self.user
        temp = create_new_todo_list(request)
        response = index(request)
        self.assertEqual(response.status_code, 200)
        
    def test_todo_from_template(self):
        request = self.factory.get('/todo/')
        request.user = self.user
        new_template = Template.objects.create(
            title_text="test template",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id_id=request.user.id
        )
        template_item = TemplateItem.objects.create(
            item_text="test item",
            created_on=timezone.now(),
            template=new_template,
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now()
        )
        
        post = request.POST.copy()
        post['todo'] = 1
        post['template'] = new_template.id
        request.POST = post
        request.method = "POST"
        response = todo_from_template(request)
        self.assertEqual(response.status_code, 302)

    def test_login_request(self):
        test_data = {'username' : 'jacob',
                     'password' : 'top_secret'}
        request = self.factory.post(f'/login/', data=test_data, 
                                content_type="application/json")
        request.user = self.user
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        response = login_request(request)
        self.assertEqual(response.status_code, 200)

    def test_updateListItem_success(self):
        # Setup for a successful update
        todo = List.objects.create(
            title_text="test list",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id=self.user
        )
        item = ListItem.objects.create(
            item_name="test item",
            item_text="This is a test item on a test list",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now(),
            list=todo,
            is_done=False
        )
        updated_text = "Updated test item text"
        response = self.client.post(
            reverse('todo:updateListItem', args=[item.id]),
            data=json.dumps({'note': updated_text}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], True)
        self.assertEqual(response_data['message'], "Note updated successfully")
        item.refresh_from_db()
        self.assertEqual(item.item_text, updated_text)

    def test_updateListItem_missing_note(self):
        # Test missing note content
        todo = List.objects.create(
            title_text="test list",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id=self.user
        )
        item = ListItem.objects.create(
            item_name="test item",
            item_text="This is a test item on a test list",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now(),
            list=todo,
            is_done=False
        )
        response = self.client.post(
            reverse('todo:updateListItem', args=[item.id]),
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], "Note content is missing")

    def test_updateListItem_invalid_item_id(self):
        response = self.client.post(
            reverse('todo:updateListItem', args=[0]),
            data=json.dumps({'note': 'Updated text'}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], "Invalid item ID")

    def test_updateListItem_item_not_found(self):
        response = self.client.post(
            reverse('todo:updateListItem', args=[999]),
            data=json.dumps({'note': 'Updated text'}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], "Item not found")

    def test_updateListItem_invalid_json(self):
        todo = List.objects.create(
            title_text="test list",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id=self.user
        )
        item = ListItem.objects.create(
            item_name="test item",
            item_text="This is a test item on a test list",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now(),
            list=todo,
            is_done=False
        )
        response = self.client.post(
            reverse('todo:updateListItem', args=[item.id]),
            data="Invalid JSON",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], "Invalid JSON data")

    def test_updateListItem_invalid_request_method(self):
        todo = List.objects.create(
            title_text="test list",
            created_on=timezone.now(),
            updated_on=timezone.now(),
            user_id=self.user
        )
        item = ListItem.objects.create(
            item_name="test item",
            item_text="This is a test item on a test list",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            tag_color="#f9f9f9",
            due_date=timezone.now(),
            list=todo,
            is_done=False
        )
        response = self.client.get(reverse('todo:updateListItem', args=[item.id]))
        self.assertEqual(response.status_code, 405)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], "Invalid request method")
