from functools import lru_cache

from claude import Claude


def top_one(retrieval_arxiv_output, user_query):
    papers = [dict(paper) for paper in retrieval_arxiv_output.papers]
    papers_str = str(papers)
    return top_one_(papers_str, user_query)


@lru_cache(maxsize=1000)
def top_one_(paper_list_string, user_query):
    top_one = Claude()
    topPaper = top_one(
        f"""I have a set of papers. I also have a query string from a user trying to figure out which paper is most relevant for them. The papers are in the following format:

    {{

    title: "Title"

    summary: "Summary"

    url: "url"

    publishDate: "date"

    }}

    Please return the paper that is the most relevant to the users query. Return the paper that is most relevant. Wrap the returned JSON in <response></response> tags. Prioritize papers that are more relevant, more informative, and more recent.

    The list of papers is:
    {
        paper_list_string
    }
    
    The user query string is:
    {
        user_query
    }

    The final format of your output should be:
    <response>
        <title> (TITLE OF THE SELECTED PAPER) </title>
        <summary> (SUMMARY OF SELECTED PAPER) </summary>
        <url> (URL OF THE SELECTED PAPER) </url>
        <publishdate> (PUBLISH DATE OF THE SELECTED PAPER) </publishdate>
    </response>
    """
    )
    # print(topPaper)
    # response = topPaper.split("<response>")[1].split("</response>")[0].replace("'", "\"")
    # print(response)

    try:
        title = topPaper.split("<title>")[1].split("</title>")[0].replace("'", '"')
    except:
        title = "Nothing"
    try:
        summary = (
            topPaper.split("<summary>")[1].split("</summary>")[0].replace("'", '"')
        )
    except:
        summary = "Nothing"
    try:
        url = topPaper.split("<url>")[1].split("</url>")[0].replace("'", '"')
    except:
        raise ValueError("Top paper could not be parsed")
        # url="https://arxiv.org/pdf/2307.04355.pdf"
    try:
        date = (
            topPaper.split("<publishdate>")[1]
            .split("</pulishdate>")[0]
            .replace("'", '"')
        )
    except:
        date = "1900-02-23"
    objectToBuild = {
        "title": title,
        "summary": summary,
        "url": url,
        "publishDate": date,
    }
    return objectToBuild
