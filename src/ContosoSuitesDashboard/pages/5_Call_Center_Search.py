import streamlit as st
from azure.cosmos import CosmosClient
import openai

st.set_page_config(layout="wide")

def make_azure_openai_embedding_request(text):
    """Create and return a new embedding request. Key assumptions:
    - Azure OpenAI endpoint, key, and deployment name stored in Streamlit secrets."""

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    aoai_endpoint = st.secrets["aoai"]["endpoint"]
    aoai_deployment_name = st.secrets["aoai"]["embedding_deployment_name"]

    client = openai.AzureOpenAI(
        azure_ad_token_provider=token_provider,
        api_version="2024-06-01",
        azure_endpoint = aoai_endpoint
    )
    # Create and return a new embedding request
    return client.embeddings.create(
        model=aoai_deployment_name,
        input=text
    )

def make_cosmos_db_vector_search_request(query_embedding, max_results=5, minimum_similarity_score=0.5):
    """Create and return a new vector search request. Key assumptions:
    - Query embedding is a list of floats based on a search string.
    - Cosmos DB endpoint, client_id, and database name stored in Streamlit secrets."""

    cosmos_client_id = st.secrets["cosmos"]["client_id"]
    cosmos_credentials = DefaultAzureCredential(managed_identity_client_id=cosmos_client_id)

    cosmos_endpoint = st.secrets["cosmos"]["endpoint"]
    cosmos_database_name = st.secrets["cosmos"]["database_name"]
    cosmos_container_name = "CallTranscripts"

    # Create a CosmosClient
    client = CosmosClient(
        url=cosmos_endpoint,
        credential=cosmos_credentials
    )
    # Load the Cosmos database and container
    database = client.get_database_client(cosmos_database_name)
    container = database.get_container_client(cosmos_container_name)

    # Create and return a new vector search request
    results = container.query_items(
        query=f"""
            SELECT TOP {max_results}
                c.id,
                c.call_id,
                c.call_transcript,
                c.abstractive_summary,
                VectorDistance(c.request_vector, @request_vector) AS SimilarityScore
            FROM c
            WHERE
                VectorDistance(c.request_vector, @request_vector) > {minimum_similarity_score}
            ORDER BY
                VectorDistance(c.request_vector, @request_vector)
            """,
        parameters=[
            {"name": "@max_results", "value": query_embedding}
        ],
        enable_cross_partition_query=True
    )

    return results


def main():
    """Main function for the call center search dashboard."""

    st.write(
    """
    # Call Center Transcript Search

    This Streamlit dashboard is intended to support vector search as part
    of a call center monitoring solution. It is not intended to be a
    production-ready application.
    """
    )

    st.write("## Search for Text")

    query = st.text_input("Query:", key="query")
    max_results = st.number_input("Max Results:", min_value=1, max_value=10, value=5)
    minimum_similarity_score = st.slider("Minimum Similarity Score:", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    if st.button("Submit"):
        with st.spinner("Searching transcripts..."):
            if query:
                query_embedding = make_azure_openai_embedding_request(query).data[0].embedding
                response = make_cosmos_db_vector_search_request(query_embedding, max_results, minimum_similarity_score)
                for item in response:
                    st.write(item)
                st.success("Transcript search completed successfully.")
            else:
                st.warning("Please enter a query.")

if __name__ == "__main__":
    main()
