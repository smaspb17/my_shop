from celery import shared_task
from django.core.mail import send_mail
from celery.utils.log import get_task_logger

from .models import Order

logger = get_task_logger(__name__)


@shared_task
def order_created(order_id):
    """
    Задание по отправке уведомления по электронной почте
    при успешном создании заказа.
    """
    logger.info('Моя задача выполняется')
    order = Order.objects.get(id=order_id)
    subject = f'Заказ № {order.id}'
    message = f'Уважаемый(-ая) {order.first_name},\n\n' \
              f'Вы успешно создали заказ.' \
              f'Номер Вашего заказа - {order.id}.'
    mail_sent = send_mail(subject,
                          message,
                          'smaspb17@yandex.ru',
                          [order.email])
    return mail_sent
