from functools import lru_cache

from anthropic import AI_PROMPT

from claude import Claude
from xml_parser import extract_tag_content


def parse_insights(insights_text: str) -> dict:
    output = {}
    [references] = extract_tag_content(insights_text, tag="references")
    references = extract_tag_content(insights_text, tag="bibitem")
    reference_list = []
    for ref in references:
        [bibkey] = extract_tag_content(ref, tag="bibkey")
        bibkey = bibkey.strip()
        bibkey = bibkey.strip("\n")
        bibkey = bibkey.strip("\\n")
        bibkey = bibkey.strip()
        [reference_text] = extract_tag_content(ref, tag="reference_text")
        [title] = extract_tag_content(ref, tag="title")
        reference_list.append(
            {"bibkey": bibkey, "reference_text": reference_text, "title": title}
        )
    output["references"] = reference_list
    new_ideas = extract_tag_content(insights_text, tag="novel_idea")
    idea_list = []
    for idea in new_ideas:
        [idea_name] = extract_tag_content(idea, tag="idea_name")
        [description] = extract_tag_content(idea, tag="description")
        idea_list.append(
            {
                "idea_name": idea_name,
                "description": description,
                "relevant_references": [],
            }
        )
    previous_work_ideas = extract_tag_content(insights_text, tag="previous_work_idea")
    for idea in previous_work_ideas:
        [idea_name] = extract_tag_content(idea, tag="idea_name")
        [description] = extract_tag_content(idea, tag="description")
        relevant_references = extract_tag_content(idea, tag="relevant_references")
        relevant_references = [
            extract_tag_content(ref, tag="bibkey")[0]
            .strip()
            .strip("\n")
            .strip("\\n")
            .strip()
            for ref in relevant_references
        ]
        idea_list.append(
            {
                "idea_name": idea_name,
                "description": description,
                "relevant_references": relevant_references,
            }
        )
    output["ideas"] = idea_list
    return output


@lru_cache(maxsize=1000)
def extract_key_insights(paper_text: str) -> dict:
    prompt = f"""List the most important ideas in the paper separate totally novel ideas
    from those that build upon previous work (both are VERY important) and then output the list of ideas in the following format:
    <references>
        <bibitem>
            <bibkey>
                # Bibtext friendly ID
            </bibkey>
            <title>
                # TITLE of the reference paper
            </title>
            <reference_text>
                # APA formatted reference
            </reference_text>
        </bibitem>
    </references>
    <previous_work_idea>
        <idea_name>
            # A 3-4 word name for the idea
        </idea_name>
        <description>
            # Description of the idea
        </description>
        <relevant_references>
            <bibkey>
                # Bibkey ID of relevant reference
            </bibkey>
            ...
            <bibkey>
            ...
            </bibkey>
        </relevant_references>
    </previous_work_idea>
    ...
    <previous_work_idea>
    ...
    </previous_work_idea>
    <novel_idea>
        <idea_name>
            # A 3-4 word name for the idea
        </idea_name>
        <description>
            # Description of the idea
        </description>
    </novel_idea>
    ...
    <novel_idea>
        ...
    </novel_idea>
    === Paper text ===
    {paper_text}

    Aim for 4-6 previous work ideas and 2-3 novel ideas.

    {AI_PROMPT} I have identified the paper's title and authors and will ignore it, beyond that, these are the most important references from previous work:
    """
    insights = Claude()(prompt, output_role_or_suffix="")

    try:
        with open("claude_insights_logs.txt", "a", encoding="utf-8") as f:
            f.write(insights + "\n")
    except:
        pass

    try:
        parsed_insights = parse_insights(insights)
    except Exception as e:
        print(f"Failed with:\n{insights}")
        raise e
    # print(parsed_insights)
    return parsed_insights
