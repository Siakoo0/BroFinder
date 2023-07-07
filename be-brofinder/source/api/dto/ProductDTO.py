from source.api.dto.EntityDTO import EntityDTO 

class ProductDTO(EntityDTO):
    def __init__(self) -> None:
        super().__init__([
            "_id",
            "url",
            "name",
            "price",
            "description",
            "reviews",
            "images",
            "reviews_summary",
            "created_at"
        ])