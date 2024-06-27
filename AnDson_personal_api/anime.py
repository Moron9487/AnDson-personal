from __future__ import annotations
from typing import TYPE_CHECKING

from .exceptions import AnimeRemovedError, RepeatedAnimeTitleError
if TYPE_CHECKING:
    from .database import Database


class Anime:

    # warning: Using AnimeDatabasePersonal.get_anime(title|alias) to get an Anime instance may be a better choice
    #            rather than using Anime(database, anime_id) directly.
    # important: Anime instance is just an object-like interaction interface.
    #            In fact, the data are stored in the database. 
    #            Therefore, an Anime instance will exist even though it has been removed in the database.
    #            It's important to return an error message when somebody uses method of Anime instance but the
    #              data is actually removed in the database.
    def __init__(self, database:Database, anime_id:int) -> None:
        self._database = database
        self._id = anime_id

        self._anime_data = self._database._raw_dict["animes"][anime_id]

    def _checking_existence(self) -> None:
        if self._id not in self._database._raw_dict["animes"]:
            raise AnimeRemovedError
    

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Anime):
            return False
        if self._database is not value._database:
            return False
        return self._id == value._id
    
    def __hash__(self) -> int:
        return hash((id(self._database), self._id))


    @property
    def title(self) -> str:
        self._checking_existence()
        return self._anime_data["title"]
    
    @title.setter
    def title(self, new_title:str):
        self._checking_existence()
        if not isinstance(new_title, str):
            raise TypeError("title must be a string")
        
        old_title = self.title
        if old_title == new_title:  # if the new title is same as the old one, do nothing.
            return None
        if new_title in self._database.anime_name_catalog:
            err_msg = f"Anime title and Alases should be unique, the new title '{new_title}' has existed in the database."
            raise RepeatedAnimeTitleError(err_msg)
        
        self._anime_data["title"] = new_title
        self._database.anime_name_catalog.pop(old_title)
        self._database.anime_name_catalog[new_title] = self._id


    @property
    def aliases(self) -> tuple:
        self._checking_existence()
        return tuple(self._anime_data["aliases"])
    
    @aliases.setter
    def aliases(self, new_aliases:tuple[str]):
        self._checking_existence()
        if not isinstance(new_aliases, (tuple)):
            raise TypeError("aliases must be a tuple of strings")
        for new_alias in new_aliases:
            if not isinstance(new_alias, str):
                raise TypeError("aliases must be a tuple of strings")
        
        old_aliases = self.aliases
        new_aliases = set(new_aliases) # aliases can't repeated
        if self.title in new_aliases:
            err_msg = f"Anime title can't be one of the aliases Alases should be unique"
            raise RepeatedAnimeTitleError(err_msg)
        for new_alias in new_aliases:
            if new_alias in self._database.anime_name_catalog:
                if new_alias in old_aliases:  # if the alias is in the old aliases set, skip it.
                    continue
                err_msg = f"Anime title and Alases should be unique, the alias '{new_alias}' has existed in the database."
                raise RepeatedAnimeTitleError(err_msg)
        
        self._anime_data["aliases"] = list(new_aliases)
        for old_alias in old_aliases:
            self._database.anime_name_catalog.pop(old_alias)
        for new_alias in new_aliases:
            self._database.anime_name_catalog[new_alias] = self._id
            

    def add_alias(self, new_alias:str):
        """
        add a alias into the anime.
        if the alias has exist in anime.aliases, it will do nothing.
        """
        self._checking_existence()
        if not isinstance(new_alias, str):
            raise TypeError("alias must be a string")
        if new_alias in self._database.anime_name_catalog:
            if new_alias in self.aliases:  # if the alias is in the old aliases set, skip it.
                return None
            err_msg = f"Anime title and Alases should be unique, the new alias '{new_alias}' has existed in the database."
            raise RepeatedAnimeTitleError(err_msg)
        
        self._anime_data["aliases"].append(new_alias)
        self._database.anime_name_catalog[new_alias] = self._id

    def remove_alias(self, alias:str):
        """
        remove a alias from the anime.
        if the alias not exists in anime.aliases, it will do nothing.
        wrong datatype of the argument will not raise any exception but be viewed as it not exists in anime.aliases.
        """
        self._checking_existence()
        self._anime_data["aliases"].remove(alias)
        self._database.anime_name_catalog.pop(alias)


    @property
    def tags(self):
        self._checking_existence()
        return tuple(self._anime_data["tags"])
    
    @tags.setter
    def tags(self, new_tags):
        self._checking_existence
        if not isinstance(new_tags, (tuple)):
            raise TypeError("tags must be a tuple of strings")
        for tag in new_tags:
            if not isinstance(tag, str):
                raise TypeError("tags must be a tuple of strings")
        self._anime_data["tags"] = list(new_tags)

    def add_tag(self, new_tag:str):
        """
        add a tag into the anime.
        if the tag has existed in anime.tags, it will do nothing.
        """
        self._checking_existence()
        if not isinstance(new_tag, str):
                raise TypeError("tag must be a string")
        if new_tag in self._anime_data["tags"]:
            return None
        self._anime_data["tags"].append(new_tag)

    def remove_tag(self, tag:str):
        """
        remove a tag from the anime.
        if the tag not exists in anime.tags, it will do nothing.
        wrong datatype of the argument will not raise any exception but be viewed as it not exists in anime.tags.
        """
        self._checking_existence()
        self._anime_data["tags"].remove(tag)


    @property
    def _last_view_id(self):  #database.last_anime_id is actually a value in raw dict
        self._checking_existence()
        return self._anime_data["_last_view_id"]

    @_last_view_id.setter
    def _last_view_id(self, new_value):
        self._checking_existence()
        self._anime_data["_last_view_id"] = new_value



    def destory(self):
        """
        remove the anime itself from the database
        """
        self._checking_existence()
        self._database.anime_name_catalog.pop(self.title)
        for alias in self.aliases:
            self._database.anime_name_catalog.pop(alias)
        self._database._raw_dict["animes"].pop(self._id)
