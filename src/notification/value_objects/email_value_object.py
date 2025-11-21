class EmailValueObject():
    def __init__(
            self,
            subject: str,
            template_path: str,
            template_variables: dict,
            to: list[str],
            reply_to_email: str | None = None,
            reply_to_name: str | None = None,
    ):
        self.subject = subject
        self.template_path = template_path
        self.template_variables = template_variables
        self.to = to
        self.reply_to_email = reply_to_email
        self.reply_to_name = reply_to_name

    def get_reply_to(self) -> list:
        return [f'{self.reply_to_name} <{self.reply_to_email}>']
