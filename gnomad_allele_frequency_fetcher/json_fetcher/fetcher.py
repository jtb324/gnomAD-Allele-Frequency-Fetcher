import requests


def fetch(jsondata):
    """function to fetch a json response from graphql
    Parameters
    __________
    jsondata
        dictionary contain the query parameters

    Returns
    _______
    json
        returns a json object containing the query parameters
    int
        if the program encounters an error then it will return -1
    """
    gnomad_website: str = "https://gnomad.broadinstitute.org/api"
    headers: dict = {"Content-Type": "application/json"}
    response = requests.post(gnomad_website, json=jsondata, headers=headers)
    json = response.json()
    if "errors" in json:

        # raise Exception(str(json["errors"]))
        return -1
    return json
