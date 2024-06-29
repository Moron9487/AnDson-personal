
class WrongDatabaseError(Exception):
    # The file is not Andson database, or the edition/version is not supported.
    pass



class AnimeRemovedError(Exception):
    # the anime has been removed in the database
    pass

class ViewRemovedError(Exception):
    # the view has been removed in the database
    pass

class ReviewRemovedError(Exception):
    # the review has been removed in the database
    pass



class RepeatedAnimeTitleError(Exception):
    # Anime title and Alases should be unique
    pass

class RepeatedViewTitleError(Exception):
    # View title should be unique under each anime
    pass

class RepeatedReviewTitleError(Exception):
    # Review title should be unique under each view
    pass



class StringFormatError(Exception):
    # A string not conform to a given format
    pass

class NotAvailableRankingError(Exception):
    # ranking value must between 0 and 10.
    pass