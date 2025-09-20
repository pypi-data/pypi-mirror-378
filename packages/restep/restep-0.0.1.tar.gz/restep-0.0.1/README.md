# RESTEP

**R**eason-based RAG for **E**arly-**St**ag**e** Developers for Community-based **P**rospecting (**RE-STEP**) is a GenAI prospecting tool to assess community-based factors in early-stage renewable-energy siting. It is targeted for early-stage developers in the renewable energy industry.



## Requirements  
### Required packages


The following packages are required for `restep`:

- `torch` (to learn how to install, please refer to [pytorch.org](https://pytorch.org/))
- `transformers`
- `accelerate`
- `safetensors`
- `sentencepiece`
- `bitsandbytes`
- `requests`
- `PyPDF2`
- `python-docx`
- `langchain`
- `tqdm`

To install these packages, you can do the following:

```bash
pip install torch transformers accelerate safetensors sentencepiece bitsandbytes requests PyPDF2 python-docx langchain tqdm
```

### GPU requirements
You require at least one GPU to use `restep`.  
VRAM requirements depend on factors like the length of the document.  
However, at least 16GB of VRAM is recommended

### huggingface access token
You will need a huggingface access token. To obtain one:  
1. you'd first need to create a [huggingface](https://huggingface.co) account if you do not have one. 
2. Create and store a new access token. To learn more, please refer to [huggingface.co/docs/hub/en/security-tokens](https://huggingface.co/docs/hub/en/security-tokens).  
3. Note: Some pre-trained large language models (LLMs) may require permissions. For more information, please refer to [huggingface.co/docs/hub/en/models-gated](https://huggingface.co/docs/hub/en/models-gated).  
4. Request for permission for `meta-llama/Llama-3.1-8B-Instruct` at https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct. 



## Installation
To install in python, simply do the following: 
```bash
pip install restep
```


## Quick Start

Here we provide a quick example on how you can execute `restep` by providing a link to the local government document and your huggingface API key. 
```python
from restep import restep
api_key="<your huggingface API key>"
url_to_local_government_document"https://www.co.marshall.in.us/egov/documents/1739816106_82896.pdf"
print(restep(url_to_local_government_document,api_key))

# This will return: {"Sentiment": "NEGATIVE", "Summary": "Opposition from residents and board members, citing concerns over property values, wildlife, and agricultural land, with some board members questioning the project's compliance with the ordinance and requesting additional conditions."}
```

## How does RE-STEP work?

![Figure](Figure.jpg)


Our paper is currently under review at ACM BuildSys '25. Stay-tuned for updates if you are curious for more details. 