from pydantic import BaseModel, Field
from typing import List, Union
import streamlit as st
from PIL import Image

system_prompt = """\
You are a report generation assistant tasked with producing a well-formatted context given parsed context.

You will be given context from one or more reports that take the form of parsed text.

You are responsible for producing a report with interleaving text and images - in the format of interleaving text and "image" blocks.
Since you cannot directly produce an image, the image block takes in a file path - you should write in the file path of the image instead.

How do you know which image to generate? Each context chunk will contain metadata including an image render of the source chunk, given as a file path. 
Include ONLY the images from the chunks that have heavy visual elements (you can get a hint of this if the parsed text contains a lot of tables).
When the text talks about charts, you MUST obtain the chart (image block) associated with the text and You MUST include at least one image block in the output. 

You MUST output your response as a tool call in order to adhere to the required output format. Do NOT give back normal text.

"""

class TextBlock(BaseModel):
    """Text block."""
    text: str = Field(description="The text for this block.")

class ImageBlock(BaseModel):
    """Image block."""
    file_path: str = Field(description="File path to the image.")

class ReportOutput(BaseModel):
    """Data model for a report.

    Can contain a mix of text and image blocks. MUST contain at least one image block.
    """
    blocks: List[Union[TextBlock, ImageBlock]] = Field(
        description="A list of text and image blocks."
    )