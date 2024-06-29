from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .exceptions import ViewRemovedError, RepeatedViewTitleError, StringFormatError, NotAvailableRankingError, RepeatedReviewTitleError
from ._funcs import _is_date_string, _is_month_string, _is_available_ranking

from .review import Review
if TYPE_CHECKING:
    from .anime import Anime
    from .database import Database


class View():
    def __init__(self, database:Database, anime:Anime, view_id:int) -> None:
        """
        warning: Please create or get a View instance with anime.create_view or anime.get_view or anime.get_all_views\n
                 Don't use View() directly!
        """
        self._database = database
        self._anime = anime
        self._id = view_id

        self._view_data = anime._anime_data["views"]["_view_objects"][self._id]
        self._review_title_catalog = {self._view_data["reviews"]["_review_objects"][review_id]["title"]:review_id for review_id in self._view_data["reviews"]["_review_objects"]}


    def _checking_existence(self) -> None:
        if self._anime._id not in self._database._raw_dict["animes"]["_anime_objects"]:
            raise ViewRemovedError("the view has been removed in the database.")
        if self._id not in self._anime._anime_data["views"]["_view_objects"]:
            raise ViewRemovedError("the view has been removed in the database.")
        
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, View):
            return False
        if self._database is not value._database:
            return False
        if self._anime._id != value._anime._id:
            return False
        return self._id == value._id
    
    def __hash__(self) -> int:
        return hash((id(self._database), self._anime._id, self._id))


    @property
    def title(self) -> str:
        self._checking_existence()
        return self._view_data["title"]
    
    @title.setter
    def title(self, new_title:str):
        self._checking_existence()
        if not isinstance(new_title, str):
            raise TypeError("title must be a string")

        old_title = self.title
        if old_title == new_title:  # if the new title is same as the old one, do nothing.
            return None
        if new_title in self._anime._view_title_catalog:
            err_msg = f"View title should be unique under the anime, the new title '{new_title}' has existed in the views of the anime."
            raise RepeatedViewTitleError(err_msg)

        self._view_data["title"] = new_title
        self._anime._view_title_catalog.pop(old_title)
        self._anime._view_title_catalog[new_title] = self._id
    

    @property
    def is_new(self) -> Optional[bool]:
        self._checking_existence()
        return self._view_data["is_new"]
    
    @is_new.setter
    def is_new(self, new_value: bool|None) -> None:
        self._checking_existence()
        if new_value is not None:
            if not isinstance(new_value, bool):
                raise TypeError("is_new must be a boolean or None")
        self._view_data["is_new"] = new_value

    
    @property
    def times_view(self) -> Optional[int]:
        self._checking_existence()
        return self._view_data["times_view"]
    
    @times_view.setter
    def times_view(self, new_value: int|None) -> None:
        self._checking_existence()
        if new_value is not None:
            if not isinstance(new_value, int):
                raise TypeError("times_view must be a integer or None")
        self._view_data["times_view"] = new_value

    
    @property
    def source(self) -> Optional[str]:
        self._checking_existence()
        return self._view_data["source"]
    
    @source.setter
    def source(self, new_source: str|None) -> None:
        self._checking_existence()
        if new_source is not None:
            if not isinstance(new_source, str):
                raise TypeError("source must be a string or None")
        self._view_data["source"] = new_source


    @property
    def episode_range(self) -> Optional[tuple[str]]:
        self._checking_existence()
        return tuple(self._view_data["episode_range"])
    
    @episode_range.setter
    def episode_range(self, new_value: tuple[str]|None) -> None:
        self._checking_existence()
        if new_value is not None:
            if not isinstance(new_value, tuple):
                raise TypeError("episode_range must be a tuple of string or None.")
            for episode in new_value:
                if not isinstance(episode, str):
                    raise TypeError("episode_range must be a tuple of string or None.")
            self._view_data["episode_range"] = list(new_value)
        else:
            self._view_data["episode_range"] = None

    def episode_range_add(self, new_range: str) -> None:
        """
        Add new episode into episode_range.\n
        the argument new_range is the name of the new episode, it must be a string.\n
        If the new_range has existed in episode_range, it will do nothing.
        """
        self._checking_existence()
        if not isinstance(new_range, str):
            raise TypeError("new_range must be a string")
        
        if new_range in self._view_data["episode_range"]:
            return None
        self._view_data["episode_range"].append(new_range)

    def episode_range_remove(self, episode_name:str) -> None:
        """
        Remove an episode from episode_range by the given episode_name.\n
        if the episode_name not exists in view.episode_range, it will do nothing.\n
        wrong datatype of the argument will not raise any exception but be viewed as it not exists in view.episode_range.
        """
        self._checking_existence()
        self._view_data["episode_range"].remove(episode_name)

    
    @property
    def duration(self) -> Optional[tuple[str]]:
        self._checking_existence()
        return tuple(self._view_data["duration"])
    
    @duration.setter
    def duration(self, new_value: tuple[str]|None) -> None:
        self._checking_existence()
        if new_value is not None:
            if not isinstance(new_value, tuple):
                raise TypeError("duration must be a tuple of month-string(format: yyyy-mm) or None.")
            for month in new_value:
                if not isinstance(month, str):
                    raise TypeError("duration must be a tuple of month-string(format: yyyy-mm) or None.")
                if not _is_month_string(month):
                    raise TypeError("duration must be a tuple of month-string(format: yyyy-mm) or None.")
            self._view_data["duration"] = list(new_value)
        else:
            self._view_data["duration"] = None
                
    def duration_add(self, new_month:str) -> None:
        """
        Add new month into duration.\n
        new_month must be a string which conform to the yyyy-mm format.\n
        If the new_month has existed in duration, it will do nothing.
        """
        self._checking_existence()
        if not isinstance(new_month, str):
            raise TypeError("new_month must be a tuple of month-string(format: yyyy-mm) or None.")
        if not _is_month_string(new_month):
            raise StringFormatError("new_month must be a tuple of month-string(format: yyyy-mm) or None.")
        
        if new_month in self._view_data["duration"]:
            return None
        
        self._view_data["duration"].append(new_month)

    def duration_remove(self, month:str) -> None:
        """
        Remove a month from duration by the given month argument.\n
        if the month not exists in view.duration, it will do nothing.\n
        wrong datatype of the argument will not raise any exception but be viewed as it not exists in view.duration.
        """
        self._checking_existence()
        self._view_data["duration"].remove(month)


    @property
    def last_episode_date(self) -> Optional[str]:
        self._checking_existence()
        return self._view_data["last_episode_date"]
    
    @last_episode_date.setter
    def last_episode_date(self, new_value:str|None) -> None:
        self._checking_existence()
        if new_value is not None:
            if not isinstance(new_value, str):
                raise TypeError("last_episode_date must be a date-string(format: yyyy-mm-dd) or None.")
            if not _is_date_string(new_value):
                raise StringFormatError("last_episode_date must be a date-string(format: yyyy-mm-dd) or None.")
        self._view_data["last_episode_date"] = new_value


    @property
    def _last_review_id(self):  #database.last_review_id is actually a value in raw dict
        self._checking_existence()
        return self._view_data["reviews"]["_last_review_id"]

    @_last_review_id.setter
    def _last_review_id(self, new_value):
        self._checking_existence()
        self._view_data["reviews"]["_last_review_id"] = new_value


    def add_review(self, title:str, item:Optional[str]=None, episode_range:Optional[tuple[str]]=None,
                   ranking:Optional[int]=None, comment:Optional[str]=None) -> Review:
        """
        `title` is the title of the review, it must be a string under the view.\n
        `item` means which aspect of the anime the review is. It must be a string, but it's optional.\n
        `episode_range` means on which episodes the review is. It must be a tuple of episode names(string) but it's opitonal.\n
        `ranking` is the ranking you give to the anime. It must be a integer between 0 and 10, but it's optional.\n
        `comment` is the comment you give to the anime. It must be a string but it's optional.\n
        It's suggested that support markdown when further process of `comment`.\n
        """
        self._checking_existence()

        # Checking datatype of args
        if not isinstance(title, str):
            raise TypeError("title must be a string.")
        if item is not None:
            if not isinstance(item, str):
                raise TypeError("item must be a string or None.")
        if episode_range is not None:
            if not isinstance(episode_range, tuple):
                raise TypeError("episode_range must be a tuple of string or None.")
            for episode in episode_range:
                if not isinstance(episode, str):
                    raise TypeError("episode_range must be a tuple of string or None.")
            episode_range = list(episode_range)
        if ranking is not None:
            if not isinstance(ranking, int):
                raise TypeError("ranking must be a integer between 0 and 10.")
            if not _is_available_ranking(ranking):
                raise NotAvailableRankingError("ranking must be a integer between 0 and 10.")
        if comment is not None:
            if not isinstance(comment, str):
                raise TypeError("comment must be a string")
            
        # Checking whether the title has existed
        if title in self._review_title_catalog:
            err_msg = f"Review title should be unique under the view, the title '{title}' has existed in the reviews of the view."
            raise RepeatedReviewTitleError(err_msg)
        
        # Adding review object into the database
        new_review_object = {
            "_class": "Review",
            "title": title,
            "item": item,
            "episode_range": episode_range,
            "ranking": ranking,
            "comment": comment
        }
        self._last_review_id += 1
        self._view_data["reviews"]["_review_objects"][self._last_review_id] = new_review_object
        self._review_title_catalog[title] = self._last_review_id

        # return Review object
        return Review(self._database, self._anime, self, self._last_review_id)

    def get_review(self, review_title:str) -> Review:
        """
        Get Review object with title.\n
        Returns `None` if the title not exists in the review list of the view.\n
        If the datatype of title is wrong, it will be viewed as the title not found.
        """
        self._checking_existence()
        if review_title in self._review_title_catalog:
            return Review(self._database, self._anime, self, self._review_title_catalog[review_title])
        else:
            return None
        
    def get_all_reviews(self) -> tuple[Review]:
        """
        Get a tuple of all re reviews under the view.
        """
        self._checking_existence()
        rtn = tuple(Review(self._database, self._anime, self, review_id) for review_id in self._view_data["reviews"]["_review_objects"])
        return rtn
    
    def clear_views(self) -> None:
        """
        Remove all review object under the view.
        """
        self._checking_existence()
        self._review_title_catalog = {}
        self._view_data["reviews"]["_review_objects"] = {}


    def destroy(self) -> None:
        """
        remove the view itself from the database
        """
        self._checking_existence()
        self._anime._view_title_catalog.pop(self._view_data["title"])
        self._anime["views"]["_view_objects"].pop(self._id)
