import requests
import math

def get_citation_count(doi):
    """
    Retrieves the number of citations for a given DOI using the OpenCitations API.

    Parameters:
        doi (str): The Digital Object Identifier of the paper.

    Returns:
        int or float: The number of citations as an integer, or NaN if the DOI is invalid.
    """
    url = f"https://opencitations.net/index/api/v1/citation-count/{doi}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data and 'count' in data[0]:
            return int(data[0]['count'])
        else:
            return float('nan')
    except (requests.exceptions.RequestException, ValueError, IndexError, KeyError):
        return float('nan')

