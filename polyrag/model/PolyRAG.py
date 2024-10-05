import json
import os
from polyrag.model.llm import Llama3
from polyrag.util.ontology_query import OntologyQuery
from polyrag.util.retrieval_tracker import RetrievalTracker
from polyrag.util.embedding_search import EmbeddingSearch
import polyrag.util.templates as tp

class PolyRAG:
    def __init__(self, config):
        self.config = config

        self.poly = config['poly']
        self.model_name = config['model_name']
        self.tracker_dir = config['tracker_dir']
        self.tracker_file = f"tracker_{self.model_name}_{self.poly}.json"
        self.tracker_path = os.path.join(self.tracker_dir, self.tracker_file)
        self.tracker = RetrievalTracker(self.tracker_path)

        self.ontology_path = config['ontology_path']
        self.onto = OntologyQuery(self.ontology_path)
        self.s2k = config['s2k']
        self.kg_es = EmbeddingSearch(config['kg_embed_path'], config['kg_path'], stage=2)
        self.s3k = config['s3k']
        self.rag_es = EmbeddingSearch(config['rag_embed_path'], config['rag_path'], stage=3)

    def _s1_sparql_prompt(self, question):
        template = tp.S1_QUERY_V2_4_SHOTS
        prompt = template.format(question=question)
        return prompt
    
    def _s1_query_result(self, output):
        s1_result = self.onto.get_query_result(output, max_result=10)
        return s1_result
    
    def _s2_kg_agreement_prompt(self, question):
        self.kg_context = self.kg_es.search_top_k(question, k=self.s2k)
        template = tp.S2_AGREEMENT_2_SHOTS
        prompt = template.format(question=question, information=['\n'.join(self.kg_context)])
        return prompt
    
    def _s2_agreement_result(self, output):
        return True if "Yes" in output else False
    
    def _s3_rag_context(self, question):
        self.rag_context = self.rag_es.search_top_k(question, k=self.s3k)
        return self.rag_context
    
    def run_llm(self, model, question, print=False):

        self.llm = model
        s1_result = None
        s2_result = None
        s3_context = None
        self.kg_context = None

        if "s1" in self.poly:
            s1_prompt = self._s1_sparql_prompt(question)
            s1_output, s1_query = self.llm.generate(s1_prompt)
            s1_result = self._s1_query_result(s1_output)
            if print:
                print("====== S1 SECTION ======") 
                print("S1 Prompt:", s1_query)
                print("S1 Output:", s1_output)

        if "s2" in self.poly:
            s2_prompt = self._s2_kg_agreement_prompt(question)
            s2_output, s2_query = self.llm.generate(s2_prompt)
            s2_result = self._s2_agreement_result(s2_output)
            if print:
                print("====== S2 SECTION ======") 
                print("S2 Prompt:", s2_query)
                print("S2 Context:", self.kg_context)
                print("S2 Output:", s2_output)
                print("S2 Agreement:", s2_result)

        if "s3" in self.poly:
            s3_context = self._s3_rag_context(question)

        self.tracker.update_tracker(question, s1_result, self.kg_context, s2_result, s3_context, save=True)

        if print:
            print("====== POLYRAG SUMMARY ======")
            print(f"Question: {question}")
            print(f"S1 SPARQL Query: {s1_output}")
            print(f"S1 SPARQL Result: {s1_result}")
            print(f"S2 KG Context: {self.kg_context}")
            print(f"S2 KG Agreement: {s2_result}")
            print(f"S3 RAG Context: {s3_context}")

        return self.tracker
    
    def get_current_context(self):
        return self.tracker[-1]['context']
    

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    q = "What department does Cao Jiannong work for?"

    config = json.load(open("../config/conf.json", "r"))
    poly = PolyRAG(config)

    
    if config['model_name'] == "llama3":
        model = Llama3(config['model_dir'])
        tracker = poly.run_llm(model, q, print=True)
        context = poly.get_current_context()
    else:
        raise ValueError("Model not supported")