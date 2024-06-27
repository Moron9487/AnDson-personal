
class RepeatedAnimeTitleError(Exception):
    # Anime title and Alases should be unique
    pass

class WrongDatabaseError(Exception):
    # The file is not Andson database, or the edition/version is not supported.
    pass

class AnimeRemovedError(Exception):
    # the anime has been removed in the database
    pass