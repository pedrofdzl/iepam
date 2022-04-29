def get_iframe_url(url: str) -> str:
    """
    Gets the url for embeded iframe base on the youtube link

    params url(str): A string containing the url

    returns str: a string with the url ready to use in iframe
    """

    result = 'https://www.youtube.com/embed/'
      
    if 'youtu.be' in url:
        video_code = url[17:]
        return result + video_code
    elif 'youtube.com' in url:
        query_params = url.split('?')[1]
        query_params = query_params.split('v=')[1]
        code = query_params.split('&')[0]
        return result + code