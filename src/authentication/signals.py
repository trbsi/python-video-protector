import bugsnag
from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from src.user.models import UserProfile
from src.user.services.invitation.invitation_service import InvitationService


@receiver(user_signed_up)
def after_registration(request, user, **kwargs):
    UserProfile.objects.create(user=user)

    try:
        invited_by_username = request.COOKIES.get('invited_by')
        invitation_service = InvitationService()
        invitation_service.save_invitation(invited_by_username=invited_by_username, invited_user=user)
    except Exception as e:
        bugsnag.notify(e)
