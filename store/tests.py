import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from store import logic
from store.models import Product, Favorite


class IndexPageTestCase(TestCase):
    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)


class SearchProductTestCase(TestCase):

    def test_search_product(self):
        """
        Search product
        :return: Product array : name, code, grade, image, categories, nutriments
        """

        name = "Nutella"

        code = "3017620429484"

        grade = "e"

        image = "https://static.openfoodfacts.org/images/products/301/762/042/9484/front_fr.147.400.jpg"

        categories = ["en:breakfasts", "en:spreads", "en:sweet-spreads", "fr:pates-a-tartiner",
                      "en:chocolate-spreads", "en:hazelnut-spreads", "en:cocoa-and-hazelnuts-spreads"]

        response = logic.search_product(code)
        response_json = json.dumps(response)
        print(response[5])
        product_array = [name, code, grade, image, categories, response[5]]
        product_array_json = json.dumps(product_array)
        self.assertEqual(response_json, product_array_json)


class UserListTestCase(TestCase):

    def setUp(self):
        """Create somme products in the database"""
        Product.objects.create(name='Nutella', grade='e', categories='test', nutriments="{'test_nutriment': 10}")
        Product.objects.create(name='Pâte à Tartiner', grade='a', categories='test',
                               nutriments="{'test_nutriment': 10}")

        self.product = Product.objects.get(name='Nutella')
        self.substitute = Product.objects.get(name='Pâte à Tartiner')

        User.objects.create(username='test_user_1')
        User.objects.create(username='test_user_0')

        self.user_1 = User.objects.get(username='test_user_1')
        self.user_0 = User.objects.get(username='test_user_0')

        Favorite.objects.create(user=self.user_0, substitute=self.substitute, product=self.product)

    def test_create_user_list(self):
        """
        Create a user list for products page
        :return: List of products for the user
        """

        users = User.objects.all()
        for user in users:
            if user.id == 1:
                response = logic.create_user_list(self.user_0)


class GetIdTestCase(TestCase):

    def setUp(self):
        self.query = 'Nutella'

    def test_get_products_id(self):
        """
        Get product id
        :return: product id
        """
        response = logic.get_products_id(self.query)

        expected_response = ['3017620429484', '3017624047813', '3017620401473', '59032823', '3017620402135',
                             '3017620421006', '3017620422003', '80135463', '3017624044003', '3017620428401',
                             '8000500142035', '3017620406003', '3017620424403', '8000500082379', '8000500045497',
                             '80051428', '8000500223321', '80050698', '80176800', '3017620425400']

        self.assertEqual(response, expected_response)


class FetchProductsIdTestCase(TestCase):

    def setUp(self):
        product = 'Nutella'
        self.url = "https://fr.openfoodfacts.org/cgi/search.pl?search_terms={}".format(product)

    def test_fetch_products_id(self):
        """
        Fetch products in txt
        :return: products_id
        """
        response = logic.fetch_products_id(self.url)

        expected_response = ['3017620429484', '3017624047813', '3017620401473', '59032823', '3017620402135',
                             '3017620421006', '3017620422003', '80135463', '3017624044003', '3017620428401',
                             '8000500142035', '3017620406003', '3017620424403', '8000500082379', '8000500045497',
                             '80051428', '8000500223321', '80050698', '80176800', '3017620425400']

        self.assertEqual(response, expected_response)


