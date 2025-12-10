from src.user.models import User
from src.user.models.invitation import Invitation


class InvitationService:
    MAX_INVITES = 10

    def can_invite(self, username: str) -> bool:
        user_exists = User.objects.filter(username=username).exists()
        if user_exists and not self._max_invites_reached(username):
            return True

        return False

    def save_invitation(self, invited_by_username: str, invited_user: User) -> None:
        invited_by = User.objects.get(username=invited_by_username)
        Invitation.objects.create(invited_user=invited_user, invited_by=invited_by)

    def _max_invites_reached(self, username: str) -> bool:
        count = Invitation.objects.filter(invited_by__username=username).count()
        if count > self.MAX_INVITES:
            return True

        return False
