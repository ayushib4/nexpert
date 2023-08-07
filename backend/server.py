import json
import time
from typing import List, Optional
import uuid
from functools import lru_cache

from fastapi import FastAPI
from pydantic import BaseModel
import arxiv_script
from functions.top_one import top_one
from functions.expand_description_to_text import expand, expand_without_paper
from pdf_parser import pdf_url_to_text
from functions.insight_extraction import extract_key_insights
from firebase import get_firestore_client
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",  # Replace with your frontend's URL
    # Add more allowed origins if needed
]

concept_map = {}


class TopPaper(BaseModel):
    url: str
    title: str
    summary: str
    publishedDate: str


class Paper(BaseModel):
    url: str
    title: Optional[str] = ""
    summary: Optional[str] = ""
    publishedDate: Optional[str] = ""


class Query(BaseModel):
    query: str


class RetrieveArxivSearchOutput(BaseModel):
    papers: List[Paper]


class ConceptNode(BaseModel):
    name: str
    referenceUrl: str
    description: str
    referenceText: Optional[str] = ""
    id: str
    parent: Optional[str] = ""
    children: Optional[List[str]] = []


class PaperInsights(BaseModel):
    url: str
    concepts: List[ConceptNode]


class QuerySchema(BaseModel):
    query: str


class TopPaperQuerySchema(BaseModel):
    query: str
    papers: RetrieveArxivSearchOutput


class ExpandGraphWithNewInsightsSchema(BaseModel):
    id: str
    query: str
    concept: ConceptNode


class idGraphSchema(BaseModel):
    id_map: dict
    query: str
    id: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


# public-facing endpoint
@app.post("/query")
def send_query(query: Query):
    firestore_client = get_firestore_client()
    retrieve_arxiv_search(query.query)
    papers = firestore_client.read_from_document(
        collection_name="retrieval", document_name=query.query
    )
    getTopPaperInput = TopPaperQuerySchema(query=query.query, papers=papers)
    try:
        topPaper = get_top_paper(getTopPaperInput)
    except:
        topPaper = get_top_paper(getTopPaperInput)
    error = 0
    result = {"-1": dict()}

    concept_map["-1"] = ConceptNode(
        name="query", referenceUrl="", description="", id="-1"
    )

    try:
        insights = generate_insights(pdf_url=topPaper["url"])
    except Exception as e:
        insights = []
        print(f"Something went wrong generating insights: {str(e)}")
        error += 1
    if insights:
        for child_concept in insights.concepts:
            child_concept.parent = "-1"
            if child_concept.id not in result["-1"]:
                # Initialize child first
                result["-1"][child_concept.id] = {}
            child_result = result["-1"][child_concept.id]
            if child_concept.referenceUrl != topPaper["url"]:
                try:
                    child_insights = generate_insights(
                        pdf_url=child_concept.referenceUrl
                    )
                    for grandchild_concept in child_insights.concepts:
                        grandchild_concept.parent = child_concept.id
                        child_concept.children.append(grandchild_concept.id)
                        firestore_client.write_data_to_collection(
                            collection_name="graph",
                            document_name=query.query,
                            data={grandchild_concept.id: dict(grandchild_concept)},
                        )
                        if grandchild_concept.id not in child_result:
                            # Initialize grand child
                            child_result[grandchild_concept.id] = {}
                except Exception as e:
                    error += 1
                    print(f"Something went wrong adding children: {str(e)}")
                    print(e)

            firestore_client.write_data_to_collection(
                collection_name="graph",
                document_name=query.query,
                data={child_concept.id: dict(child_concept)},
            )

    hydrated_graph = hydrate_node(
        input=idGraphSchema(id="-1", query=query.query, id_map=result)
    )
    return hydrated_graph


