class RetrieverAdapter:
    def __init__(self, retriever):
        self.retriever = retriever

    def search(
            self,
            db,
            query,
            kb_name,
            owner_id,
            top_k=5,
            filters=None,
            document_id=None,
    ):

        return self.retriever.retrieve(
            db=db,
            query=query,
            kb_name=kb_name,
            owner_id=owner_id,
            top_k=top_k,
            filters=filters,
            document_id=document_id
        )
