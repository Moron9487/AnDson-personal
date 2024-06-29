from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .exceptions import ReviewRemovedError, RepeatedReviewTitleError, NotAvailableRankingError
from ._funcs import _is_available_ranking

if TYPE_CHECKING:
    from .view import View
    from .anime import Anime
    from .database import Database


class Review:
    def __init__(self, database:Database, anime:Anime, view:View, review_id:str) -> None:
        """
        warning: Please create or get a Review instance with view.add_review or view.get_ewview or view.get_all_reviews\n
                 Don't use Review() directly!
        """
        self._database = database
        self._anime = anime
        self._view = view
        self._id = review_id

        self._review_data = self._view._view_data["reviews"]["_review_objects"][self._id]


    def _checking_existence(self) -> None:
        if self._anime._id not in self._database._raw_dict["animes"]["_anime_objects"]:
            raise ReviewRemovedError("the review has been removed in the database.")
        if self._view._id not in self._anime._anime_data["views"]["_view_objects"]:
            raise ReviewRemovedError("the review has been removed in the database.")
        if self._id not in self._view._view_data["reviews"]["_review_objects"]:
            raise ReviewRemovedError("the review has been removed in the database.")
        

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Review):
            return False
        if self._database is not value._database:
            return False
        if self._anime._id != value._anime._id:
            return False
        if self._view._id != value._view._id:
            return False
        return self._id == value._id
    
    def __hash__(self) -> int:
        return hash((id(self._database), self._anime._id, self._view._id, self._id))

        
    @property
    def title(self) -> str:
        self._checking_existence()
        return self._review_data["title"]
    
    @title.setter
    def title(self, new_title:str) -> None:
        self._checking_existence()
        if not isinstance(new_title, str):
            raise TypeError("title must be a string")

        old_title = self.title
        if old_title == new_title:  # if the new title is same as the old one, do nothing.
            return None
        if new_title in self._view._review_title_catalog:
            err_msg = f"Review title should be unique under the view, the new title '{new_title}' has existed in the reviews of the view."
            raise RepeatedReviewTitleError(err_msg)

        self._review_data["title"] = new_title
        self._view._review_title_catalog.pop(old_title)
        self._view._review_title_catalog[new_title] = self._id

    
    @property
    def item(self) -> Optional[str]:
        self._checking_existence()
        return self._review_data["item"]
    
    @item.setter
    def item(self, new_item: str|None) -> None:
        self._checking_existence()
        if new_item is not None:
            if not isinstance(new_item, str):
                raise TypeError("item must be a string or None.")
        self._review_data["item"] = new_item

    
    @property
    def episode_range(self) -> Optional[tuple[str]]:
        self._checking_existence()
        return tuple(self._review_data["episode_range"])

    @episode_range.setter
    def episode_range(self, new_range):
        self._checking_existence
        if not isinstance(new_range, tuple):
            raise TypeError("episode_range must be a tuple of strings")
        for episode in new_range:
            if not isinstance(episode, str):
                raise TypeError("episode_range must be a tuple of strings")
        self._review_data["episode_range"] = list(new_range)

    def episode_range_add(self, new_range: str) -> None:
        """
        Add new episode into episode_range.\n
        the argument new_range is the name of the new episode, it must be a string.\n
        If the new_range has existed in episode_range, it will do nothing.
        """
        self._checking_existence()
        if not isinstance(new_range, str):
            raise TypeError("new_range must be a string")
        
        if new_range in self._review_data["episode_range"]:
            return None
        self._review_data["episode_range"].append(new_range)

    def episode_range_remove(self, episode_name:str) -> None:
        """
        Remove an episode from episode_range by the given episode_name.\n
        if the episode_name not exists in review.episode_range, it will do nothing.\n
        wrong datatype of the argument will not raise any exception but be viewed as it not exists in review.episode_range.
        """
        self._checking_existence()
        self._review_data["episode_range"].remove(episode_name)


    @property
    def ranking(self) -> Optional[int]:
        self._checking_existence()
        return self._review_data["ranking"]
    
    @ranking.setter
    def ranking(self, new_ranking: int|None) -> None:
        self._checking_existence()
        if new_ranking is not None:
            if not isinstance(new_ranking, int):
                raise TypeError("ranking must be a integer between 0 and 10.")
            if not _is_available_ranking(new_ranking):
                raise NotAvailableRankingError("ranking must be a integer between 0 and 10.")
        self._review_data["ranking"] = new_ranking

    
    @property
    def comment(self) -> Optional[str]:
        self._checking_existence()
        return self._review_data["comment"]
    
    @comment.setter
    def comment(self, new_comment: str|None) -> None:
        self._checking_existence()
        if new_comment is not None:
            if not isinstance(new_comment, str):
                raise TypeError("comment must be a string")
        self._review_data["comment"] = new_comment


    def destroy(self) -> None:
        """
        remove the review itself from the database
        """
        self._checking_existence()
        self._view._review_title_catalog.pop(self._review_data["title"])
        self._view["reviews"]["_review_objects"].pop(self._id)
