def tag_wrapper(txt: str, tag: str = 'b') -> str:
    """
    Обворачивает текст тегом
    :param str txt: текст
    :param str tag: char of tag
    :return: str
    """
    
    return f'<{tag}>{txt}</{tag}>'