@app.get("/hydrate-node")
def hydrate_node(input: idGraphSchema):
    def helper(cur_id, id_map):
        result_map = {}

        if cur_id == "-1":
            current_concept = None
            result_map[cur_id] = {
                "name": input.query,
                "id": "-1",
                "children": [],
                "parent": None,
                "description": None,
                "referenceUrl": None,
                "referenceText": None,
            }
        else:
            current_concept = concept_map[cur_id]
            result_map[cur_id] = {
                "name": current_concept.name,
                "id": cur_id,
                "children": [],
                "parent": current_concept.parent,
                "description": current_concept.description,
                "referenceUrl": current_concept.referenceUrl,
                "referenceText": current_concept.referenceText,
            }

        if current_concept:
            parent_concept = concept_map[current_concept.parent]
            if parent_concept.referenceUrl == current_concept.referenceUrl:
                # Don't expand children (leaf node to avoid recursion)
                return result_map[cur_id]

        children = []
        children_id_map = id_map[cur_id]
        for child_id, _ in children_id_map.items():
            children.append(helper(child_id, children_id_map))

        result_map[cur_id]["children"] = children

        return result_map[cur_id]

    return helper(input.id, input.id_map)


def retrieve_arxiv_search(query: str) -> str:
    firestore_client = get_firestore_client()
    papers = arxiv_script.search_arxiv(query)
    firestore_client.write_data_to_collection(
        collection_name="retrieval", document_name=query, data={"papers": papers}
    )
    return "Success"


@app.get("/top-paper")
def get_top_paper(input: TopPaperQuerySchema):
    firestore_client = get_firestore_client()
    result = top_one(input.papers, input.query)
    topPaper = {
        "url": result["url"],
        "title": result["title"],
        "summary": result["summary"],
        "publishedDate": result["publishDate"],
    }
    firestore_client.write_data_to_collection(
        collection_name="retrieval",
        document_name=input.query,
        data={"topPaper": topPaper},
    )
    return topPaper


def generate_insights(pdf_url: str) -> PaperInsights:
    paper_text = pdf_url_to_text(pdf_url)
    insights = extract_key_insights(paper_text)

    try:
        with open("insight_logs.txt", "a", encoding="utf-8") as f:
            f.write(json.dumps(insights) + "\n")
    except:
        pass

    references = insights["references"]
    references = {ref["bibkey"]: ref["title"] for ref in references}

    concepts = []
    for idea in insights["ideas"]:
        reference_text = ""
        relevant_references = idea["relevant_references"]
        if relevant_references:
            url = ""
            bibkey = relevant_references.pop(0)

            # Handle malformed/missing references
            if bibkey in references:
                reference_text = references[bibkey]
                # print(bibkey, reference_text)
                results = arxiv_script.search_arxiv(reference_text)
                url = results[0]["url"]
            # print(url)
        else:
            url = pdf_url
        new_uid = str(uuid.uuid4())
        new_concept = ConceptNode(
            name=idea["idea_name"],
            id=new_uid,
            referenceUrl=url,
            description=idea["description"],
            referenceText=reference_text,
        )
        concept_map[new_uid] = new_concept
        concepts.append(new_concept)
    paper_insights = PaperInsights(url=pdf_url, concepts=concepts)
    return paper_insights


@app.post("/expand-graph-with-new-nodes")
def expand_graph_with_new_nodes(
    input: ExpandGraphWithNewInsightsSchema,
):
    result = {input.id: {}}
    firestore_client = get_firestore_client()
    insights = generate_insights(pdf_url=input.concept.referenceUrl)
    for child_concept in insights.concepts:
        result[input.id][child_concept.id] = {}
        child_concept.parent = input.concept.id
        firestore_client.write_data_to_collection(
            collection_name="graph",
            document_name=input.query,
            data={child_concept.id: dict(child_concept)},
        )
    hydrated_graph = hydrate_node(
        input=idGraphSchema(id=input.id, query=input.query, id_map=result)
    )
    return hydrated_graph


@app.post("/more-info")
def more_information(concept: ConceptNode) -> str:
    url = concept.referenceUrl
    things = time.time()
    if url == "":
        return expand_without_paper(concept.description)
    else:
        print(time.time() - things)
        paper_text = pdf_url_to_text(concept.referenceUrl)
        print(time.time() - things)
        return expand(concept.description, paper_text)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
