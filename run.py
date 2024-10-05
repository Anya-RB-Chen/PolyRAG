import json
from polyrag.model.Llama3 import Llama3
from polyrag.model.PolyRAG import PolyRAG

if __name__ == "__main__":

    q = "What department does Cao Jiannong work for?"

    config = json.load(open("config.json", "r"))
    poly = PolyRAG(config)

    
    if config['model_name'] == "llama3":
        model = Llama3(config['model_dir'])
        tracker = poly.run_llm(model, q, print=True)
        context = poly.get_current_context()
    else:
        raise ValueError("Model not supported")
    
    tp = """You are a smart assistant who knows everything about PolyU. Given a question and a context, you should be able to answer the question based on the context.
    
    The context is as follows:
    {context}
    
    The question is:
    {question}
    
    Please answer the question."""

    prompt = tp.format(context=context, question=q)
    response = model.generate(prompt)
    print(response)