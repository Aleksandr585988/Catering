
from rest_framework import status, viewsets, routers
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Dish, DishOrderItem, Order, Restaurant
from .serializers import DishSerializer, OrderCreateSerializer, RestaurantSerializer
from .enums import OrderStatus
from shared.cache import CacheService
from .services import schedule_order
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
            "eta": DATE
        }


        WORKFLOW
        1. validate the input
        2. create ``
        """

        # Validates the input data
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not isinstance(serializer.validated_data, dict):
            raise ValueError("Invalid data format.")

        # Creates the order in the database
        order: Order = Order.objects.create(
            status=OrderStatus.NOT_STARTED,
            user=request.user,
            eta=serializer.validated_data["eta"],
        )
        
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

        schedule_order(order=order)


        print(f"New Food Order is created: {order.pk}.\nETA;{order.eta} ")

        # Creates a cacheable order structure to store in Redis 
        order_cache = {
            "id": order.pk,
            "status": order.status,
            "eta": order.eta.strftime("%Y-%m-%d"),
            "food": [
                {"dish_id": dish_order["dish"].id, "quantity": dish_order["quantity"]}
                for dish_order in dishes_order
            ],
        }

        # Checks if the order is already cached
        cached_order = self.cache_service.get(namespace="order", key=str(order.pk))
        if cached_order:
            return Response(
                data=json.loads(cached_order),
                status=status.HTTP_200_OK,              
            )

        # Stores the order in Redis cache with a TTL (1 hour)
        self.cache_service.set(namespace="order", key=str(order.pk), instance=order_cache, ttl=3600)
        cached_order = self.cache_service.get(namespace="order", key=str(order.pk))

        # Returns the response
        return Response(
            data={
                "id": order.pk,
                "status": order.status,
                "eta": order.eta,
                "food": order_cache["food"],
                "total": 9999,
            },
            status=status.HTTP_201_CREATED,
        )


# ViewSet For Restaurant
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    @action(detail=True, methods=["get"])
    def dishes(self, request, pk=None):
        restaurant = self.get_object()
        dishes = Dish.objects.filter(restaurant=restaurant)
        serializer = DishSerializer(dishes, many=True)
        return Response(data=serializer.data)


# ViewSet For Dish
class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer


router = routers.DefaultRouter()
router.register(prefix="food", viewset=FoodAPIViewSet, basename="food",)
router.register(prefix="restaurants", viewset=RestaurantViewSet, basename="restaurant")
router.register(prefix="dishes", viewset=DishViewSet, basename="dish")
