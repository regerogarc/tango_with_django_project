from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from django.shortcuts import redirect

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

    return render(request, "rango/index.html", context = context_dict)

def about(request):
    
    context_dict = {"boldmessage": "This tutorial has been put together by Mr Incredible"}
    
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
            return redirect('/rango/')
        else:
            # The form contained error. Just print them to terminal
            print(form.errors)
    
    return render(request, 'rango/add_category.html', {'form':form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect('/rango/')
    
    form = PageForm()

    if request.method == "POST":
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.save()
                
                print("Page Created!: ", page)

                return redirect("/rango/")
        else:
            print(form.errors)
    return render(request, 'rango/add_page.html', {'form':form, 'category':category})
