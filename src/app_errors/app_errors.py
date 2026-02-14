class UserPermissionError(Exception):
    """Levée lorsqu'un utilisateur n'a pas les droits requis."""

    pass


class UserAlreadyExistsError(Exception):
    """Levée lorsqu'un utilisateur existe déjà lors de sa création."""

    pass


class UserNotFoundError(Exception):
    """Levée lorsqu'un utilisateur n'est pas trouvé."""

    pass


class InvalidInputError(Exception):
    """Levée lorsqu'une entrée utilisateur est invalide."""

    pass


class InvalidPassWordError(Exception):
    """Levée lorsqu'un mot de passe ne respecte pas les critères."""

    pass


class CreationError(Exception):
    """Levée lorsqu'une création (ex: utilisateur, objet) échoue."""

    pass


class IncorrectPasswordError(Exception):
    """Levée lorsqu'un mot de passe saisi est incorrect."""

    pass


class UserSessionExpiredError(Exception):
    """Levée lorsqu'il n'y a pas de session active pour l'utilisateur."""

    pass


class SomeThingWentWrongError(Exception):
    """Levée pour signaler une erreur générique inattendue."""

    pass


class DataDownloadError(Exception):
    """Levée en cas d'erreur lors du téléchargement des fichiers."""

    pass


class InsufficientDiskSpaceError(Exception):
    """Levée lorsqu'il n'y a pas assez d'espace disque."""

    pass
