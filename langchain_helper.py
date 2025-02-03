from langchain_community.llms import GooglePalm
from langchain_community.llms import HuggingFaceHub
from langchain.llms import Cohere
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import SemanticSimilarityExampleSelector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import FewShotPromptTemplate
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX, _mysql_prompt
from langchain.prompts.prompt import PromptTemplate
# from sentence_transformers import SentenceTransformer
from few_shots import few_shots

import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env (especially openai api key)


def get_few_shot_db_chain():
    db_user = "root"
    db_password = "sree2003"
    db_host = "localhost"
    db_name = "shoe_stocks_chatbot"

    db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
                              sample_rows_in_table_info=3)
    table_info=db.table_info

    print("Tables in database:",db.get_usable_table_names())


    llm = HuggingFaceHub(
        repo_id="tiiuae/falcon-7b-instruct",  # or other suitable models
        huggingfacehub_api_token="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",  # free token from HuggingFace
        model_kwargs={"temperature": 0.1}
    )

    #llm = GooglePalm(google_api_key=os.environ["GOOGLE_API_KEY"], temperature=0.1)
    print("LLM",llm)
    print("Few shots data:", few_shots[:2])  # Print first 2 examples

    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

    print("Embeddings model loaded successfully")

    to_vectorize = [" ".join(example.values()) for example in few_shots]
    print("First text to vectorize:", to_vectorize[0])

    vectorstore = Chroma.from_texts(to_vectorize, embeddings, metadatas=few_shots, persist_directory="./chroma_db" )
    print("Collection name:", vectorstore._collection.name)
    print("Number of documents:", vectorstore._collection.count())

    example_selector = SemanticSimilarityExampleSelector(
        vectorstore=vectorstore,
        k=2,
    )

    mysql_prompt = """You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer to the input question.
        Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per MySQL. You can order the results to return the most informative data in the database.
        Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
        Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
        Pay attention to use CURDATE() function to get the current date, if the question involves "today".

        Use the following format:

        Question: Question here
        SQLQuery: Query to run with no pre-amble
        SQLResult: Result of the SQLQuery
        Answer: Final answer here


        """
    top_k=2
    example_prompt = PromptTemplate(
        input_variables=["Question", "SQLQuery", "SQLResult", "Answer", ],
        template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",
    )

    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=mysql_prompt,
        suffix=PROMPT_SUFFIX,
        input_variables=["input", "table_info", "top_k"],  # These variables are used in the prefix and suffix
    )
    chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, prompt=few_shot_prompt)
    print("CHAIN",chain)
    return chain
