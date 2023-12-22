from langchain.chains.openai_functions import create_structured_output_chain
from langchain.callbacks import get_openai_callback
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

from model_to_extract import ReqModel


async def use_chain(input_: str, file: str):

    model = ChatOpenAI(temperature=0, model='gpt-3.5-turbo')
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a world class algorithm for extracting information in structured formats."),
        ("human", "Use the given format to extract information from the following text: {input}"),
        ("human", "Tip: Make sure to answer in the correct format and all properties encolsed in double quotes"
                  "and all dates in format '%d.%m.%Y'"),
    ])
    chain = create_structured_output_chain(ReqModel, model, prompt)
    with get_openai_callback() as cb:
        try:
            result = await chain.arun(input_)
        except Exception as er:
            print(er)
            return
        print(f"Call cost (USD) {cb.total_cost}$")

    return result
