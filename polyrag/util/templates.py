S1_QUERY_4_SHOTS = """Given a input question, provide a SPARQL query to find the answer according to the following pre-defined schema:
Namespace: base
Class: DEPARTMENT, STAFF
Object Property: works_for
Datatype Property: has_name, has_research_interest, has_position, graduated_from, obtained_degree


Question: What department does Cao Jiannong work for?
SPARQL: '''
SELECT ?department
WHERE {{
?staff base:has_name ?name .
FILTER (contains(lcase(?name), lcase("cao jiannong")))
?staff base:works_for ?dept .
?dept rdf:type base:DEPARTMENT .
?dept rdfs:label ?department .
}}
'''

Question: What is/are the research interests of Cao Jiannong?
SPARQL: '''
SELECT ?research_interest
WHERE {{
?staff base:has_name ?name .
FILTER (contains(lcase(?name), lcase("cao jiannong")))
?staff base:has_research_interest ?research_interest .
}}
'''

Question: Who has the research interest in Coding for Business?
SPARQL: '''
SELECT ?name
WHERE {{
?staff base:has_name ?name .
?staff base:has_research_interest ?research_interest .
FILTER (contains(lcase(?research_interest), lcase("Coding for Business")))
}}
'''

Question: Which staff in AMA graduated from Hong Kong Polytechnic University?
SPARQL: '''
SELECT ?name
WHERE {{
?staff base:has_name ?name .
?staff base:works_for base:AMA .
?staff base:graduated_from ?school .
FILTER (contains(lcase(?school), lcase("Hong Kong Polytechnic University")))
}}
'''

Question: {question}
SPARQL: '''
"""

# ------------------------------------------------------------------------------

S1_QUERY_V2_4_SHOTS = """Given a input question, provide a SPARQL query to find the answer according to the following pre-defined schema:
Namespace: base
Class: DEPARTMENT, STAFF
Object Property: works_for
Datatype Property: has_name, has_research_interest, has_position, graduated_from, obtained_degree, has_published_in, has_works_in


Question: What department does Cao Jiannong work for?
SPARQL: '''
SELECT ?department
WHERE {{
?staff base:has_name ?name .
FILTER (contains(lcase(?name), lcase("cao jiannong")))
?staff base:works_for ?dept .
?dept rdf:type base:DEPARTMENT .
?dept rdfs:label ?department .
}}
'''

Question: Who has the research interest in Coding for Business?
SPARQL: '''
SELECT ?name
WHERE {{
?staff base:has_name ?name .
?staff base:has_research_interest ?research_interest .
FILTER (contains(lcase(?research_interest), lcase("Coding for Business")))
}}
'''

Question: Which staff in AMA graduated from Hong Kong Polytechnic University?
SPARQL: '''
SELECT ?name
WHERE {{
?staff base:has_name ?name .
?staff base:works_for base:AMA .
?staff base:graduated_from ?school .
FILTER (contains(lcase(?school), lcase("Hong Kong Polytechnic University")))
}}
'''

Question: What has Prof. Nancy SU published?
SPARQL: '''
SELECT ?publication
WHERE {{
?staff base:has_name ?name .
FILTER (contains(lcase(?name), lcase("Nancy SU")))
?staff base:has_published_in ?publication .
}}
'''

Question: {question}
SPARQL: '''
"""


# ------------------------------------------------------------------------------


S2_AGREEMENT_2_SHOTS = """Given a question and some information, justify whether the information is able to answer the question.

Question: What department does Cao Jiannong work for?
Information: 
Cao Jiannong is a professor.
Cao Jiannong works for the Department of Computing.
Cao Han is the head professor of the Department of Marketing and Management.
Able to answer the question: Yes

Question: What is/are the research interests of Cao Jiannong?
Information:
Cao Jiannong is a professor.
Cao Han's research interests are in Coding for Business.
Cao Jiannong has research interests.
Able to answer the question: No

Question: {question}
Information:
{information}
Able to answer the question: """


# ------------------------------------------------------------------------------

MCMORE_NO_CONTEXT_0_SHOT = """The following multiple choice questions (with all the possible correct answers) are about PolyU's academic staff:

Question: {question}
{choices}
Answer: """

MCMORE_NO_CONTEXT_2_SHOTS = """The following multiple choice questions (with all the possible correct answers) are about PolyU's academic staff:

Question: Who has research interest in "cancer therapy"?
A. Prof. Chow Ming-cheung
B. Prof. Chan Ho-yin
C. Qing Li
D. Cao Jiannong
E. Prof. Wong Wing-tak
F. Prof. Wong Ka-Leung
G. Prof. Tai Chi-shing
H. Prof. Chow Ming-cheung
Answer: A,E

Question: What department does Cao Jiannong work for?
A. AMA
B. COMP
C. APSS
D. EIE
E. CSE
F. MATH
G. IS
H. HTI
Answer: C

Question: {question}
{choices}
Answer: """

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


MCMORE_0_SHOT = """According to the information given as contexts, choose the correct answer(s) for the following multiple choice questions about PolyU's academic staff:

Context: 
'''
{context}
'''
Question: {question}
{choices}
Answer: """


# ------------------------------------------------------------------------------


MCMORE_2_SHOTS = """According to the information given as contexts for each question, choose the correct answer(s) for the following multiple choice questions about PolyU's academic staff:

Context: 
'''
Prof. Chow Ming-cheung and Prof. Wong Wing-tak are professors in the Department of Biomedical Engineering. 
Prof. Chow Ming-cheung and Prof. Wong Wing-tak have research interests in "cancer therapy".
'''
Question: Who has research interest in "cancer therapy"?
A. Prof. Chow Ming-cheung
B. Prof. Chan Ho-yin
C. Qing Li
D. Cao Jiannong
E. Prof. Wong Wing-tak
F. Prof. Wong Ka-Leung
G. Prof. Tai Chi-shing
H. Prof. Chow Ming-cheung
Answer: A,E

Context: 
'''
Prof. Cao Jiannong is a professor in the Department of Computing. 
Prof. Cao Jiannong has research interests in "Coding for Business".
'''
Question: What department does Cao Jiannong work for?
A. AMA
B. COMP
C. APSS
D. EIE
E. CSE
F. MATH
G. IS
H. HTI
Answer: C

Context: 
'''
{context}
'''
Question: {question}
{choices}
Answer: """