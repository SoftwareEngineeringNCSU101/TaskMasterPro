from django.test import SimpleTestCase
from django.urls import reverse, resolve
from todo.views import (
    index, todo_from_template, delete_todo, template, 
    template_from_todo, updateListItem, removeListItem,
    createNewTodoList, getListItemByName, getListItemById, 
    markListItem, addNewListItem, register_request, 
    login_request, logout_request, password_reset_request,
    user_analytics
)

class TestURLS(SimpleTestCase):
    def test_index_url(self):
        url = reverse('todo:index')
        self.assertEqual(resolve(url).func, index)

    def test_todo_url(self):
        url = reverse('todo:todo')
        self.assertEqual(resolve(url).func, index)

    def test_todo_list_id_url(self):
        url = reverse('todo:todo_list_id', args=[1])
        self.assertEqual(resolve(url).func, index)

    def test_todo_from_template_url(self):
        url = reverse('todo:todo_from_template')
        self.assertEqual(resolve(url).func, todo_from_template)

    def test_delete_todo_url(self):
        url = reverse('todo:delete_todo')
        self.assertEqual(resolve(url).func, delete_todo)

    def test_template_url(self):
        url = reverse('todo:template')
        self.assertEqual(resolve(url).func, template)

    def test_template_with_id_url(self):
        url = reverse('todo:template', args=[1])
        self.assertEqual(resolve(url).func, template)

    def test_template_from_todo_url(self):
        url = reverse('todo:template_from_todo')
        self.assertEqual(resolve(url).func, template_from_todo)

    def test_updateListItem_url(self):
        url = reverse('todo:updateListItem')
        self.assertEqual(resolve(url).func, updateListItem)

    def test_removeListItem_url(self):
        url = reverse('todo:removeListItem')
        self.assertEqual(resolve(url).func, removeListItem)

    def test_createNewTodoList_url(self):
        url = reverse('todo:createNewTodoList')
        self.assertEqual(resolve(url).func, createNewTodoList)

    def test_getListItemByName_url(self):
        url = reverse('todo:getListItemByName')
        self.assertEqual(resolve(url).func, getListItemByName)

    def test_getListItemById_url(self):
        url = reverse('todo:getListItemById')
        self.assertEqual(resolve(url).func, getListItemById)

    def test_markListItem_url(self):
        url = reverse('todo:markListItem')
        self.assertEqual(resolve(url).func, markListItem)

    def test_addNewListItem_url(self):
        url = reverse('todo:addNewListItem')
        self.assertEqual(resolve(url).func, addNewListItem)

    def test_updateListItem_with_id_url(self):
        url = reverse('todo:updateListItem', args=[1])
        self.assertEqual(resolve(url).func, updateListItem)

    def test_register_url(self):
        url = reverse('todo:register')
        self.assertEqual(resolve(url).func, register_request)

    def test_login_url(self):
        url = reverse('todo:login')
        self.assertEqual(resolve(url).func, login_request)

    def test_logout_url(self):
        url = reverse('todo:logout')
        self.assertEqual(resolve(url).func, logout_request)

    def test_password_reset_url(self):
        url = reverse('todo:password_reset')
        self.assertEqual(resolve(url).func, password_reset_request)

    def test_user_analytics_url(self):
        url = reverse('todo:user_analytics')
        self.assertEqual(resolve(url).func, user_analytics)
