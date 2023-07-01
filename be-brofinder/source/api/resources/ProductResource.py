from source.api.BaseResource import BaseResource
from source.utils.MongoDB import MongoDB

class ProductResource(BaseResource):

    @property
    def mongo(self):
        return MongoDB()

    @property
    def urls(self):
        return ('/product')
    
    def get(self):
        rules = {
            "key" : {
                "type" : str,
                "required" : True,
                "location" : "args",
                "help" : "Il campo 'key' risulta essere obbligatorio, ma non è stato passato."
            },
            "filter" : {
                "type" : str,
                "default" : "keyword",
                "location" : "args",
                "help" : "Il campo 'filter' risulta essere obbligatorio, ma non è stato passato.",
            },
            "price" : {
                "type" : int,
                "default": 0,
                "location" : "args"
            }
        }


        args = self.validate(rules)

        filters = {
            "url" : {"url" :  args["key"]},
            "name" : {"data.name" :  {"$regex" : f'.*{args["key"]}.*'}},
            "key" : {"data.keyword": {"$regex" : f'.*{args["key"]}.*'}}
        }

        or_cond = [filters[filt] for filt in args["filter"].split(",")]

        cond = {"$or" : or_cond}

        if args["price"] > 0:
            cond["price"] = {"$lte" : args['price']}

        products = []

        for product in self.mongo.collection("products").find(cond):
            del product["data"][-1]["_id"]

            product["data"][-1]["created_at"] = product["data"][-1]["created_at"].isoformat() 

            products.append(product["data"][-1])
        
        return products, 200