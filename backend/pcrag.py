from pinecone import Pinecone, ServerlessSpec
import pinecone
import time
from sentence_transformers import SentenceTransformer

class PineconeRAG:
    def __init__(self, api_key, index_name="rag-index", dimension=384,embedding_model="multi-qa-MiniLM-L6-cos-v1" , metric="cosine"):
        # Initialize Pinecone
        pinecone= Pinecone(api_key=api_key)
        
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.spec = ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ) 

        # Create index if it doesn't exist
        #if index_name not in pinecone.list_indexes():
        #    pinecone.create_index(name=index_name, dimension=dimension, metric=metric,spec=self.spec)
        
        self.index = pinecone.Index(index_name)
        self.embedding_model = SentenceTransformer(embedding_model)

    def store_products(self, products):
        vectors = []
        
        for product in products:
            # Concatenate relevant fields for embedding-based search
            product_text = f"{product['name']} - {product['specifications']} - Store: {product['storefront']}"
            embedding = self.embedding_model.encode(product_text).tolist()

            # Prepare metadata, but **skip None values**
            metadata = {
                "name": product["name"],
                "image": product["image"],
                "storefront": product["storefront"]
            }

            # Add only non-null numeric fields
            if product["price"]:
                metadata["price"] = float(product["price"].replace("$", "").replace(",", ""))
            if product["stars"]:
                metadata["stars"] = float(product["stars"])
            if product["ratings"]:
                metadata["ratings"] = float(product["ratings"])
            if product["discounted_price"]:
                metadata["discounted_price"] = float(product["discounted_price"].replace("$", "").replace(",", ""))

            vectors.append((product["name"], embedding, metadata))

        self.index.upsert(vectors)
        print(f"Inserted {len(vectors)} products.")
    
    def search_products(self, query, top_k=5, price_range=None, min_stars=None, storefront=None):
        query_embedding = self.embedding_model.encode(query).tolist()
        
        filters = {}

        if price_range:  # Example: (1000, 2000)
            filters["price"] = {"$gte": price_range[0], "$lte": price_range[1]}
        
        if min_stars:
            filters["stars"] = {"$gte": min_stars}
        
        if storefront:
            filters["storefront"] = {"$eq": storefront}

        # ✅ Use keyword arguments explicitly
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filters,
            include_metadata=True
        )

        return [
            {
                "name": match["metadata"]["name"],
                "price": match["metadata"]["price"],
                "stars": match["metadata"]["stars"],
                "ratings": match["metadata"]["ratings"],
                "discounted_price": match["metadata"].get("discounted_price"),
                "image": match["metadata"]["image"],
                "storefront": match["metadata"]["storefront"],
                "score": match["score"]
            }
            for match in results["matches"]
        ]

    def reset_index(self):
        self.index.delete_index(self.index_name)
        self.index.create_index(name=self.index_name, dimension=self.dimension, metric=self.metric)
        print("Index reset.")






api_key = "pcsk_2LaRQ9_U9rUpRtm2Lv4xj2HciDUtdg43j7ncAcLp6xTagvhynBGhp6JYf5YWJB2oNPyBwv"

# Initialize RAG system
rag = PineconeRAG(api_key)

# Sample products
products = [
     {
    "name": "Samsung Galaxy S21 FE 5G Smartphone - Black",
    "price": "$699.99",
    "stars": 4,
    "ratings": 1000,
    "discounted_price": "$649.99",
    "image": "https://www.amazon.com/dp/B09BQHJY9V?th=1&psc=1",
    "specifications": "- 6.4\" FHD Display\n- Qualcomm Snapdragon 888 Processor\n- 8GB RAM and 256GB Storage\n- Triple Rear Cameras\n- IP68 Water Resistance\n- 5000mAh Battery",
    "storefront": "Amazon"
  },
  {
    "name": "Motorola Moto G Stylus (2021) - Charcoal",
    "price": "$299.99",
    "stars": 4,
    "ratings": 500,
    "discounted_price": "$279.99",
    "image": "https://www.amazon.com/dp/B08Y1TFL3P?th=1&psc=1",
    "specifications": "- 6.8\" FHD Display\n- Qualcomm Snapdragon 845 Processor\n- 4GB RAM and 64GB Storage\n- Dual Rear Cameras\n- IP68 Water Resistance\n- 4000mAh Battery",
    "storefront": "Amazon"
  }
]


#rag.store_products(products)


results = rag.search_products("Motorola")


for product in results:
    print(product)

