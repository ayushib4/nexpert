from functools import lru_cache

import arxiv


@lru_cache(maxsize=1000)
def search_arxiv(query, numRecentPapers=5, numMostCitedPapers=5):
    searchRelevance = arxiv.Search(
        query=query,
        max_results=5,
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending,
    )
    searchDate = arxiv.Search(
        query=query,
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    papers = []

    for result in searchRelevance.results():
        papers.append(
            {
                "title": result.title,
                "summary": result.summary,
                "url": result.pdf_url,
                "publishedDate": str(result.published),
            }
        )
    for result in searchDate.results():
        papers.append(
            {
                "title": result.title,
                "summary": result.summary,
                "url": result.pdf_url,
                "publishedDate": str(result.published),
            }
        )
    # papers =
    return papers