class SaveProductTestCase(TestCase):

    def setUp(self):
        self.product_array = ['Nutella', '3017620429484', 'e',
                              'https://static.openfoodfacts.org/images/products/301/762/042/9484/front_fr.147.400.jpg',
                              ['en:breakfasts', 'en:spreads', 'en:sweet-spreads', 'fr:pates-a-tartiner',
                               'en:chocolate-spreads', 'en:hazelnut-spreads', 'en:cocoa-and-hazelnuts-spreads'],
                              {'saturated-fat_value': '10.6', 'sugars_value': '56.3', 'nova-group_100g': '4',
                               'nutrition-score-uk_100g': '26', 'nutrition-score-fr': '26', 'proteins_serving': 0.945,
                               'sugars_serving': 8.44, 'fat': 30.9, 'carbohydrates_value': '57.5',
                               'carbohydrates': 57.5, 'saturated-fat_100g': 10.6, 'salt_unit': 'g',
                               'sodium_serving': 0.00591, 'nova-group': '4', 'energy_value': '539.0', 'fat_100g': 30.9,
                               'proteins_100g': 6.3, 'salt_serving': 0.015, 'fat_value': '30.9', 'proteins_unit': 'g',
                               'sugars': 56.3, 'salt_100g': 0.1, 'sodium_100g': 0.0393700787401575,
                               'carbohydrates_100g': 57.5, 'fat_unit': 'g', 'nova-group_serving': '4',
                               'saturated-fat_serving': 1.59, 'salt': 0.1, 'nutrition-score-fr_100g': '26',
                               'proteins': 6.3, 'sodium': 0.0393700787401575, 'saturated-fat': 10.6,
                               'energy_100g': '2255', 'sodium_value': '0.04', 'energy_unit': 'kcal',
                               'nutrition-score-uk': '26', 'saturated-fat_unit': 'g', 'proteins_value': '6.3',
                               'energy_serving': '338', 'sugars_unit': 'g', 'carbohydrates_unit': 'g',
                               'fat_serving': 4.63, 'energy': '2255', 'sugars_100g': 56.3,
                               'carbohydrates_serving': 8.62, 'salt_value': '0.1', 'sodium_unit': 'g'}]

    def test_save_product(self):
        """
        Save product in database
        :return: bool for success
        """

        response = logic.save_product(self.product_array)
        self.assertEqual(response, True)


class StareProductTestCase(TestCase):

    def setUp(self):
        """Create somme products in the database"""
        Product.objects.create(name='Nutella', grade='e', code='3017620429484')
        Product.objects.create(name='Pâte à Tartiner', grade='a', code='3662072013370')
        self.product = Product.objects.get(name='Nutella')
        self.substitute = Product.objects.get(name='Pâte à Tartiner')
        User.objects.create(username='test_user')
        self.user = User.objects.get(username='test_user')
        self.product_array = [0, self.product.code]
        self.substitute_array = [0, self.substitute.code]

    def test_stare_product(self):
        """
        Staring product
        :return: bool for success
        """

        response = logic.stare_product(self.user, self.product_array, self.substitute_array)
        self.assertEqual(response, True)


class DeleteProductTestCase(TestCase):

    def setUp(self):
        """Create somme products in the database"""
        Product.objects.create(name='Nutella', grade='e', code='3017620429484')
        Product.objects.create(name='Pâte à Tartiner', grade='a', code='3662072013370')

        self.product = Product.objects.get(name='Nutella')
        self.substitute = Product.objects.get(name='Pâte à Tartiner')

        User.objects.create(username='test_user')
        self.user = User.objects.get(username='test_user')

        Favorite.objects.create(user=self.user, substitute=self.substitute, product=self.product)

    def test_delete_product(self):
        """
        Delete favorite product
        :return: bool for success
        """

        response = logic.delete_product(self.user, self.product.id, self.substitute.id)
        self.assertEqual(response, True)


class CheckDatabaseTestCase(TestCase):
    def setUp(self):
        """Create somme products in the database"""
        Product.objects.create(name='Nutella', grade='e', code='3017620429484')
        self.product = Product.objects.get(name='Nutella')

    def test_in_database(self):
        """
        Check if in database
        :return: product
        """
        response = logic.in_database(self.product.code)
        self.assertEqual(response, self.product)


class GetProductTestCase(TestCase):
    def setUp(self):
        """Create somme products in the database"""
        Product.objects.create(name='Nutella', grade='e', code='3017620429484')
        self.product_array = ['Nutella', '3017620429484', 'e', '', '', '']

    def test_get_product(self):
        """
        Get product array
        """
        response = logic.get_product('3017620429484')
        self.assertEqual(response, self.product_array)


class PullProductTestCase(TestCase):

    def test_pull_product(self):
        """
        Save product
        :return: Product array : Product queryset, Category, List of categories, Grade, Id
        """

        response = logic.pull_product('3662072013370', '3017620429484')
        name = 'Pâte à Tartiner'
        code = '3662072013370'
        grade = 'a'
        image = 'https://static.openfoodfacts.org/images/products/366/207/201/3370/front_fr.4.400.jpg'
        categories = ['en:breakfasts', 'en:spreads', 'en:sweet-spreads', 'fr:pates-a-tartiner',
                      'en:chocolate-spreads', 'en:hazelnut-spreads', 'en:cocoa-and-hazelnuts-spreads']

        product_array = [name, code, grade, image, categories, response[5]]
        product_array_json = json.dumps(product_array)
        response_json = json.dumps(response)
        self.assertEqual(response_json, product_array_json)


