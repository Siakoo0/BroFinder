from source.api.dto.EntityDTO import EntityDTO 

class SearchDTO(EntityDTO):
    def __init__(self) -> None:
        super().__init__([
           "text",  
           "user", 
           "forward"
        ])