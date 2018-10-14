"""
This file contains all the app logic functions ( logic.py )
"""
import re
import logging
import requests
from .models import Product, Favorite, User


def create_user_list(user):
    """
    Create a user list for products page
    :param user: The user
    :return: List of products for the user
    """

    pairs = []
    for i in range(Favorite.objects.filter(user=user).count()):
        pair = []
        product = Favorite.objects.filter(user=user)[i].product
        pair.append(product)

        substitute = Favorite.objects.filter(user=user)[i].substitute
        pair.append(substitute)
        pairs.append(pair)
        i += 1
    print(pairs)
    return pairs


def get_product_array(query, product_code=None):
    """
    Get product array
    :param query:
    :param product_code:
    :return:
    """

    if query:
        return search_product(query)
    elif product_code is not None:
        return search_product(product_code)
    else:
        return None


def get_products_id(product):
    """
    Get product id
    :param product:
    :return: product id
    """
    url = "https://fr.openfoodfacts.org/cgi/search.pl?search_terms={}".format(product)

    try:
        # Getting the id
        products_id = fetch_products_id(url)
        # print(products_id)
        # logging.info(products_id)
        return products_id
    except KeyError:
        return None


def search_product(products_id):
    """
    Search product
    :param products_id: Requested product(s)
    :return: Product array : name, code, grade, image, categories, nutriments
    """
    products_id = get_products_id(products_id)

    i = 0
    product_array = None
    while product_array is None and len(products_id) > i:
        product_array = get_product(products_id[i])
        i += 1
    return product_array


def fetch_products_id(url):
    """
    Fetch products in txt
    :param url: Page
    :return: products_id
    """
    data = requests.get(url)
    results = data.text
    products_id = re.findall(r'<a href="/produit/(\d+)/', results)
    return products_id


def save_product(product_array):
    """
    Save product in database
    :param product_array:
    :return: bool for success
    """

    try:
        Product.objects.get_or_create(
            name=product_array[0],
            code=product_array[1],
            grade=product_array[2],
            image=product_array[3],
            categories=product_array[4],
            nutriments=product_array[5]
        )
        logging.info("Success : Product in database !")
        return True

    except ValueError:
        logging.info("Fail : Get or create product didn't work ...")
        return False


def stare_product(user, product_array, substitute_array):
    """
    Staring product
    :param user:
    :param product_array:
    :param substitute_array:
    :return: bool for success
    """

    product_code = product_array[1]
    substitute_code = substitute_array[1]

    product = Product.objects.get(code=product_code)
    substitute = Product.objects.get(code=substitute_code)

    try:
        Favorite.objects.get_or_create(user=user, product=product, substitute=substitute)
        # print("Product stared !")
        # logging.info("Product stared !")
        return True

    except ValueError:
        return False


def delete_product(user, product_code, substitute_code):
    """
    Delete favorite product
    :param user:
    :param product_code:
    :param substitute_code:
    :return: bool for success
    """

    user = User.objects.filter(id=user.id)

    if user.exists():
        favorites = Favorite.objects.all()

        for favorite in favorites:

            if favorite.product.id == product_code:
                if favorite.substitute.id == substitute_code:
                    if favorite.user == user[0]:
                        print("Delete !")
                        logging.info("Delete !")

                        favorite.delete()
                        return True

    print("Delete failed!")
    logging.warning("Delete failed!")
    return False


def in_database(product_id):
    """
    Check if in database
    :param product_id: product id
    :return: product
    """
    stored_product = Product.objects.filter(code=product_id).count()

    if stored_product == 1:
        return Product.objects.get(code=product_id)

    elif stored_product > 1:
        while stored_product > 1:
            print("Destroy...")
            Product.objects.filter(code=product_id).delete()
        return Product.objects.get(code=product_id)

    else:
        return False


def get_product(product_id):
    """
    Get product array
    :param product_id: Requested product
    :return: product_array : Product, Category, Code, Grade, List of categories
    """
    if in_database(product_id):
        product_object = Product.objects.get(code=product_id)
        return [product_object.name,
                product_object.code,
                product_object.grade,
                product_object.image,
                product_object.categories,
                product_object.nutriments]
    else:
        product_array = pull_product(product_id)

        if product_array is not None:
            return product_array

        else:
            return None


def pull_product(product_id, product_code=None, nova=False):
    """
    Save product
    :param product_id: Requested product
    :param product_code: If fetching substitutes this is the product to substitute
    :param nova: Searching for group nova boolean
    :return: Product array : Product queryset, Category, List of categories, Grade, Id
    """
    page = "https://world.openfoodfacts.org/api/v0/product/{}.json".format(product_id)
    data = requests.get(page).json()

    if data:
        if data['product']:
            product = data['product']
            try:
                if product_code is not None:
                    # print("Product code is not None so we are fetching subs !")
                    # logging.info("Product code is not None so we are fetching subs !")

                    # We are fetching substitutes
                    product_array = fetch_product_array(product, product_code)
                else:
                    # print("Product code is None so we are fetching product !")
                    # logging.info("Product code is None so we are fetching product !")

                    # We are fetching product
                    if nova:
                        product_array = fetch_nova_group(product)
                    else:
                        product_array = fetch_product_array(product)

                if product_array is not None:
                    return product_array

                else:
                    return None

            except IndexError:
                return None

        else:
            return None
    else:
        return None


