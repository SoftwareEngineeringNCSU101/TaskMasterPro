import datetime
import json

from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError
from django.utils import timezone

from todo.models import List, ListItem, Template, TemplateItem, ListTags, SharedUsers, SharedList

from todo.forms import NewUserForm
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.utils.safestring import mark_safe


# Render the home page with users' to-do lists
def index(request, list_id=0):
    if not request.user.is_authenticated:
        return redirect("/login")
    
    shared_list = []

    if list_id != 0:
        # latest_lists = List.objects.filter(id=list_id, user_id_id=request.user.id)
        latest_lists = List.objects.filter(id=list_id)

    else:
        latest_lists = List.objects.filter(user_id_id=request.user.id).order_by('-updated_on')

        try:
            query_list_str = SharedList.objects.get(user_id=request.user.id).shared_list_id
        except SharedList.DoesNotExist:
            query_list_str = None
        
        if query_list_str != None:
            shared_list_id = query_list_str.split(" ")
            shared_list_id.remove("")

            latest_lists = list(latest_lists)

            for list_id in shared_list_id:
            
                try:
                    query_list = List.objects.get(id=int(list_id))
                except List.DoesNotExist:
                    query_list = None

                if query_list:
                    shared_list.append(query_list)
        
    latest_list_items = ListItem.objects.order_by('list_id')
    saved_templates = Template.objects.filter(user_id_id=request.user.id).order_by('created_on')
    list_tags = ListTags.objects.filter(user_id=request.user.id).order_by('created_on')
    
    # change color when is or over due
    cur_date = datetime.date.today()
    for list_item in latest_list_items:       
        list_item.color = "#FF0000" if cur_date > list_item.due_date else "#000000"
    
    # Filter ListItems by lists belonging to the logged-in user
    user = request.user
    user_lists = List.objects.filter(user_id=user)
    user_list_items = ListItem.objects.filter(list__in=user_lists)

    # Calendar events based on user's tasks with a due date
    calendar_events = [
        {
            "title": item.item_name,
            "start": item.due_date.strftime('%Y-%m-%d'),
            "end": item.due_date.strftime('%Y-%m-%d')  # Optional end date
        }
        for item in user_list_items if item.due_date
    ]
            
    context = {
        'latest_lists': latest_lists,
        'latest_list_items': latest_list_items,
        'templates': saved_templates,
        'list_tags': list_tags,
        'shared_list': shared_list,
        'calendar_events': mark_safe(json.dumps(calendar_events))
    }
    return render(request, 'todo/index.html', context)

