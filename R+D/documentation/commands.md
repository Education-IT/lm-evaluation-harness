### Command:

``` bash
lm_eval --model hf --model_args pretrained=openai-community/openai-gpt --tasks arc_easy --device cuda:0 --batch_size auto --web_access --web_data_action load

lm_eval --model hf \
    --model_args pretrained=openai-community/openai-gpt \
    --tasks arc_easy \
    --device cuda:0 \
    --batch_size auto \
    --num_fewshot 2 
```

### Models:
* openai-community/openai-gpt
* openai-community/gpt2
* openai-community/gpt2-large
* microsoft/Phi-3.5-mini-instruct
* meta-llama/Llama-3.2-1B
* meta-llama/Llama-3.2-1B-Instruct
* meta-llama/Meta-Llama-3.1-8B
* google/gemma-2-2b
* Qwen/Qwen2.5-1.5B-Instruct

### Logs:
``` python
eval_logger.info(f"")
```