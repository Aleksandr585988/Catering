from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self) -> None:
        # THREAD IMPLEMENTATION
        # from .processor import Processor
        # Processor().start()
        # return super().ready()

        # CALERY WORKER IMPLEMENTATION
        from .tasks import order_validation

        print("I am HERE.....")
        order_validation.delay()