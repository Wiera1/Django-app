from string import ascii_letters
from random import choices
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from shopapp.models import Product
from shopapp.utils import add_two_numbers


class SimpleTest(TestCase):
    def test_details(self):
        response = self.client.get("/customer/details/")
        self.assertEqual(response.status_code, 404)

        # self.assertEqual(len(response.content["customers"]), 5)

class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        # Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "123.45",
                "description": "A good table",
                "discount": "10",
            }
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )

class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(name="Best Product", price="123.45")

    # @classmethod
    # def tearDownClass(cls):
    #     cls.product.delete()


    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})

        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})

        )
        self.assertContains(response, self.product.name)
#
#
class ProductsListViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        expected = Product.objects.filter(archived=False).order_by("pk")
        products_in_context = response.context["products"]
        self.assertQuerySetEqual(
            products_in_context,
            expected,
            transform=lambda x: x,
            ordered=False,
        )
        # self.assertQuerysetEqual(
            # qs=Product.objects.filter(archived=False).all(),
            # values=(p.pk for p in response.context["products"]),
            # transform=lambda p: p.pk
        # )
        self.assertTemplateUsed(response, 'shopapp/products-list.html')


class OrdersListViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.credentials = dict(username="bob_test", password="qwerty")
        cls.user = User.objects.create_user(**cls.credentials)

    # @classmethod
    # def tearDownClass(cls):
    #     cls.user.delete()

    def setUp(self) -> None:
        super().setUp()
        self.user = self.__class__.user
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.credentials = dict(username="bob_test", password="qwerty")
        cls.user = User.objects.create_user(**cls.credentials)

    def tearDownClass(cls):
        cls.user.delete()
        cls.order_list.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_order_details(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Discount")
        self.assertContains(response, "Orders")


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(
            reverse("shopapp:products-export"),
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data,
        )


class OrdersExportTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'products-fixture.json',
        'orders-fixture.json',
    ]

    @classmethod
    def setUpTestData(cls):
        cls.staff_user = User.objects.create_user(username='staffuser', password='pass', is_staff=True)

    @classmethod
    def tearDownClass(cls):
        cls.staff_user.delete()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.client.force_login(self.staff_user)

    def test_order_export(self):
        url = reverse("shopapp:order_list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertIn("orders", json_data)
        orders = json_data["orders"]

        self.assertIsInstance(orders, list)

        order = orders[0]
        self.assertIn("id", order)
        self.assertIn("address", order)
        self.assertIn("promo_code", order)
        self.assertIn("user_id", order)
        self.assertIn("product_ids", order)
        self.assertIsInstance(order["product_ids"], list)