from django.core.mail import EmailMultiAlternatives
from django.template.defaultfilters import striptags
from django.template.loader import render_to_string

from app import settings
from src.notification.value_objects.email_value_object import EmailValueObject


class EmailService:
    @staticmethod
    def send(notification: EmailValueObject) -> None:
        context = notification.template_variables
        context = {
            **context,
            'TEMPLATE_APP_NAME': settings.APP_NAME
        }
        html = render_to_string(notification.template_path, context=context)
        text = striptags(html)
        to_emails = settings.ADMIN_EMAILS if notification.to[0] == 'admins' else notification.to

        msg = EmailMultiAlternatives(
            subject=notification.subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_emails,
            reply_to=notification.get_reply_to()
        )
        msg.attach_alternative(html, "text/html")
        msg.send()
