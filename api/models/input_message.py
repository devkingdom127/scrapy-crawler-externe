class InputMessage:
    body = {}

    @staticmethod
    def get_options():
        options = InputMessage.body["crawler_options"]
        return options["start_url"], options["locations"], options["user"]