# Create a new to-do list from templates and redirect to the to-do list homepage
def todo_from_template(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    template_id = request.POST['template']
    fetched_template = get_object_or_404(Template, pk=template_id)
    todo = List.objects.create(
        title_text=fetched_template.title_text,
        created_on=timezone.now(),
        updated_on=timezone.now(),
        user_id_id=request.user.id
    )
    for template_item in fetched_template.templateitem_set.all():
        ListItem.objects.create(
            item_name=template_item.item_text,
            item_text="",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            due_date=timezone.now(),
            tag_color=template_item.tag_color,
            list=todo,
            is_done=False,
        )
    return redirect("/todo")


# Create a new Template from existing to-do list and redirect to the templates list page
def template_from_todo(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    todo_id = request.POST['todo']
    fetched_todo = get_object_or_404(List, pk=todo_id)
    new_template = Template.objects.create(
        title_text=fetched_todo.title_text,
        created_on=timezone.now(),
        updated_on=timezone.now(),
        user_id_id=request.user.id
    )
    for todo_item in fetched_todo.listitem_set.all():
        TemplateItem.objects.create(
            item_text=todo_item.item_name,
            created_on=timezone.now(),
            finished_on=timezone.now(),
            due_date=timezone.now(),
            tag_color = todo_item.tag_color,
            template=new_template
        )
    return redirect("/templates")


# Delete a to-do list
def delete_todo(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    todo_id = request.POST['todo']
    fetched_todo = get_object_or_404(List, pk=todo_id)
    fetched_todo.delete()
    return redirect("/todo")


# Render the template list page
def template(request, template_id=0):
    if not request.user.is_authenticated:
        return redirect("/login")
    if template_id != 0:
        saved_templates = Template.objects.filter(id=template_id)
    else:
        saved_templates = Template.objects.filter(user_id_id=request.user.id).order_by('created_on')
    context = {
        'templates': saved_templates
    }
    return render(request, 'todo/template.html', context)


# Remove a to-do list item, called by javascript function
@csrf_exempt
def removeListItem(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_item_id = body['list_item_id']
        print("list_item_id: ", list_item_id)
        try:
            with transaction.atomic():
                being_removed_item = ListItem.objects.get(id=list_item_id)
                being_removed_item.delete()
        except IntegrityError as e:
            print(str(e))
            print("unknown error occurs when trying to update todo list item text")
        return redirect("/todo")
    else:
        return redirect("/todo")

# Update a to-do list item, called by javascript function
@csrf_exempt
def updateListItem(request, item_id):
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            updated_text = data.get('note')

            if not updated_text:
                return JsonResponse({"success": False, "message": "Note content is missing"}, status=400)

            if item_id <= 0:
                return JsonResponse({"success": False, "message": "Invalid item ID"}, status=400)

            # Update the item in the database within a transaction
            with transaction.atomic():
                todo_list_item = ListItem.objects.get(id=item_id)
                todo_list_item.item_text = updated_text
                todo_list_item.save(force_update=True)

            # Return a JSON response indicating success
            return JsonResponse({"success": True, "message": "Note updated successfully"})

        except ListItem.DoesNotExist:
            return JsonResponse({"success": False, "message": "Item not found"}, status=404)
        except IntegrityError as e:
            print(str(e))
            return JsonResponse({"success": False, "message": "Database error occurred"}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


# Add a new to-do list item, called by javascript function
@csrf_exempt
def addNewListItem(request):
    print('DEBUG')
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_id = body['list_id']
        item_name = body['list_item_name']
        create_on = body['create_on']
        create_on_time = datetime.datetime.fromtimestamp(create_on)
        finished_on_time = datetime.datetime.fromtimestamp(create_on)
        due_date = body['due_date']
        tag_color = body['tag_color']
        print(item_name)
        print(create_on)
        result_item_id = -1
        # create a new to-do list object and save it to the database
        try:
            with transaction.atomic():
                todo_list_item = ListItem(item_name=item_name, created_on=create_on_time, finished_on=finished_on_time, due_date=due_date, tag_color=tag_color, list_id=list_id, item_text="", is_done=False)
                todo_list_item.save()
                result_item_id = todo_list_item.id
        except IntegrityError:
            print("unknown error occurs when trying to create and save a new todo list")
            return JsonResponse({'item_id': -1})
        return JsonResponse({'item_id': result_item_id})  # Sending an success response
    else:
        return JsonResponse({'item_id': -1})


# Mark a to-do list item as done/not done, called by javascript function
@csrf_exempt
def markListItem(request):
    """
    Mark a list item as done or undo it
    """
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_id = body['list_id']
        list_item_name = body['list_item_name']
        list_item_id = body['list_item_id']
        # remove the first " and last "
        list_item_is_done = True
        is_done_str = str(body['is_done'])
        finish_on = body['finish_on']
        finished_on_time = datetime.datetime.fromtimestamp(finish_on)
        print("is_done: " + str(body['is_done']))
        if is_done_str == "0" or is_done_str == "False" or is_done_str == "false":
            list_item_is_done = False
        try:
            with transaction.atomic():
                query_list = List.objects.get(id=list_id)
                query_item = ListItem.objects.get(id=list_item_id)
                query_item.is_done = list_item_is_done
                query_item.finished_on = finished_on_time
                query_item.save()
                # Sending an success response
                return JsonResponse({'item_name': query_item.item_name, 'list_name': query_list.title_text, 'item_text': query_item.item_text})
        except IntegrityError:
            print("query list item" + str(list_item_name) + " failed!")
            JsonResponse({})
        return HttpResponse("Success!")  # Sending an success response
    else:
        return HttpResponse("Request method is not a Post")

# Get all the list tags by user id
@csrf_exempt
def getListTagsByUserid(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        try:
            with transaction.atomic():
                user_id = request.user.id
                list_tag_list = ListTags.objects.filter(user_id=user_id).values()
                return JsonResponse({'list_tag_list': list(list_tag_list)})
        except IntegrityError:
            print("query list tag by user_id = " + str(user_id) + " failed!")
            JsonResponse({})
    else:
        return JsonResponse({'result': 'get'})  # Sending an success response

# Get a to-do list item by name, called by javascript function
@csrf_exempt
def getListItemByName(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_id = body['list_id']
        list_item_name = body['list_item_name']
        # remove the first " and last "
        # list_item_name = list_item_name

        print("list_id: " + list_id)
        print("list_item_name: " + list_item_name)
        try:
            with transaction.atomic():
                query_list = List.objects.get(id=list_id)
                query_item = ListItem.objects.get(list_id=list_id, item_name=list_item_name)
                # Sending an success response
                return JsonResponse({'item_id': query_item.id, 'item_name': query_item.item_name, 'list_name': query_list.title_text, 'item_text': query_item.item_text})
        except IntegrityError:
            print("query list item" + str(list_item_name) + " failed!")
            JsonResponse({})
    else:
        return JsonResponse({'result': 'get'})  # Sending an success response


# Get a to-do list item by id, called by javascript function
@csrf_exempt
def getListItemById(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_id = body['list_id']
        list_item_name = body['list_item_name']
        list_item_id = body['list_item_id']

        print("list_id: " + list_id)
        print("list_item_name: " + list_item_name)
        print("list_item_id: " + list_item_id)

        try:
            with transaction.atomic():
                query_list = List.objects.get(id=list_id)
                query_item = ListItem.objects.get(id=list_item_id)
                print("item_text", query_item.item_text)
                # Sending an success response
                return JsonResponse({'item_id': query_item.id, 'item_name': query_item.item_name, 'list_name': query_list.title_text, 'item_text': query_item.item_text})
        except IntegrityError:
            print("query list item" + str(list_item_name) + " failed!")
            JsonResponse({})
    else:
        return JsonResponse({'result': 'get'})  # Sending an success response


# Create a new to-do list, called by javascript function
@csrf_exempt
def createNewTodoList(request):

    if not request.user.is_authenticated:
        return redirect("/login")

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_name = body['list_name']
        create_on = body['create_on']
        tag_name = body['list_tag']
        shared_user = body['shared_user']
        user_not_found = []
        print(shared_user)
        create_on_time = datetime.datetime.fromtimestamp(create_on)
        # print(list_name)
        # print(create_on)
        # create a new to-do list object and save it to the database
        try:
            with transaction.atomic():
                user_id = request.user.id
                # print(user_id)
                todo_list = List(user_id_id=user_id, title_text=list_name, created_on=create_on_time, updated_on=create_on_time, list_tag=tag_name)
                if body['create_new_tag']:
                    # print('new tag')
                    new_tag = ListTags(user_id_id=user_id, tag_name=tag_name, created_on=create_on_time)
                    new_tag.save()

                todo_list.save()
                print(todo_list.id)

                # Progress
                if body['shared_user']:
                    user_list = shared_user.split(' ')
                    

                    k = len(user_list)-1
                    i = 0
                    while i <= k:

                        try:
                            query_user = User.objects.get(username=user_list[i])
                        except User.DoesNotExist:
                            query_user = None

                        if query_user:

                            shared_list_id = SharedList.objects.get(user=query_user).shared_list_id
                            shared_list_id = shared_list_id + str(todo_list.id) + " "
                            SharedList.objects.filter(user=query_user).update(shared_list_id=shared_list_id)
                            i += 1
                            
                        else:
                            print("No user named " + user_list[i] + " found!")
                            user_not_found.append(user_list[i])
                            user_list.remove(user_list[i])
                            k -= 1

                    shared_user = ' '.join(user_list)
                    new_shared_user = SharedUsers(list_id=todo_list, shared_user=shared_user)
                    new_shared_user.save()

                    print(user_not_found)

                    if user_list:
                        List.objects.filter(id=todo_list.id).update(is_shared=True)

        except IntegrityError as e:
            print(str(e))
            print("unknown error occurs when trying to create and save a new todo list")
            return HttpResponse("Request failed when operating on database")
        # return HttpResponse("Success!")  # Sending an success response
        context = {
            'user_not_found': user_not_found,
        }
        return HttpResponse("Success!")
        # return redirect("index")
    else:
        return HttpResponse("Request method is not a Post")


# Register a new user account
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(user)

            # Add a empty list to SharedList table
            shared_list = SharedList(user=User.objects.get(username=user), shared_list_id="")
            shared_list.save()

            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("todo:index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="todo/register.html", context={"register_form":form})


# Login a user
def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("todo:index")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="todo/login.html", context={"login_form":form})


# Logout a user
def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.")
	return redirect("todo:index")


# Reset user password
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "todo/password/password_reset_email.txt"
                    c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_email = EmailMessage(subject, email, settings.EMAIL_HOST_USER, [user.email])
                        send_email.fail_silently = False
                        send_email.send()
                    except BadHeaderError:
                        return HttpResponse('Invalid header found')                  
                    return redirect("/password_reset/done/")
            else:
                messages.error(request, "Not an Email from existing users!")
        else:
            messages.error(request, "Not an Email from existing users!")
    
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="todo/password/password_reset.html", context={"password_reset_form":password_reset_form})


from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from django.shortcuts import render
from .models import ListItem, List
# from datetime import datetime, date, timedelta
from django.utils import timezone
from collections import defaultdict
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
import datetime


def user_analytics(request):
    user = request.user
    today = timezone.now().date()

    # Filter ListItems by lists belonging to the logged-in user
    user_lists = List.objects.filter(user_id=user)
    user_list_items = ListItem.objects.filter(list__in=user_lists)

    # Total tasks and overdue calculations
    total_tasks = user_list_items.count()
    overdue_tasks = user_list_items.filter(due_date__lt=today, is_done=False).count()
    overdue_percentage = (overdue_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Aggregations for daily, weekly, and monthly completions
    daily_completions = user_list_items.filter(is_done=True).annotate(date=TruncDay('finished_on')).values('date').annotate(count=Count('id')).order_by('date')
    weekly_completions = user_list_items.filter(is_done=True).annotate(week=TruncWeek('finished_on')).values('week').annotate(count=Count('id')).order_by('week')
    monthly_completions = user_list_items.filter(is_done=True).annotate(month=TruncMonth('finished_on')).values('month').annotate(count=Count('id')).order_by('month')

    # Convert data for Chart.js
    daily_data = {
        'labels': [item['date'].strftime('%Y-%m-%d') for item in daily_completions],
        'counts': [item['count'] for item in daily_completions]
    }
    weekly_data = {
        'labels': [item['week'].strftime('%Y-%W') for item in weekly_completions],
        'counts': [item['count'] for item in weekly_completions]
    }
    monthly_data = {
        'labels': [item['month'].strftime('%Y-%m') for item in monthly_completions],
        'counts': [item['count'] for item in monthly_completions]
    }

    # Procrastination and completion time metrics
    total_procrastination_hours = 0
    procrastination_count = 0
    total_completion_time = 0
    completion_count = 0

    # Iterate only over tasks with both created_on and finished_on dates for completion time
    for item in user_list_items.filter(is_done=True, finished_on__isnull=False, created_on__isnull=False):
        # Procrastination calculation
        if item.due_date:
            due_date = timezone.make_aware(
                datetime.datetime.combine(item.due_date, datetime.datetime.min.time())
            ) if isinstance(item.due_date, datetime.date) else item.due_date
            procrastination_duration = (item.finished_on - due_date).total_seconds() / 3600
            if procrastination_duration > 0:
                total_procrastination_hours += procrastination_duration
                procrastination_count += 1

        # Completion time calculation
        print(f"Task {item.id}: created_on = {item.created_on}, finished_on = {item.finished_on}")
        completion_time = (item.finished_on - item.created_on).total_seconds() / 3600
        total_completion_time += completion_time
        completion_count += 1

    # Calculate averages, ensuring non-zero denominators
    avg_procrastination_hours = total_procrastination_hours / procrastination_count if procrastination_count > 0 else 0
    avg_completion_time_hours = total_completion_time / completion_count if completion_count > 0 else 0

    # Task density for busy days
    tasks_per_day = defaultdict(int)
    for item in user_list_items:
        if item.due_date:
            tasks_per_day[item.due_date] += 1

    # Classify busy days
    busy_days = {}
    for due_date, count in tasks_per_day.items():
        if count >= 5:
            busy_days[due_date] = 'Very Busy'
        elif count >= 3:
            busy_days[due_date] = 'Busy'
        elif count >= 1:
            busy_days[due_date] = 'Moderately Busy'
        else:
            busy_days[due_date] = 'Not Busy'
    print(busy_days)

    # Calendar events based on user's tasks with a due date
    calendar_events = [
        {
            "title": item.item_name,
            "start": item.due_date.strftime('%Y-%m-%d'),
            "end": item.due_date.strftime('%Y-%m-%d')  # Optional end date
        }
        for item in user_list_items if item.due_date
    ]

    context = {
        'list_items': user_list_items,
        'daily_data': daily_data,
        'weekly_data': weekly_data,
        'monthly_data': monthly_data,
        'due_soon_count': user_list_items.filter(due_date__gte=today, is_done=False).count(),
        'overdue_count': overdue_tasks,
        'completed_count': user_list_items.filter(is_done=True).count(),
        'overdue_percentage': overdue_percentage,
        'avg_procrastination_hours': avg_procrastination_hours,
        'avg_completion_time_hours': avg_completion_time_hours,
        'busy_days': busy_days,
        'today': today,
        'calendar_events': mark_safe(json.dumps(calendar_events))
    }

    return render(request, 'todo/user_analytics.html', context)
