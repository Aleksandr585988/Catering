import logging
import uuid

from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from config import celery_app
from shared.cache import CacheService

User = get_user_model()
# CACHE: dict[uuid.UUID, dict] = {}

logger = logging.getLogger(__name__)


@celery_app.task
def send_activation_mail(email: str, activation_link: str):
    send_mail(
        subject="User activation",
        message=f"Please, activate your accout: {activation_link}",
        from_email="admin@catering.support.com",
        recipient_list=[email],
    )


class Activator:
    UUID_NAMESPACE = uuid.uuid4()

    def __init__(self, email: str | None = None) -> None:
        self.email: str | None = email
        self.cache = CacheService()

    def create_activation_key(self) -> uuid.UUID:
        # assert self.email
        if self.email is None:
            raise ValueError("Email is not specified for activation key creation")
        return uuid.uuid3(self.UUID_NAMESPACE, self.email)

    def send_user_activation_email(self, activation_key: uuid.UUID):
        link = f"https://frontend.com/users/activation/{activation_key}"

        if self.email is None:
            raise ValueError("Email is required for activation")
        else:
            send_activation_mail.delay(
                email=self.email,
                activation_link=link,
            )

    def save_activation_information(self, user_id: int, activation_key: uuid.UUID):
        """Save activation information to the cache.

        1. Connect to the Cache Service
        2. Save the next structure to the Cache:
        {
            "266e78c9-f317-4f36-b489-683d3b905031": {
                "user_id": 3
            }
        }
        3. Return None
        """

        payload = {"user_id": user_id}

        # CACHE[activation_key] = payload
        self.cache.set(
            namespace="activation", key=str(activation_key), instance=payload
        )

    def activate_user(self, activation_key: uuid.UUID | None) -> None:
        if activation_key is None:
            raise ValueError("Can not activate user without activation key")

        # user_data = CACHE.pop(activation_key, None)
        user_data = self.cache.get(namespace="activation", key=str(activation_key))
        if not user_data:
            raise ValueError("Invalid activation key")

        user = User.objects.get(id=user_data["user_id"])
        if user.is_active:
            logger.info(f"User {user.email} is already activated.")
            return

        user.is_active = True
        user.save()
        logger.info(f"User {user.email} has been activated.")
