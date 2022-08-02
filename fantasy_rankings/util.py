
def hyperlink(name, link=None) -> str:
    '''Generate a markdown external link based on the information provided.
    If the link is None, then the name is provided as plain text.

    :param name: Display name for the link
    :param link: External link that is used as the endpoint when the name is clicked.
    :return: string formatted for markdown
    '''
    if link is None:
        return name
    return f"[{name}]({link})"