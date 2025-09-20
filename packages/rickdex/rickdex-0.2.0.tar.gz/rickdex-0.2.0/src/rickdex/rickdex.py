import requests

base_url = "https://rickandmortyapi.com/api"

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
            resp = requests.get(self.url).json()
            return resp.get("info", [])
        except Exception as e:
            return {"error": str(e)}
    
    def get_all(self, ids: list = None) -> dict:
        """
        Returns all elements from the API or only the specified IDs.
        Examples:
            get_all()         # Returns all elements
            get_all([1, 2])   # Returns elements with IDs 1 and 2
        """
        try:
            if ids is None:
                count = Rickdex.info(self)["count"]
                ids = list(range(1, count + 1))
            return requests.get(f"{self.url}/{ids}").json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_one(self, id: int) -> dict:
        """
        Returns a single element by its ID.
        Example:
            get_one(1)   # Returns the element with ID 1
        """
        try:
            if 1 <= id <= Rickdex.info(self)["count"]:
                return requests.get(f"{self.url}/{id}").json()
            else:
                return {"error": "ID does not exist in the API"}
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
            resp = requests.get(self.url, params=params).json()
            return resp.get("results", [])
        except Exception as e:
            return {"error": str(e)}
    
    def item_filter(self, id: int, *args) -> dict:
        """
        Returns only the specified fields of an element by its ID.
        Example:
            item_filter(1, "name")   # Returns only the 'name' field of the element with ID 1
        """
        try:
            if 1 <= id <= Rickdex.info(self)["count"]:
                result = {}
                item = Rickdex.get_one(self, id)
                for key, value in item.items():
                    if key in args:
                        result[key] = value
                return result
            else:
                return {"error": "ID does not exist in the API"}
        except Exception as e:
            return {"error": str(e)}

class Character(Rickdex):
    """
    Class for operations related to characters from the Rick and Morty API.
    Inherits generic methods from Rickdex.
    """
    def __init__(self):
        url = f"{base_url}/character"
        super().__init__(url)

class Location(Rickdex):
    """
    Class for operations related to locations from the Rick and Morty API.
    Inherits generic methods from Rickdex.
    """
    def __init__(self):
        url = f"{base_url}/location"
        super().__init__(url)

class Episode(Rickdex):
    """
    Class for operations related to episodes from the Rick and Morty API.
    Inherits generic methods from Rickdex.
    """
    def __init__(self):
        url = f"{base_url}/episode"
        super().__init__(url)