def get_result_by_keys(response: dict) -> list:
    """
    Вычлениваем нужный list из полученных данных
    :param dict response: данные
    :return: list
    """
    
    response_data: dict = response.get('data', {})
    response_properties: dict = response_data.get('propertySearch', {})
    return response_properties.get('properties', [])
