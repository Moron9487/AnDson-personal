from __future__ import annotations
from typing import TYPE_CHECKING

import json

from .anime import Anime
from .exceptions import RepeatedAnimeTitleError, WrongDatabaseError


def _version_check(raw_dict: dict):  # To be complete in the future
    if raw_dict["_edition"] != "AnDson Personal":
        raise WrongDatabaseError("the api not support the given AnDson edition")

    if raw_dict["_version"][0] != 1 or raw_dict["_version"][1] > 0 or raw_dict["_version"][2] > 0:
        raise WrongDatabaseError("the api not support the given AnDson version")

def _get_anime_name_catalog(raw_dict:dict) -> dict:
    # user will search anime object with title or alias instead of id
    anime_name_catalog = {}
    for anime_id in raw_dict["animes"]["_anime_objects"]:  #{anime-title | anime-alias: anime-id}
        anime = raw_dict["animes"]["_anime_objects"][anime_id]

        title = anime["title"]
        anime_name_catalog[title] = anime_id
        for alias in anime["aliases"]:
            anime_name_catalog[alias] = anime_id
    return anime_name_catalog
            

def _load_AnDson(file_path:str) -> dict:
    """
    load data from an existing AnDson.json to AnDson object in python
    """
    # important: An AnDson file can be load in multiple process at the same time.
    #            This api just provide a way to loading data from AnDson to python, 
    #              editing data in python and saving from python to AnDson.
    json_file = open(file_path,"r")
    raw_dict = json.load(json_file)  
    json_file.close()
    _version_check(raw_dict)
    return raw_dict


class Database:
    def __init__(self, file_path:str=None) -> None:
        """
        use Database() to create a new database object, or use Database(file_path) to load an existing AnDson file.
        """
        if file_path is None:
            raw_dict = {
                "_edition": "AnDson Personal",
                "_version": [1,0,0],
                "animes":{"_last_anime_id": 0,
                          "_anime_objects":{}}}
        else:
            raw_dict = _load_AnDson(file_path)
        self._raw_dict = raw_dict
        self.anime_name_catalog = _get_anime_name_catalog(self._raw_dict)


    @property
    def _last_anime_id(self):  #database.last_anime_id is actually a value in raw dict
        return self._raw_dict["animes"]["_last_anime_id"]

    @_last_anime_id.setter
    def _last_anime_id(self, new_value):
        self._raw_dict["animes"]["_last_anime_id"] = new_value


    def save_AnDson(self, file_path:str) -> None:
        """
        save the Database object in python with the given path.
        """
        json_file = open(file_path, "w")
        json.dump(self._raw_dict, json_file)
        json_file.close()
        return None


    def create_anime(self, title:str, aliases:tuple[str]=(), tags:tuple[str]=()) -> Anime:
        """
        `title`: The title of the anime, it must be a string.\n
        `aliases`: A tuple of aliases of the anime, each of the alias should be a string.\n
        `tags`: A tuple of tags of the anime, each of the tag should be a string.
        """
        # Checking datatype of args
        if not isinstance(title, str):
            raise TypeError("title must be a string")
        if not isinstance(aliases, (tuple)):
            raise TypeError("aliases must be a tuple of strings")
        for alias in aliases:
            if not isinstance(alias, str):
                raise TypeError("aliases must be a tuple of strings")
        if not isinstance(tags, (tuple)):
            raise TypeError("tags must be a tuple of strings")
        for tag in tags:
            if not isinstance(tag, str):
                raise TypeError("tags must be a tuple of strings")


        # Checking whether the inputed title and aliases unique or not
        aliases = set(aliases) # aliases can't repeated
        if title in aliases:
            err_msg = f"Anime title can't be one of the aliases Alases should be unique"
            raise RepeatedAnimeTitleError(err_msg)
        if title in self.anime_name_catalog:
            err_msg = f"Anime title and Alases should be unique, the title of the new anime '{title}' has exist in the database."
            raise RepeatedAnimeTitleError(err_msg)
        for alias in aliases:
            if alias in self.anime_name_catalog:
                err_msg = f"Anime title and Alases should be unique, the alias of the new anime '{alias}' has exist in the database."
                raise RepeatedAnimeTitleError(err_msg)


        # Adding anime object into database
        new_anime_object = {
            "_class": "Anime",
            "title": title,
            "aliases": list(aliases),
            "tags": list(tags),
            "views": {"_last_view_id": 0,
                      "_view_objects": {}}}
        self._last_anime_id += 1
        self._raw_dict["animes"]["_anime_objects"][self._last_anime_id] = new_anime_object

        # Register anime title and aliases to the anime_name_catalog
        self.anime_name_catalog[title] = self._last_anime_id
        for alias in aliases:
            self.anime_name_catalog[alias] = self._last_anime_id
        
        #return Anime instance
        return Anime(self, self._last_anime_id)

    def get_anime(self, name:str) -> Anime|None:
        """
        "name" can be title or alias \n
        Returns an Anime instance if the name is in the database, otherwise, returns None.
        """
        if name in self.anime_name_catalog:
            return Anime(self, self.anime_name_catalog[name])
        else:
            return None

    def get_all_animes(self) -> tuple[Anime]:
        """
        Returns a tuple of all animes in the database
        """
        rtn = tuple(Anime(self,anime_id) for anime_id in self._raw_dict["animes"]["_anime_objects"])
        return rtn

    def clear_anime(self) -> None:
        """
        remove all anime data in the Database object.
        """
        # hint: last_anime_id will not reset.
        self.anime_name_catalog = {}
        self._raw_dict["animes"]["_anime_objects"] = {}