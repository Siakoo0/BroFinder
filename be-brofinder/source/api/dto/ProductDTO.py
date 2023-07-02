from source.api.dto.EntityDTO import EntityDTO 

class ProductDTO(EntityDTO):
    def __init__(self) -> None:
        super().__init__([
            "_id",
            "name",
            "price",
            "description",
            "reviews",
            "images",
            "reviews_summary"
        ])