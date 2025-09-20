from .document_reader import get_docs
from .generator import generator
from .retriever import (
    instantiate_pipeline_llama,
    retriever,
    remove_overlap_and_join,
    summarize_text,
)

import gc
import torch
from tqdm.notebook import tqdm_notebook


def restep(urls,token):
    pipe=instantiate_pipeline_llama(token)
    chunked_texts=get_docs(urls)
    retrieved_text=[]
    for text in tqdm_notebook(chunked_texts, desc="retrieving relevant texts"):
        retrieved_text.append(retriever(text, pipe))
        gc.collect()
        torch.cuda.empty_cache()
    text=remove_overlap_and_join(retrieved_text)
    summarized_retrieved_text=[]
    if len(text.split())>3300:
        for i in tqdm_notebook(retrieved_text, desc="Text too long, summarizing retrieved texts"):
            summarized_retrieved_text.append(summarize_text(i,pipe))
        text=remove_overlap_and_join(summarized_retrieved_text)
        del retrieved_text, summarized_retrieved_text
    else:
        del retrieved_text
    answer=generator(text,pipe)
    del pipe, text, chunked_texts
    gc.collect()
    torch.cuda.empty_cache()
    return(answer)    