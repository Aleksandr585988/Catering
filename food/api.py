from rest_framework import status, viewsets, routers
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Dish, DishOrderItem, Order, Restaurant
from .serializers import DishSerializer, OrderCreateSerializer, RestaurantSerializer
from .enums import OrderStatus
from shared.cache import CacheService
import json


class FoodAPIViewSet(viewsets.GenericViewSet):
    cache_service = CacheService()

    # HTTP GET /food/dishes
    @action(methods=["get"], detail=False)
    def dishes(self, request):
        dishes = Dish.objects.all()
        serializer = DishSerializer(dishes, many=True)
        return Response(data=serializer.data)

    # HTTP GET /food/orders
    @action(methods=["post"], detail=False)
    def orders(self, request):
        """create new order for food.

        HTTP REQUEST EXAMPLE
        {
            "food": {
                1: 3  // id: quantity
                2: 1  // id: quantity
            },
            "eta": TIMESTAMP
        }


        WORKFLOW
        1. validate the input
        2. create ``
        """

        # Validates the input data
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not isinstance(serializer.validated_data, dict):
            raise ValueError(...)
        
        # Checks if the order is already cached
        cached_order = self.cache_service.get(f"order:{serializer.validated_data['id']}")
        if cached_order:
            print(f"Order {serializer.validated_data['id']} fetched from Redis cache")
            return Response(
                data=json.loads(cached_order),
                status=status.HTTP_200_OK,
            )

        # order = Order(status=OrderStatus.NOT_STARTED, provider=None)
        # order.save()

        # Creates the order in the database
        order = Order.objects.create(
            status=OrderStatus.NOT_STARTED, 
            user=request.user,
            eta=serializer.validated_data["eta"]
            )
        print(f"New Food Order is created: {order.pk}.\nETA;{order.eta} ")

        # Proces the food items (dishes) ordered
        try:
            dishes_order = serializer.validated_data["food"]
        except KeyError as error:
            raise ValueError("Food order is not properly built")

        # Creates DishOrderItems and associate them with the order
        for dish_order in dishes_order:
            instance = DishOrderItem.objects.create(
                dish=dish_order["dish"],
                quantity=dish_order["quantity"],
                order=order
            )
            print(f"New Dish Order Item is created: {instance.pk}")

        # Creates a cacheable order structure to store in Redis
        order_cache = {
            "id": order.pk,
            "status": order.status,
            "eta": order.eta,
            "food": [
                {"dish_id": dish_order["dish"], "quantity": dish_order["quantity"]}
                for dish_order in dishes_order
            ],
        }

        # Stores the order in Redis cache with a TTL (1 hour)
        self.cache_service.set(f"order:{order.pk}", json.dumps(order_cache), timeout=3600)
        print(f"Order {order.pk} cached in Redis")

        # Returns the response
        return Response(
            data={
                "id": order.pk,
                "status": order.status,
                "eta": order.eta,
                "total": 9999,
            },
            status=status.HTTP_201_CREATED,
        )


# ViewSet для Restaurant
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    @action(detail=True, methods=["get"])
    def dishes(self, request, pk=None):
        restaurant = self.get_object()
        dishes = Dish.objects.filter(restaurant=restaurant)
        serializer = DishSerializer(dishes, many=True)
        return Response(data=serializer.data)


# ViewSet для Dish
class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer


router = routers.DefaultRouter()
router.register(prefix="food", viewset=FoodAPIViewSet, basename="food",)
router.register(prefix="restaurants", viewset=RestaurantViewSet, basename="restaurant")
router.register(prefix="dishes", viewset=DishViewSet, basename="dish")
