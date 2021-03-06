from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    # Query the DB for a list of all the categories. Order the list in descending order of likes.
    # Then take the first 5 elements - the top 5 categories, and place it in the context_dict.
    # The - in -likes specifies descending order.
    category_list = Category.objects.order_by("-likes")[:5]
    # Get the 5 most viewed pages
    page_list = Page.objects.order_by("-views")[:5]

    context_dict = {}

    context_dict["boldmessage"] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict["categories"] = category_list
    context_dict["pages"] = page_list

    visitor_cookie_handler(request)

    response = render(request, "rango/index.html", context = context_dict)

    return response

def get_server_side_cookie(request, cookie, defualt_val=None):
    val = request.session.get(cookie)
    if not val:
        val = defualt_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1

        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    
    request.session['visits'] = visits

def about(request):
    
    context_dict = {"boldmessage": "This tutorial has been put together by Finlay Durkin"}
    
    visitor_cookie_handler(request)
    context_dict["visits"] = request.session['visits']
    
    return render(request, "rango/about.html", context = context_dict)

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        #Try to find a category matching the slug. If not .get raises a DoesNotExist exception
        category = Category.objects.get(slug=category_name_slug)

        #Retrieve all the associated pages
        pages = Page.objects.filter(category=category)

        context_dict["pages"] = pages

        context_dict["category"] = category
    except Category.DoesNotExist:
        #Don't do anyting - the template will display a no category message.
        context_dict["category"] = None
        context_dict["pages"] = None

    return render(request, "rango/category.html", context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    # An HTTP POST request?
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            #Save the new category to the database.
            cat = form.save(commit=True)
            print("Category Created!: ", cat, cat.slug)

            # Redirect user back to index
            return redirect(reverse('index'))
        else:
            # The form contained error. Just print them to terminal
            print(form.errors)
    
    return render(request, 'rango/add_category.html', {'form':form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect(reverse('index'))
    
    form = PageForm()

    if request.method == "POST":
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                
                print("Page Created!: ", page)

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug':category_name_slug}))
        else:
            print(form.errors)
    return render(request, 'rango/add_page.html', {'form':form, 'category':category})

def register(request):
    # A boolean for telling the template wether the registration was succesfull or not.
    registered = False

    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # Hash the password with the set_password() method
            user.set_password(user.password)
            user.save()

            # Commit=False - don't save the model just yet - need to check everything first.
            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'rango/register.html', context = {'user_form': user_form, 
                                                            'profile_form': profile_form, 
                                                            'registered': registered})

def user_login(request):
    if request.method == 'POST':
        # Here we use .get instead of POST[''] becuase .get will return None if the var doesnt exist whereas .POST[''] will throw a KeyError Exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        # Try to match the credentials to user. Will return the user object or None if no matches were found.
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    
    # The request is not an HTTP POST so display the login form.
    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    # Since they're already logged in, user data is not required and we know which user they are.
    logout(request)
    return redirect(reverse('rango:index'))