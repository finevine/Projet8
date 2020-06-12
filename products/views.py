from django.shortcuts import redirect
from django.views import generic
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Product, Favourite


@login_required
def save(request, pk_health, pk_unhealth):
    ''' save a favorite parameters are defined in the url path '''
    healthy_product = Product.objects.get(code=pk_health)
    unhealthy_product = Product.objects.get(code=pk_unhealth)
    try:
        favourite = Favourite(
            healthy_product=healthy_product,
            unhealthy_product=unhealthy_product,
            owner=request.user
        )
        favourite.save()
    except IntegrityError:
        # integrity of the database is affected :
        # foreign key check fails, duplicate key, etc.
        pass
    # Redirect to referer or products index if no referer
    return redirect(
        request.META.get('HTTP_REFERER', reverse('products:index'))
        )


@login_required
def delete(request, pk_health, pk_unhealth):
    ''' delete a favourite parameters are defined in the url path '''
    healthy_product = Product.objects.get(code=pk_health)
    unhealthy_product = Product.objects.get(code=pk_unhealth)
    try:
        favourite = Favourite.objects.get(
            healthy_product=healthy_product,
            unhealthy_product=unhealthy_product,
            owner=request.user)
        favourite.delete()
    except IntegrityError:
        pass
    return redirect(request.META.get('HTTP_REFERER'))


class ProductsView(generic.ListView):
    ''' GET param : "q" product to find '''
    model = Product
    paginate_by = 12
    # Could skip the template_name .ListView take for template model_list.html
    template_name = 'products/product_list.html'

    def get_queryset(self):
        ''' return 120 similar products '''
        name = self.request.GET.get('q')
        return Product.objects.get_similar(name.lower())[:120]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # name to find in product name or category
        context['query'] = self.request.GET.get('q')
        return context


@method_decorator(login_required, name='dispatch')
class FavouritesView(generic.ListView):
    model = Favourite
    paginate_by = 12
    template_name = 'products/favourites_list.html'

    def get_queryset(self):
        return Favourite.objects.filter(
            owner=self.request.user).order_by('unhealthy_product__code')


class CompareView(generic.ListView):
    '''
    parameter : "category:id"
    GET param : "code" product to compare
    Show the candidates products for being favourite
    to replace a given product
    '''
    model = Product
    paginate_by = 12
    template_name = 'products/compare_list.html'

    def get_queryset(self):
        ''' return max 120 better products '''
        self.product_to_replace = Product.objects.get(code=self.kwargs['pk'])
        return Product.objects.get_better(self.product_to_replace)[:120]

    def get_context_data(self, **kwargs):
        ''' Pass the context that will be used in template '''
        context = super().get_context_data(**kwargs)

        context['categories'] = self.product_to_replace.categories
        context['product_to_replace'] = self.product_to_replace
        context['headerImg'] = self.product_to_replace.image

        # # From products of the same category ...
        # products = Product.objects.filter(
        #     categories__name=self.product_to_replace.categories)
        # ... check if they are already saved by the user :
        if self.request.user.is_authenticated:
            context['in_fav'] = [
                prod.code for prod in self.get_queryset()
                if Favourite.objects.filter(
                    healthy_product=prod.code,
                    unhealthy_product=self.product_to_replace.code,
                    owner=self.request.user,
                    ).exists()
                ]
        else:
            context['in_fav'] = []
        return context

    # @register.filter
    # def get_item(dictionary, key):
    #     '''
    #     to find items in a dict in a template filter
    #     not used here but kept for learning purpose
    #     '''
    #     return dictionary.get(key)


class ProductDetailView(generic.DetailView):
    '''
    parameter : "product:code"
    Show the details of a given product
    '''
    model = Product

    def get_context_data(self, **kwargs):
        ''' Add hearderImg in context '''
        context = super().get_context_data(**kwargs)
        context['headerImg'] = self.object.image
        return context
