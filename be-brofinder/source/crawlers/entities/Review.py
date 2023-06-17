class Review:
    def __init__(self, text : str, vote : int = None) -> None:
        self.text = text
        if vote:
            self.vote = vote