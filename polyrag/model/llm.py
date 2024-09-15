import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM

class Llama3:
    def __init__(self,model_dir) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        eot = "<|eot_id|>"
        eot_id = self.tokenizer.convert_tokens_to_ids(eot)
        self.tokenizer.pad_token = eot
        self.tokenizer.pad_token_id = eot_id

        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            torch_dtype=torch.float16,
            device_map='auto'
        )
        self.model.config.eos_token = eot
        self.model.config.eos_token_id = eot_id
    
    def get_prompt(self, message: str, chat_history: list[tuple[str, str]],
               system_prompt: str) -> str:
        """
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>

        {{ system_prompt }}<|eot_id|><|start_header_id|>user<|end_header_id|>

        {{ user_msg_1 }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

        {{ model_answer_1 }}<|eot_id|>
        """
        texts = [f'<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n']
        # The first user input is _not_ stripped
        do_strip = False
        for user_input, response in chat_history:
            user_input = user_input.strip() if do_strip else user_input
            do_strip = True
            texts.append(f'{user_input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n{response.strip()}<|eot_id|>\n\n')
        message = message.strip() if do_strip else message
        texts.append(f'{message}<|eot_id|>')
        return ''.join(texts)

    def generate(self, text, temperature=0.7, system="You are a chatbot who gives helpful, detailed, and precise answers to the user's questions.", top_p=0.8, max_new_tokens=256):
        query = self.get_prompt(text, [], system)

        inputs = self.tokenizer(query, return_tensors="pt", add_special_tokens=False,return_token_type_ids=False)
        for k in inputs:
            inputs[k] = inputs[k].cuda()

        outputs = self.model.generate(**inputs, do_sample=True, temperature=temperature, top_p=top_p, max_length=max_new_tokens + inputs['input_ids'].size(-1))
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        return response, query