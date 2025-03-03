import uuid
import logging
from django.core.mail import send_mail
from django.contrib.auth import get_user_model


User = get_user_model()
CACHE: dict[uuid.UUID, dict] = {}

logger = logging.getLogger(__name__)


class Activator:
    UUID_NAMESPACE = uuid.uuid4()

    def __init__(self, email: str | None = None) -> None:
        self.email: str | None = email

    def create_activation_key(self) -> uuid.UUID:
        # assert self.email
        if self.email is None:
            raise ValueError("Email is not specified for activation key creation")
        return uuid.uuid3(self.UUID_NAMESPACE, self.email)

    def send_user_activation_email(self, activation_key: uuid.UUID):
        link = f"https://frontend.com/users/activation/{activation_key}"
        self.send_activation_mail(activation_link=link)

    def send_activation_mail(self, activation_link: str):
        if self.email is None:
            raise ValueError("Email is not specified to send the Email")
        else:
            send_mail(
                subject="User activation",
                message=f"Please, activate your accout: {activation_link}",
                from_email="admin@catering.support.com",
                recipient_list=[self.email],
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
        CACHE[activation_key] = payload

    def activate_user(self, activation_key: uuid.UUID | None) -> None:
        if activation_key is None:
            raise ValueError("Can not activate user without activation key")

        user_data = CACHE.pop(activation_key, None)
        if not user_data:
            raise ValueError("Invalid activation key")

        user = User.objects.get(id=user_data["user_id"])
        if user.is_active:
            logger.info(f"User {user.email} is already activated.")
            return

        user.is_active = True
        user.save()
        logger.info(f"User {user.email} has been activated.")

