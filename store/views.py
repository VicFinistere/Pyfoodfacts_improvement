"""
This file handle django app views (store/views.py)
"""
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.http import Http404
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.urls import reverse_lazy
from django.views import generic

from gofacts_project import settings
from store import logic
from .models import Product, Profile


def page_not_found_view(request, exception=None):
    """
    Page not found
    :param request:
    :param exception:
    :return: Page not found page
    """
    context = RequestContext(request)
    err_code = 404
    response = render_to_response('store/404.html', {"code": err_code}, context)
    response.status_code = 404
    return response


def server_error_view(request, exception=None):
    """
    Server error
    :param request:
    :param exception:
    :return: Server error page
    """
    context = RequestContext(request)
    err_code = 500
    response = render_to_response('store/500.html', {"code": err_code}, context)
    response.status_code = 500
    return response


class SignUp(generic.CreateView):
    """
    Sign up
    """
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'store/signup.html'


def index(request):
    """
    Index page
    :param request:
    :return: Index page
    """
    # .order_by('-created_at')[:12]
    # products = Product.objects.filter(available=True)
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'store/index.html', context)


def search(request, product_code=None, nova=False):
    """
    Search product and substitutes
    :param request:
    :param product_code:
    :param nova:
    :return: results page
    """
    query = request.GET.get('query')
    full_result = request.GET.get('full_result')
    product_array = logic.get_product_array(query, product_code)
    print("Nova : {}".format(nova))
    if product_code is not None:
        full_result = True

    if product_array is not None:
        print("Product is found in view ! (view)")

        [
            product_name,
            product_code,
            product_grade,
            product_image,
            product_categories,
            product_nutriments
        ] \
            = product_array

        product_nova = 0
        substitutes = None

        if full_result:
            if nova:
                product_nova = logic.pull_product(product_code, nova=True)
                print("This is the nova group for this product {}".format(product_nova))

                print("We are searching for more natural products ! (view)")
                substitutes = logic.get_nova_substitutes(product_categories, product_array[1], product_nova)
                # for substitute in substitutes:
                #     nova_list.append(substitute[5]['nova-group'])
                s = 0

                for substitute in substitutes:
                    substitutes[s] = [substitutes[s], substitute[5]['nova-group']]
                    s += 1
            else:
                print("Now for the substitutes ! (view)")
                substitutes = logic.get_substitutes(product_categories, product_array[1], product_grade)

        product_code = logic.int_code(product_code)
        print("Product nova : {}".format(product_nova))
        context = {
            'query': query,
            'categories': product_categories,
            'product_name': product_name,
            'product_code': product_code,
            'product_grade': product_grade,
            'product_nova': product_nova,
            'product_image': product_image,
            'product_nutriments': product_nutriments,
            'full_result': full_result,
            'substitutes': substitutes,
        }
        logging.info('New search for {}'.format(product_name))
        return render(request, 'store/results.html', context)

    return incomplete_product_search(request=request, query=query)


def incomplete_product_search(request, query):
    product = logic.search_incomplete_product(query)

    if product:
        if product is not None:

            if len(product) == 4:
                [product_name, product_grade, product_image, product_code] = product
                context = {
                    'query': query,
                    'product_name': product_name,
                    'product_grade': product_grade,
                    'product_image': product_image,
                    'product_code': product_code
                }
                logging.info('New search for {}'.format(product_name))
                return render(request, 'store/incomplete.html', context)

            else:
                [product_name, product_image, product_code] = product
                context = {
                    'query': query,
                    'product_name': product_name,
                    'product_image': product_image,
                    'product_code': product_code
                }
                logging.info('New search for {}'.format(product_name))
                return render(request, 'store/incomplete.html', context)

        raise Http404("Product can't be found...")
    raise Http404("There is no product for the search")


def product_page(request, product_code):
    """
    Get a page for product

    :param request:
    :param product_code:
    :return: Page product
    """
    product = product_code

    if product:
        product_array = logic.pull_product(product_code)
        print("Product is found in view ! (view)")

        if product_array is not None:
            [
                product_name,
                product_code,
                product_grade,
                product_image,
                categories,
                product_nutriments
            ] \
                = product_array

            context = {
                'categories': categories,
                'product_name': product_name,
                'product_code': product_code,
                'product_grade': product_grade,
                'product_image': product_image,
                'product_nutriments': product_nutriments,
            }
            return render(request, 'store/product.html', context)

        else:
            print("Product array can't be complete...")
            raise Http404("Product array can't be complete...")
    else:
        print("Product page can't be found...")
        raise Http404("Product page can't be found...")


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
@transaction.atomic
def profile_page(request):
    """
    User page
    :param request:
    :return:
    """

    query_user = User.objects.filter(id=request.user.id)
    if query_user.exists():
        user = User.objects.get(id=request.user.id)
        Profile.objects.get_or_create(user=query_user[0])
        profile = Profile.objects.get(user=user)

        context = {
            'username': user.username,
            'profile': profile,
            'profile_user': profile.user,
            'user': user,
        }
        return render(request, 'store/profile.html', context)
    raise Http404("User page can't be found...")


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
@transaction.atomic
def update_profile(request):
    """
    Update profile
    :param request:
    :return: Updated profile
    """

    profile_user = request.GET.get('profile_user')
    gender = request.GET.get('gender')
    email = request.GET.get('email')

    user_query = User.objects.filter(id=profile_user)
    user = User.objects.get(id=profile_user)
    profile = Profile.objects.get(user=user_query[0])

    profile.gender = gender
    profile.save()

    user.email = email
    user.save()
    return profile_page(request)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
@transaction.atomic
def products_page(request):
    """
    Page of products
    :param request:
    :return:
    """
    pairs = logic.create_user_list(request.user)

    if pairs is not None:
        paginator = Paginator(pairs, 6)

        page = request.GET.get('page')
        try:
            pairs = paginator.page(page)
        except PageNotAnInteger:
            pairs = paginator.page(1)
        except EmptyPage:
            pairs = paginator.page(paginator.num_pages)

        context = {
            'pairs': pairs,
            'paginate': True
        }
        return render(request, 'store/products.html', context)
    raise Http404("Products can't be found...")


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
@transaction.atomic
def save_products_pair(request, product_code, substitute_code):
    """
    Stare a product
    :param request:
    :param product_code:
    :param substitute_code:
    :return: Page of products
    """

    if product_code and substitute_code:

        # Get both products
        product_array = logic.get_product_array(product_code)
        substitute_array = logic.search_product(substitute_code)

        product_is_saved = False
        if product_array is not None:
            product_is_saved = logic.save_product(product_array)

        substitute_is_saved = False
        if substitute_array is not None:
            substitute_is_saved = logic.save_product(substitute_array)

        stared = False
        if product_is_saved and substitute_is_saved:
            stared = logic.stare_product(request.user, product_array, substitute_array)

        if stared:
            context = {
                'substitute_code': substitute_code,
                'product_code': product_code
            }
            return render(request, 'store/save.html', context)

        else:
            raise Http404("Not able to save product and substitute")

    raise Http404("There is no product and substitute to save")


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
@transaction.atomic
def delete_products_pair(request, product_id, substitute_id):
    """
    Stare a product
    :param request:
    :param product_id:
    :param substitute_id:
    :return: Page of products
    """
    delete = logic.delete_product(request.user, product_id, substitute_id)
    context = RequestContext(request)

    if delete is False:
        response = render_to_response('store/products.html', {"code": 404}, context)
        response.status_code = 404
    else:
        response = render_to_response('store/products.html', {"code": 200}, context)
        response.status_code = 200

    return products_page(request)
