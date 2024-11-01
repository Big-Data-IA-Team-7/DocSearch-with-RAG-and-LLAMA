from llama_parse import LlamaParse
from llama_index.core.schema import TextNode
import re
from pathlib import Path
import os
from llama_index.core import (
    StorageContext,
    SummaryIndex,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.llms.openai import OpenAI
from fast_api.schemas.report_schema import ReportOutput, system_prompt
import logging
import nest_asyncio
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

nest_asyncio.apply()


def get_page_number(file_name):
    match = re.search(r"-page-(\d+)\.jpg$", str(file_name))
    if match:
        return int(match.group(1))
    return 0

def _get_sorted_image_files(image_dir):
    """Get image files sorted by page."""
    raw_files = [f for f in list(Path(image_dir).iterdir()) if f.is_file()]
    sorted_files = sorted(raw_files, key=get_page_number)
    return sorted_files

def get_text_nodes(json_dicts, image_dir=None):
    """Split docs into nodes, by separator."""
    nodes = []

    image_files = _get_sorted_image_files(image_dir) if image_dir is not None else None
    md_texts = [d["md"] for d in json_dicts]

    for idx, md_text in enumerate(md_texts):
        chunk_metadata = {"page_num": idx + 1}
        if image_files is not None and idx < len(image_files):
            image_file = image_files[idx]
            chunk_metadata["image_path"] = str(image_file)
        chunk_metadata["parsed_text_markdown"] = md_text
        node = TextNode(
            text="",
            metadata=chunk_metadata,
        )
        nodes.append(node)

    return nodes

def report_generate(file_path, user_query, file_name):

    embed_model = OpenAIEmbedding(model="text-embedding-3-large")
    llm = OpenAI(model="gpt-4o")

    Settings.embed_model = embed_model
    Settings.llm = llm

    parser = LlamaParse(
        result_type="markdown",
        use_vendor_multimodal_model=True,
        vendor_multimodal_model_name="anthropic-sonnet-3.5",
    )

    image_dir = f"data_images_{file_name}"

    os.makedirs(image_dir, exist_ok=True)

    md_json_objs = parser.get_json_result(file_path)
    md_json_list = md_json_objs[0]["pages"]
    image_dicts = parser.get_images(md_json_objs, download_path=image_dir)

    text_nodes = get_text_nodes(md_json_list, image_dir=image_dir)

    if not os.path.exists(f"storage_nodes_summary{file_name}"):
        index = VectorStoreIndex(text_nodes)
        # save index to disk
        index.set_index_id(f"summary_{file_name}")
        index.storage_context.persist(f"./storage_nodes_summary_{file_name}")
    else:
        # rebuild storage context
        storage_context = StorageContext.from_defaults(persist_dir=f"storage_nodes_summary_{file_name}")
        # load index
        index = load_index_from_storage(storage_context, index_id=f"summary_index_{file_name}")

    llm = OpenAI(model="gpt-4o", system_prompt=system_prompt)
    sllm = llm.as_structured_llm(output_cls=ReportOutput)

    query_engine = index.as_query_engine(
        similarity_top_k=5,
        llm=sllm,
        response_mode="compact",
    )

    response = query_engine.query(user_query)

    return response.response