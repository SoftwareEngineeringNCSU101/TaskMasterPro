from django.urls import path
from . import views

app_name = "todo"


# Urls for to-done app
urlpatterns = [
    path('', views.index, name='index'),
    path('todo', views.index, name='todo'),
    path('todo/<int:list_id>', views.index, name='todo_list_id'),
    path('todo/new-from-template', views.todo_from_template, name='todo_from_template'),
    path('delete-todo', views.delete_todo, name='delete_todo'),
    path('templates', views.template, name='template'),
    path('templates/<int:template_id>', views.template, name='template'),
    path('templates/new-from-todo', views.template_from_todo, name='template_from_todo'),
    path('updateListItem', views.update_list_item, name='updateListItem'),
    path('removeListItem', views.remove_list_item, name='removeListItem'),
    path('createNewTodoList', views.create_new_todo_list, name='createNewTodoList'),
    path('getListItemByName', views.get_list_item_by_name, name='getListItemByName'),
    path('getListItemById', views.get_list_item_by_id, name='getListItemById'),
    path('markListItem', views.mark_list_item, name='markListItem'),
    path('addNewListItem', views.add_new_list_item, name='addNewListItem'),
    path('updateListItem/<int:item_id>', views.update_list_item, name='updateListItem'),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout"),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('user_analytics', views.user_analytics, name='user_analytics')
]
