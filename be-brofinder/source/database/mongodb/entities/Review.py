class Review:
    def __init__(
            self, 
            text : str, 
            vote : int = None,
            media: list = [],
            date : str = "N/D"
        ) -> None:
        
        self.text = text
        
        if vote:
            self.vote = vote
        
        self.media = media
        self.date = date
