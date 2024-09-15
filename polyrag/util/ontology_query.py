import os
import json
from rdflib import Graph, Namespace

# ignore the value error
import logging
logging.getLogger("rdflib.term").setLevel(logging.ERROR)


class OntologyQuery:

    def __init__(self, ontology_path, namespace="http://example.org/"):
        self.ontology_path = ontology_path
        self.g = Graph()
        self.g.parse(ontology_path, format="turtle")
        self.namespace = Namespace(namespace)
        self.g.bind("base", self.namespace)

    def qres_to_text(self, qres):
        res = ""
        for row in qres:
            res += f"{row}\n"
        return res
    
    def qres_to_list(self, qres):
        # convert the query result to list of values
        res = []
        for row in qres:
            res.append(row[0].value)
        return res
    
    def qres_to_context(self, qres):
        res = []
        for row in qres:
            res.append(row[0].value)
        return (','.join(res) if res else None)
    
    def query(self, query, max_result=8, return_text=False, return_list=False, return_anstext=True):
        try:
            qres = self.g.query(query, initNs={"base": self.namespace})
            if len(qres) > max_result:
                return None
            if return_text:
                return self.qres_to_text(qres)
            elif return_list:
                return self.qres_to_list(qres)
            elif return_anstext:
                return self.qres_to_context(qres)
            else:
                return qres
        except Exception as e:
            return None
        
    def get_batch_clean_query(self, llm_output_path):
        with open(llm_output_path, 'r') as f:
            data = json.load(f)
        sparql = [output['output'] for output in data]
        cleaned_query = []
        for query in sparql:
            # select the text between SELECT and '}'
            if ("SELECT" not in query) or ("}" not in query):
                cleaned_query.append(None)
                continue
            cleaned = query.split('SELECT')[1].split('}')[0]
            # add the SELECT back
            cleaned = 'SELECT ' + cleaned + '}'
            cleaned = cleaned.replace('\\', '')
            # detect the abnormal of brackets
            cleaned = cleaned.replace('?', ' ?')
            if cleaned.count('(') < cleaned.count(')'):
                cleaned = cleaned.replace(')', '', 1)
            cleaned_query.append(cleaned)
        return cleaned_query
    
    def get_batch_query_results(self, llm_output_path, max_result=8, print_result=True, 
                                return_text=False, return_list=False, return_anstext=True):
        assert sum([return_text, return_list, return_anstext]) == 1, "Only one of return_text, return_list, return_anstext can be True"
        cleaned_query = self.get_batch_clean_query(llm_output_path)
        query_results = []
        for i, q in enumerate(cleaned_query):
            results = self.query(q, max_result=max_result, 
                                 return_text=return_text, return_list=return_list, return_anstext=return_anstext)
            query_results.append(results)
            if print_result:
                print(f'Query {i+1} ', results)
        return query_results
    
    def get_clean_query(self, llm_output):
        sparql = llm_output
        if ("SELECT" not in sparql) or ("}" not in sparql):
            return None
        cleaned = sparql.split('SELECT')[1].split('}')[0]
        cleaned = 'SELECT ' + cleaned + '}'
        cleaned = cleaned.replace('\\', '')
        cleaned = cleaned.replace('?', ' ?')
        if cleaned.count('(') < cleaned.count(')'):
            cleaned = cleaned.replace(')', '', 1)
        return cleaned
    
    def get_query_result(self, llm_output, max_result=8, print_result=True, 
                         return_text=False, return_list=False, return_anstext=True):
        assert sum([return_text, return_list, return_anstext]) == 1, "Only one of return_text, return_list, return_anstext can be True"
        cleaned_query = self.get_clean_query(llm_output)
        results = self.query(cleaned_query, max_result=max_result, 
                             return_text=return_text, return_list=return_list, return_anstext=return_anstext)
        if print_result:
            print(results)
        return results



# ============================================
# Example usage
# ============================================
                
if __name__ == "__main__":
    ontology_path = os.path.join(os.path.dirname(__file__), "polyu_onto_v1.ttl")
    oq = OntologyQuery(ontology_path)


    # find the research_interest of a staff
    q = '''
    SELECT ?research_interest
    WHERE {
    ?staff base:has_name ?name .
    FILTER (contains(lcase(?name), lcase("cao jiannong")))
    ?staff base:has_research_interest ?research_interest .
    }
    '''

    # find the staff who has a particular research interest
    q = '''
    SELECT ?name
    WHERE {
    ?staff base:has_name ?name .
    ?staff base:has_research_interest ?research_interest .
    FILTER (contains(lcase(?research_interest), lcase("Coding for Business")))
    }
    '''
    
    # find all the staff from dept who graduated from particular university
    q = '''
    SELECT ?name
    WHERE {
    ?staff base:has_name ?name .
    ?staff base:works_for base:AMA .
    ?staff base:graduated_from ?school .
    FILTER (contains(lcase(?school), lcase("Hong Kong Polytechnic University")))
    }
    '''

    # find the department of a staff
    q = '''
    SELECT ?department
    WHERE {
    ?staff base:has_name ?name .
    FILTER (contains(lcase(?name), lcase("cao jiannong")))
    ?staff base:works_for ?dept .
    ?dept rdf:type base:DEPARTMENT .
    ?dept rdfs:label ?department .
    }
    '''

    print(oq.query(q, return_context=True))
    # print the result in one line
    values = []
    for row in oq.query(q, return_context=False):
        if ',' not in row[0].value:
            values.append(row[0].value)
        else:
            temp = row[0].value
            temp = temp.split(',')
            values.append(temp[0])
    print(",".join(values))
    

        
