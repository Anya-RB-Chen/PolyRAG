import numpy as np
import os
import json
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingSearch:

    def __init__(self, vector_path, data_path, stage=2):
        self.vector_path = vector_path
        self.embeddings = np.load(vector_path)
        self.data_path = data_path
        self.data = json.load(open(data_path, "r"))
        if stage == 2:
            self.labels = [f"{x['sub']} {x['rel']} {x['obj']}" for x in self.data]
        elif stage == 3:
            self.labels = [x['text'] for x in self.data]
        else:
            raise ValueError("Invalid stage number, should be 2 or 3")

    def unload_embedding_model(self):
        del self.model

    def search_top_k(self, query, k=5, print_result=False):
        if not isinstance(self.labels, list):
            raise ValueError('Data must be a list of strings')
        if not isinstance(self.embeddings, np.ndarray):
            raise ValueError('Embeddings must be a numpy array')
        query_embedding = self.model.encode(query)
        query_embedding = query_embedding.reshape(1, -1)
        cosine_similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
        top_k_indices = np.argsort(cosine_similarities)[-k:][::-1]
        top_k_similarities = cosine_similarities[top_k_indices]
        if print_result:
            print(f"Query: {query}")
            for i, (index, sim) in enumerate(zip(top_k_indices, top_k_similarities)):
                print(f"{i+1:2d} | {self.labels[index]:30s} | {sim:.2f}")
        return [self.labels[i] for i in top_k_indices]
    
    def search_top_k_batch(self, queries, k=5, print_result=False):
        if not isinstance(self.labels, list):
            raise ValueError('Data must be a list of strings')
        if not isinstance(self.embeddings, np.ndarray):
            raise ValueError('Embeddings must be a numpy array')
        query_embeddings = self.model.encode(queries)
        cosine_similarities = cosine_similarity(query_embeddings, self.embeddings)
        top_k_indices = np.argsort(cosine_similarities, axis=1)[:, -k:][:, ::-1]
        top_k_similarities = np.array([cosine_similarities[i][top_k_indices[i]] for i in range(len(queries))])
        if print_result:
            for i, query in enumerate(queries):
                print(f"Query: {query}")
                for j, (index, sim) in enumerate(zip(top_k_indices[i], top_k_similarities[i])):
                    print(f"{j+1:2d} | {self.labels[index]:30s} | {sim:.2f}")
        return [[self.labels[i] for i in indices] for indices in top_k_indices]
    

# ------------------------------------------------------------------------------
    
if __name__ == "__main__":

    # =================================================
    k = 10
    round = 3   # 2 for KG, 3 for RAG
    benchmark_path = "benchmark_KPQA_StaffMCMore_v1.json"
    model_path = "instructor-xl"
    # =================================================

    embedding_path = "rag_staff/text_chunk.npy" if round == 3 else "kg_staff/triples_staff.npy"
    data_path = "staff_rag.json" if round == 3 else "staff_kg.json"

    benchmark_path = os.path.join(os.path.dirname(__file__), "benchmark", benchmark_path)
    model_path = os.path.join(os.path.dirname(__file__), model_path)
    embedding_path = os.path.join(os.path.dirname(__file__), "dataset_retrieval", embedding_path)
    data_path = os.path.join(os.path.dirname(__file__), "dataset", data_path)

    benchmark = json.load(open(benchmark_path, "r"))
    ids = [bench['id'] for bench in benchmark]
    questions = [bench['question'] for bench in benchmark]
    ground_truths = [bench['ground_truth'] for bench in benchmark]

    search = EmbeddingSearch(model_path, embedding_path, data_path, stage=round)
    search.load_embedding_model()
    contexts = search.search_top_k_batch(questions, k=k, print_result=True)
    search.unload_embedding_model()

    name = "KGretrieval" if round==2 else "RAGretrieval"
    context_path = os.path.join(os.path.dirname(__file__), "dataset_contexts", 
                                f"context_KPQA_StaffMCMore_v1_{name}_top{k}.json")
    with open(context_path, "w") as f:
        json.dump([{"id": i, "context": ('\n').join(c)} for i, c in zip(ids, contexts)], f, indent=4) 