from functions.insight_extraction import extract_key_insights
from pdf_parser import pdf_url_to_text
import json
import arxiv_script
import uuid
from externalTools.scihub import SciHub

pdf_url = "https://arxiv.org/pdf/2307.12008.pdf"

paper_text = pdf_url_to_text(pdf_url)
insights = extract_key_insights(paper_text)

# sh = SciHub()

references = insights["references"]
references = {ref["bibkey"]: ref["title"] for ref in references}

concepts = []
for idea in insights["ideas"]:
    relevant_references = idea["relevant_references"]
    # print()
    # print(relevant_references)
    # print()
    if relevant_references:
        url = ""
        # while relevant_references and not url:
        bibkey = relevant_references.pop(0)
        reference_text = references[bibkey]
        print(bibkey, reference_text)
        # results = sh.search(reference_text, 1)
        # print(results)
        # print()
        results = arxiv_script.search_arxiv(reference_text)
        url = results[0]["url"]
        print(url)
        # if len(results["papers"]) != 0:
        #     print(results["papers"][0]["pdf"])
        # else:
        #     print(bibkey, "skip")
        # if "arxiv" in reference_text.lower():
        #     top_results = arxiv_script.search_arxiv(reference_text)
        #     # print(
        #     #     "=== REF ===\n",
        #     #     reference_text,
        #     #     "=== ARXIV RESULTS ===\n",
        #     #     top_results,
        #     # )
        #     url = top_results[0]["url"]
        #     break
        # else:
        #     # print("Skip: ", reference_text)
        #     pass
    else:
        url = pdf_url
    concepts.append(
        {
            "name": idea["idea_name"],
            "id": str(uuid.uuid4()),
            "referenceUrl": url,
            "description": idea["description"]
        }
    )
print(json.dumps(concepts, indent=2))