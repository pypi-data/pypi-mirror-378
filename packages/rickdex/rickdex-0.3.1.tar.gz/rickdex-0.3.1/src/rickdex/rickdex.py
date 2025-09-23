import requests

BASE_URL = "https://rickandmortyapi.com/api"

class Rickdex:
    """
    Base class for interacting with the Rick and Morty API.
    Provides generic methods for retrieving information, fetching items,
    filtering, and extracting specific fields from API resources.
    """
    def __init__(self, url):
        self.url = url

    def info(self) -> dict:
        """
        Returns general information about the API resource.
        Example: total count, number of pages, etc.
        """
        try:
            resp = requests.get(self.url, timeout=(2, 5)).json()
            return resp.get("info", [])
        except Exception as e:
            return {"error": str(e)}
    
    def get_all(self, ids: list = None) -> list:
        """
        Returns all elements from the API or only the specified IDs.
        Examples:
            get_all()         # Returns all elements
            get_all([1, 2])   # Returns elements with IDs 1 and 2
        """
        try:
            if ids is None:
                with requests.Session() as session:
                    result = []
                    page = 1
                    pages = session.get(self.url, timeout=(2, 5)).json()["info"]["pages"]
                    while page <= pages:
                        params = {"page": page}
                        resp = session.get(self.url, params=params, timeout=(2, 10)).json()
                        result.append(resp.get("results", []))
                        page += 1
                    return result
            else:
                return requests.get(f"{self.url}/{ids}", timeout=(2, 10)).json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_one(self, id: int) -> dict:
        """
        Returns a single element by its ID.
        Example:
            get_one(1)   # Returns the element with ID 1
        """
        try:
            return requests.get(f"{self.url}/{id}", timeout=(2, 5)).json()
        except Exception as e:
            return {"error": str(e)}
    
    def api_filter(self, **kwargs) -> dict:
        """
        Returns elements from the API according to the provided filters.
        Example:
            api_filter(name="rick")   # Returns all elements with 'rick' in the name
        """
        try:
            parameters = ["name", "status", "species", "type", "gender", "dimension", "episode"]
            params = {}
            for key, value in kwargs.items():
                if key in parameters:
                    params[key] = value
            resp = requests.get(self.url, params=params, timeout=(2, 5)).json()
            return resp.get("results", [])
        except Exception as e:
            return {"error": str(e)}
    
    def item_filter(self, id: int | list, *args) -> dict:
        """
        Returns only the specified fields of an element (or elements) by its ID (or IDs).
        Examples:
            item_filter(1, "name")             # Returns only the 'name' field of the element with ID 1
            item_filter([1, 2], "name", "status") # Returns 'name' and 'status' fields for elements with IDs 1 and 2
        """
        try:
            if isinstance(id, int):
                result = {}
                element = self.get_one(id)
                for key in args:
                    result[key] = element.get(key)
                return result
            if isinstance(id, list):
                result = []
                elements = self.get_all(id)
                index = 0
                while index <= len(id) - 1:
                    tempDict = {}
                    for key in args:
                        tempDict[key] = elements[index].get(key)
                    result.append(tempDict)
                    index += 1
                return result
        except Exception as e:
            return {"error": str(e)}

class Character(Rickdex):
    """
    Class for operations related to characters from the Rick and Morty API.
    Inherits generic methods from Rickdex.
    """
    def __init__(self):
        url = f"{BASE_URL}/character"
        super().__init__(url)

class Location(Rickdex):
    """
    Class for operations related to locations from the Rick and Morty API.
    Inherits generic methods from Rickdex.
    """
    def __init__(self):
        url = f"{BASE_URL}/location"
        super().__init__(url)

class Episode(Rickdex):
    """
    Class for operations related to episodes from the Rick and Morty API.
    Inherits generic methods from Rickdex.
    """
    def __init__(self):
        url = f"{BASE_URL}/episode"
        super().__init__(url)