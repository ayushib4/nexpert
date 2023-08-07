import re


def extract_tag_content(input_string, tag):
    # Define the pattern to match the specified tag
    pattern = f"<{tag}>(.*?)</{tag}>"

    # Find all occurrences of the pattern and return them as a list
    elements = re.findall(pattern, input_string, re.DOTALL)
    elements = [element.strip() for element in elements]
    return elements


# from lxml import etree


# def extract_tag_content(xml_string, tag):
#     # Parse the XML string
#     root = etree.fromstring(xml_string)

#     # Find all occurrences of the specified tag
#     elements = root.findall(f".//{tag}")

#     # Extract the text content of each element and return it as a list
#     return [element.text for element in elements]
