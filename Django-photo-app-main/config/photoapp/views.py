'''Photo app generic views'''

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from photoapp.models import Photo

from .models import Photo


class PhotoListView(LoginRequiredMixin, ListView):
    model = Photo
    template_name = 'photoapp/list.html'
    context_object_name = 'photos'


class PhotoTagListView(PhotoListView):
    
    template_name = 'photoapp/taglist.html'
    
    # Custom function
    def get_tag(self):
        return self.kwargs.get('tag')

    def get_queryset(self):
        return self.model.objects.filter(tags__slug=self.get_tag())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.get_tag()
        return context
     

class PhotoDetailView(UserPassesTestMixin, DetailView):
    model = Photo
    template_name = 'photoapp/detail.html'
    context_object_name = 'photo'

    def test_func(self):
        photo = self.get_object()
        return self.request.user == photo.submitter


class PhotoCreateView(LoginRequiredMixin, CreateView):

    model = Photo
    
    fields = ['title', 'description', 'image', 'tags']

    template_name = 'photoapp/create.html'
    
    success_url = reverse_lazy('photo:list')

    def form_valid(self, form):

        form.instance.submitter = self.request.user
        
        return super().form_valid(form)

class UserIsSubmitter(UserPassesTestMixin):

    # Custom method
    def get_photo(self):
        return get_object_or_404(Photo, pk=self.kwargs.get('pk'))
    
    def test_func(self):
        
        if self.request.user.is_authenticated:
            return self.request.user == self.get_photo().submitter
        else:
            raise PermissionDenied('Sorry you are not allowed here')

class PhotoUpdateView(UserIsSubmitter, UpdateView):
    
    template_name = 'photoapp/update.html'

    model = Photo

    fields = ['title', 'description', 'tags']
    
    success_url = reverse_lazy('photo:list')

class PhotoDeleteView(UserIsSubmitter, DeleteView):
    
    template_name = 'photoapp/delete.html'

    model = Photo

    success_url = reverse_lazy('photo:list')\

from django.db.models import Q
from django.shortcuts import render
from photoapp.models import Photo

from .models import Photo


def search(request):
    query = request.GET.get('q')
    photos = Photo.objects.filter(tags__name__icontains=query)
    return render(request, 'photoapp/search_results.html', {'photos': photos, 'q': query})
