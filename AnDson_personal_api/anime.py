from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .exceptions import AnimeRemovedError, RepeatedAnimeTitleError, RepeatedViewTitleError, StringFormatError
from ._funcs import _is_month_string, _is_date_string
from .view import View

if TYPE_CHECKING:
    from .database import Database


class Anime:
    # warning: Using database.get_anime(title|alias) to get an Anime instance may be a better choice
    #            rather than using Anime(database, anime_id) directly.
    # important: Anime instance is just an object-like interaction interface.
    #            In fact, the data are stored in the database. 
    #            Therefore, an Anime instance will exist even though it has been removed in the database.
    #            It's important to return an error message when somebody uses method of Anime instance but the
    #              data is actually removed in the database.
    def __init__(self, database:Database, anime_id:int) -> None:
        """
        warning: Please create or get an Anime instance with database.create_anime or database.get_anime or database.get_all_animes\n
                 Don't use Anime() directly!
        """
        self._database = database
        self._id = anime_id

        self._anime_data = self._database._raw_dict["animes"]["_anime_objects"][anime_id]
        self._view_title_catalog = {self._anime_data["views"]["_view_objects"][view_id]["title"]: view_id for view_id in self._anime_data["views"]["_view_objects"]}


    def _checking_existence(self) -> None:
        if self._id not in self._database._raw_dict["animes"]["_anime_objects"]:
            raise AnimeRemovedError("the anime has been removed in the database.")
    

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
    def aliases(self) -> tuple[str]:
        self._checking_existence()
        return tuple(self._anime_data["aliases"])
    
    @aliases.setter
    def aliases(self, new_aliases:tuple[str]):
        self._checking_existence()
        if not isinstance(new_aliases, tuple):
            raise TypeError("aliases must be a tuple of strings")
        for new_alias in new_aliases:
            if not isinstance(new_alias, str):
                raise TypeError("aliases must be a tuple of strings")
        
        old_aliases = self._anime_data["aliases"]
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
            if new_alias in self._anime_data["aliases"]:  # if the alias is in the old aliases set, skip it.
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
        if not isinstance(new_tags, tuple):
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
    def _last_view_id(self):  #database.last_view_id is actually a value in raw dict
        self._checking_existence()
        return self._anime_data["views"]["_last_view_id"]

    @_last_view_id.setter
    def _last_view_id(self, new_value):
        self._checking_existence()
        self._anime_data["views"]["_last_view_id"] = new_value
    

    def create_view(self, title:str, is_new:Optional[bool]=None, times_view:Optional[int]=None, source:Optional[str]=None,
                    episode_range:Optional[tuple[str]]=None, duration:Optional[tuple[str]]=None,last_episode_date:Optional[str]=None,
                    comment: Optional[str]=None) -> View:
        """
        Create a view object. \n\n

        `title`: The title of the view, it must be a unique string under the anime.\n
        `is_new`: Whether the anime is new of the season when you watch it. It is a boolean, but it's optional.\n
        `times_view`: How many times you watch it. It's a integer but it's optional.\n
        `source`: Where you watch the anime. It must be a string but it's optional.\n
        `episode_range`: A tuple of episode names that you whatch this time. Episode name must be string. It's optional\n
        `duration`: A tuple of months when you whatch it. Month should comform to the format: "yyyy-mm". It's optional\n
        `last_episode_date`: When you whatch the last episode. The date should comform to the format: "yyyy-mm-dd". It's optional\n
        A view object still has a property `reviews`. You can't add review with create_view but you can use view.add_review()
        """
        self._checking_existence()
        
        # Checking datatype of args
        if not isinstance(title, str):
            raise TypeError("title must be a string.")
        if is_new is not None:
            if not isinstance(is_new, bool):
                raise TypeError("is_new must be a boolean or None.")
        if times_view is not None: 
            if not isinstance(times_view, int):
                raise TypeError("times_view must be a integer or None.")
        if source is not None:
            if not isinstance(source, str):
                raise TypeError("source must be a string or None.")
        if episode_range is not None:
            if not isinstance(episode_range, tuple):
                raise TypeError("episode_range must be a tuple of string or None.")
            for episode in episode_range:
                if not isinstance(episode, str):
                    raise TypeError("episode_range must be a tuple of string or None.")
            episode_range = list(episode_range)
        if duration is not None:
            if not isinstance(duration, tuple):
                raise TypeError("duration must be a tuple of month-string(format: yyyy-mm) or None.")
            for month in duration:
                if not isinstance(month, str):
                    raise TypeError("duration must be a tuple of month-string(format: yyyy-mm) or None.")
                if not _is_month_string(month):
                    raise StringFormatError("duration must be a tuple of month-string(format: yyyy-mm) or None.")
            duration = list(duration)
        if last_episode_date is not None:
            if not isinstance(last_episode_date, str):
                raise TypeError("last_episode_date must be a date-string(format: yyyy-mm-dd) or None.")
            if not _is_date_string(last_episode_date):
                raise StringFormatError("last_episode_date must be a date-string(format: yyyy-mm-dd) or None.")
            
        # Checking whether the title has existed
        if title in self._view_title_catalog:
            err_msg = f"View title should be unique under the anime, the title '{title}' has existed in the views of the anime."
            raise RepeatedViewTitleError(err_msg)
        
        # Adding view object into the database
        new_view_object = {
            "_class": "View",
            "title": title,
            # view info
            "is_new": is_new,
            "times_view": times_view,
            "source": source,
            # view record
            "episode_range": episode_range,
            "duration": duration,
            "last_episode_date": last_episode_date,
            # review
            "reviews": {"_last_review_id": 0,
                        "_review_objects":{}},
            }
        self._last_view_id += 1
        self._anime_data["views"]["_view_objects"][self._last_view_id] = new_view_object
        self._view_title_catalog[title] = self._last_view_id

        #return View object
        return View(self._database, self, self._last_view_id)

    def get_view(self, view_title:str) -> View:
        """
        Get View object with title.\n
        Returns `None` if the title not exists in the view list of the anime.\n
        If the datatype of title is wrong, it will be viewed as the title not found.
        """
        self._checking_existence()
        if view_title in self._view_title_catalog:
            return View(self._database, self, self._view_title_catalog[view_title])
        else:
            return None
    
    def get_all_views(self) -> tuple[View]:
        """
        Get a tuple of all views under the anime.
        """
        self._checking_existence()
        rtn = tuple(View(self._database, self, view_id) for view_id in self._anime_data["views"]["_view_objects"])
        return rtn
    
    def clear_views(self) -> None:
        """
        Remove all view object under the anime.
        """
        self._checking_existence()
        self._view_title_catalog = {}
        self._anime_data["views"]["_view_objects"] = {}


    def destory(self):
        """
        remove the anime itself from the database
        """
        self._checking_existence()
        self._database.anime_name_catalog.pop(self._anime_data["title"])
        for alias in self._anime_data["aliases"]:
            self._database.anime_name_catalog.pop(alias)
        self._database._raw_dict["animes"]["_anime_objects"].pop(self._id)
