from pdf_parser import pdf_url_to_text
from functions.insight_extraction import extract_key_insights

if __name__ == "__main__":
    attention_url = "https://arxiv.org/pdf/1706.03762.pdf"
    paper_text = pdf_url_to_text(attention_url)
    insights = extract_key_insights(paper_text)
    print(insights)