class FetchProductTestCase(TestCase):
    def setUp(self):
        self.array = {'product_name': 'Ratatouille', 'code': '3560070486274', 'nutrition_grades': 'a',

                      'image_url': 'https://static.openfoodfacts.org/images/products/356/007/048/6274/'
                                   'front_fr.54.400.jpg',

                      'categories_hierarchy': ['en:canned-foods', 'en:meals', 'en:prepared-vegetables',
                                               'en:canned-meals', 'fr:ratatouilles'],
                      'nutriments': {'fruits-vegetables-nuts': '83', 'fruits-vegetables-nuts_value': '83',
                                     'salt_unit': 'g', 'carbohydrates_100g': '4.5', 'sodium_serving': '0.502',
                                     'fiber_value': '1.2', 'sodium_100g': '0.334645669291339', 'fiber': '1.2',
                                     'fat_100g': '1.2', 'fat_unit': 'g', 'energy': '146', 'saturated-fat_unit': 'g',
                                     'energy_serving': '219', 'sugars': '3.6', 'fiber_100g': '1.2', 'sodium_unit': 'g',
                                     'proteins_serving': '1.35', 'carbohydrates': '4.5',
                                     'fruits-vegetables-nuts_label': 'Fruits, légumes et noix(minimum)',
                                     'sodium': '0.334645669291339', 'energy_100g': '146', 'fiber_serving': '1.8',
                                     'fruits-vegetables-nuts_serving': '83', 'fat_serving': '1.8',
                                     'proteins_100g': '0.9', 'nutrition-score-uk_100g': -3, 'sugars_serving': '5.4',
                                     'saturated-fat': '0.2', 'nova-group': '4', 'salt_value': '0.85',
                                     'salt_100g': '0.85', 'sugars_unit': 'g', 'nutrition-score-fr': -3, 'salt': '0.85',
                                     'fat': '1.2', 'nutrition-score-uk': -3, 'energy_unit': 'kJ',
                                     'proteins_value': '0.9', 'proteins_unit': 'g', 'nova-group_serving': '4',
                                     'nutrition-score-fr_100g': -3, 'carbohydrates_value': '4.5',
                                     'sugars_value': '3.6', 'saturated-fat_value': '0.2',
                                     'carbohydrates_serving': '6.75', 'proteins': '0.9', 'saturated-fat_100g': '0.2',
                                     'fruits-vegetables-nuts_100g': '83', 'fat_value': '1.2', 'energy_value': '146',
                                     'sodium_value': '0.33464566929133854', 'nova-group_100g': '4',
                                     'carbohydrates_unit': 'g', 'fiber_unit': 'g', 'sugars_100g': '3.6',
                                     'fruits-vegetables-nuts_unit': 'g', 'salt_serving': '1.27',
                                     'saturated-fat_serving': '0.3'}}

    def test_fetch_product_array(self):
        """
        Fetch product array
        :return: product array
        """

        name = 'Ratatouille'
        code = '3560070486274'
        grade = 'a'
        image = 'https://static.openfoodfacts.org/images/products/356/007/048/6274/front_fr.54.400.jpg'
        categories = ['en:canned-foods', 'en:meals', 'en:prepared-vegetables', 'en:canned-meals', 'fr:ratatouilles']
        nutriments = {'fruits-vegetables-nuts': '83', 'fruits-vegetables-nuts_value': '83', 'salt_unit': 'g',
                      'carbohydrates_100g': '4.5', 'sodium_serving': '0.502', 'fiber_value': '1.2',
                      'sodium_100g': '0.334645669291339', 'fiber': '1.2', 'fat_100g': '1.2', 'fat_unit': 'g',
                      'energy': '146', 'saturated-fat_unit': 'g', 'energy_serving': '219', 'sugars': '3.6',
                      'fiber_100g': '1.2', 'sodium_unit': 'g', 'proteins_serving': '1.35', 'carbohydrates': '4.5',
                      'fruits-vegetables-nuts_label': 'Fruits, légumes et noix(minimum)', 'sodium': '0.334645669291339',
                      'energy_100g': '146', 'fiber_serving': '1.8', 'fruits-vegetables-nuts_serving': '83',
                      'fat_serving': '1.8', 'proteins_100g': '0.9', 'nutrition-score-uk_100g': -3,
                      'sugars_serving': '5.4', 'saturated-fat': '0.2', 'nova-group': '4', 'salt_value': '0.85',
                      'salt_100g': '0.85', 'sugars_unit': 'g', 'nutrition-score-fr': -3, 'salt': '0.85', 'fat': '1.2',
                      'nutrition-score-uk': -3, 'energy_unit': 'kJ', 'proteins_value': '0.9', 'proteins_unit': 'g',
                      'nova-group_serving': '4', 'nutrition-score-fr_100g': -3, 'carbohydrates_value': '4.5',
                      'sugars_value': '3.6', 'saturated-fat_value': '0.2', 'carbohydrates_serving': '6.75',
                      'proteins': '0.9', 'saturated-fat_100g': '0.2', 'fruits-vegetables-nuts_100g': '83',
                      'fat_value': '1.2', 'energy_value': '146', 'sodium_value': '0.33464566929133854',
                      'nova-group_100g': '4', 'carbohydrates_unit': 'g', 'fiber_unit': 'g', 'sugars_100g': '3.6',
                      'fruits-vegetables-nuts_unit': 'g', 'salt_serving': '1.27', 'saturated-fat_serving': '0.3'}

        response = logic.fetch_product_array(self.array, '3017620429484')
        product_array = [name, code, grade, image, categories, nutriments]
        product_array_json = json.dumps(product_array)
        response_json = json.dumps(response)
        self.assertEqual(response_json, product_array_json)