def fetch_product_array(product, product_code=None):
    """
    Fetch product array
    :param product:
    :param product_code:
    :return: product array
    """
    categories, image, name, code, grade, nutriments = 0, 0, 0, 0, 0, 0

    if 'code' in product:

        if product_code is not None:

            if product['code'] != product_code:
                code = product['code']
            else:
                return None
        else:
            code = product['code']

    if 'categories_hierarchy' in product:
        categories = product['categories_hierarchy']

    if 'image_url' in product:
        image = product['image_url']

    if 'product_name' in product:
        name = product['product_name']

    if 'nutrition_grades' in product:
        grade = product['nutrition_grades']

    if 'nutriments' in product:
        nutriments = product['nutriments']

    if categories and image and name and grade and nutriments:
        print("Fetching product array has worked !")
        logging.info("Fetching product array has worked !")
        return [name, code, grade, image, categories, nutriments]

    else:
        print("Fetching product array didn't worked !")
        logging.warning("Fetching product array didn't worked !")
        return None


def fetch_nova_group(product):
    """
    Fetch nova group
    :param product:
    :return: nova group
    """
    if 'nutriments' in product:
        nutriments = product['nutriments']

        if 'nova-group' in nutriments:
            print("{}".format(nutriments['nova-group']))
            return nutriments['nova-group']
        else:
            return None


def get_substitutes(categories, product_code, minimal_grade):
    """
    Get substitutes for product
    :param categories: The requested list of categories
    :param product_code: The product code
    :param minimal_grade: The minimal grade
    :return:
    """
    # print("get substitutes (logic)")
    # logging.info("get substitutes (logic)")
    categories = list_categories(categories)

    substitutes = None
    while substitutes is None:

        # category = get_category(categories)

        if len(categories) > 1:
            category = categories[-1]
            categories = categories.pop()
        else:
            category = categories[0]

        substitutes = search_substitutes(category, minimal_grade, product_code)

    return substitutes


def get_nova_substitutes(categories, product_code):
    """
    Get substitutes for product
    :param categories: The requested list of categories
    :param product_code: The product code
    :return:
    """
    # print("get substitutes (logic)")
    # logging.info("get substitutes (logic)")
    categories = list_categories(categories)
    minimal_nova = pull_product(product_code, nova=True)
    if minimal_nova is None:
        return None
    else:
        print("{}(get nova substitutes)".format(minimal_nova))
        nova_substitutes = None
        while nova_substitutes is None:

            # category = get_category(categories)

            if len(categories) > 1:
                category = categories[-1]
                categories = categories.pop()
            else:
                category = categories[0]

            nova_substitutes = search_nova_substitutes(category, minimal_nova, product_code)

        return nova_substitutes


def search_substitutes(category, minimal_grade, product_code):
    """
    Search substitutes
    :param category:
    :param minimal_grade:
    :param product_code:
    :return: substitutes
    """
    url = url_category_for_grade(category, minimal_grade)
    # [url, category] = try_url_redirection(url, category)

    if url is not None:

        print(" We will use this URL to fetch substitutes ")

        nutrition_score = ord('a')
        substitutes = None

        i = -1

        while substitutes is None and 5 > i and 97 + i <= ord(minimal_grade) - 1:
            i += 1
            url = url_category_for_grade(category, grade=chr(nutrition_score + i))
            substitutes = fetch_substitutes(url, product_code)
        return substitutes

    else:
        return None


def search_nova_substitutes(category, minimal_nova, product_code):
    """
    Search substitutes
    :param category:
    :param minimal_nova:
    :param product_code:
    :return: substitutes
    """
    url = url_category_for_grade(category, minimal_nova)
    # [url, category] = try_url_redirection(url, category)

    if url is not None:

        print(" We will use this URL to fetch substitutes ")

        nova_substitutes = None
        i = -1

        while nova_substitutes is None and 4 > i and i <= int(minimal_nova):
            i += 1
            url = url_category_for_nova(category, nova=i)
            nova_substitutes = fetch_substitutes(url, product_code)
        return nova_substitutes

    else:
        return None


def fetch_substitutes(url, product_code):
    """
    Fetch substitutes
    :param url: Products url
    :param product_code: Product code
    :return:
    """
    substitutes = []

    products_id = fetch_products_id(url)

    if products_id:

        for _, product_val in enumerate(products_id):
            print(product_val)
            print(product_code)
            if product_val != product_code:
                product_array = get_product(product_val)

                if product_array:
                    substitutes.append(product_array)

                if len(substitutes) >= 6:
                    return substitutes

        return substitutes

    else:
        print("Product range is None")
        return None


def list_categories(categories):
    """
    List categories
    :param categories:
    :return: list of categories
    """
    if isinstance(categories, str):
        categories = categories.replace("]", "")
        categories = categories.replace("[", "")
        categories = categories.replace("'", "")
        categories = ''.join(categories).split(',')
    return categories


def url_category_for_grade(category, grade):
    """
    Url category for grade
    :param category:
    :param grade:
    :return:
    """

    url = "https://fr.openfoodfacts.org/cgi/search.pl?action=process&" \
          "tagtype_0=categories&tag_contains_0=contains&tag_0={}" \
          "&tagtype_1=nutrition_grades&tag_contains_1=contains&tag_1={}" \
          "&sort_by=unique_scans_n&page_size=20&axis_x=energy&axis_y=products_n" \
          "&action=display".format(category, grade)

    return url


def url_category_for_nova(category, nova):
    """
        Url category for grade
        :param category:
        :param nova:
        :return:
        """

    url = "https://fr.openfoodfacts.org/cgi/search.pl?action=process&" \
          "tagtype_0=categories&tag_contains_0=contains&tag_0={}" \
          "&tagtype_1=nova_groups&tag_contains_1=contains&tag_1={}" \
          "&sort_by=unique_scans_n&page_size=20&axis_x=energy&axis_y=products_n" \
          "&action=display".format(category, nova)

    return url


def int_code(product_code):
    """
    Check if code is an integer for template
    :param product_code:
    :return:
    """
    if not isinstance(product_code, int):
        product_code = int(product_code)
    else:
        product_code = product_code

    return product_code
