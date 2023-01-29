'''Photo app Forms'''
from django.shortcuts import render

from .forms import SearchForm
from .models import MyModel


def search_view(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['query']
        results = MyModel.objects.filter(name__contains=query)
    else:
        results = MyModel.objects.all()
    return render(request, 'search_results.html', {'form': form, 'results': results})

from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Search'}))