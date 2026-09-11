from django.shortcuts import render

def home(request):
    context = {
        'title': 'Home Page'
    }
    return render(request, 'blog/home.html', context)

def contact_view(request):
    return render(request, 'blog/contact.html')


