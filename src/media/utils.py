import re as regex

from src.user.models import User


def replace_tags(description: str | None) -> str | None:
    if not description:
        return description
    user_tags = regex.findall(r"@\w+", description)
    for user_tag in user_tags:
        username = user_tag.replace('@', '')
        user = User.objects.filter(username=username).first()
        if not user:
            continue

        description = description.replace(user_tag, f'@{user.id}')

    return description


def load_tags(description: str | None) -> str | None:
    if not description:
        return description
    # Replace numerical @ with string @
    # e.g. @11 is @some_username
    user_tags = regex.findall(r'@\w+', description)
    for user_tag in user_tags:
        id = user_tag.replace('@', '')
        if not id.isdigit():
            continue

        user = User.objects.filter(id=id).first()
        if not user:
            continue

        description = description.replace(user_tag, f'@{user.username}')

    return description