class FetchSubstitutesTestCase(TestCase):

    def setUp(self):
        category = 'fr:ratatouilles'
        grade = 'a'

        self.url = "https://fr.openfoodfacts.org/cgi/search.pl?action=process&" \
                   "tagtype_0=categories&tag_contains_0=contains&tag_0={}" \
                   "&tagtype_1=nutrition_grades&tag_contains_1=contains&tag_1={}" \
                   "&sort_by=unique_scans_n&page_size=20&axis_x=energy&axis_y=products_n" \
                   "&action=display".format(category, grade)

    def test_fetch_substitutes(self):
        """
        Fetch substitutes
        """

        response = logic.fetch_substitutes(self.url, '3560070486274')
        self.assertEqual(response, response)


class FetchNovaSubstitutesTestCase(TestCase):

    def setUp(self):
        category = 'fr:ratatouilles'
        nova_groups = '4'

        self.url = "https://fr.openfoodfacts.org/cgi/search.pl?action=process&" \
                   "tagtype_0=categories&tag_contains_0=contains&tag_0={}" \
                   "&tagtype_1=nova_groups&tag_contains_1=contains&tag_1={}" \
                   "&sort_by=unique_scans_n&page_size=20&axis_x=energy&axis_y=products_n" \
                   "&action=display".format(category, nova_groups)

    def test_fetch_substitutes(self):
        """
        Fetch substitutes
        """

        response = logic.fetch_nova_substitutes(self.url, '3560070486274')
        self.assertEqual(response, response)


class ListCategoriesTestCase(TestCase):
    def setUp(self):
        self.c_str = "'en:canned-foods', 'en:meals', 'en:prepared-vegetables', 'en:canned-meals', 'fr:ratatouilles'"
        self.c_list = ['en:canned-foods', ' en:meals', ' en:prepared-vegetables', ' en:canned-meals',
                       ' fr:ratatouilles']

    def test_list_categories(self):
        """
        List categories
        :return: list of categories
        """

        response = logic.list_categories(self.c_str)
        self.assertEqual(response, self.c_list)


class UrlCategoryTestCase(TestCase):
    def setUp(self):
        category = 'fr:ratatouilles'
        grade = 'a'

        self.url = "https://fr.openfoodfacts.org/cgi/search.pl?action=process&" \
                   "tagtype_0=categories&tag_contains_0=contains&tag_0={}" \
                   "&tagtype_1=nutrition_grades&tag_contains_1=contains&tag_1={}" \
                   "&sort_by=unique_scans_n&page_size=20&axis_x=energy&axis_y=products_n" \
                   "&action=display".format(category, grade)

    def test_url_category_for_grade(self):
        """
        Url category for grade
        """
        response = logic.url_category_for_grade('fr:ratatouilles', 'a')
        self.assertEqual(response, self.url)


class IntCodeTestCase(TestCase):

    def test_int_code(self):
        """
        Check if code is an integer for template
        """
        response = logic.int_code('3560070486274')
        self.assertEqual(response, 3560070486274)
