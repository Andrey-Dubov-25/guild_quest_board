from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdventurer(BasePermission):
    """Доступ только авантюристу."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_adventurer()


class IsTavernKeeper(BasePermission):
    """Доступ только тавернщику."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_tavern_keeper()
        )


class IsTavernKeeperOrRedAdventurer(BasePermission):
    """
    Разделение доступа:
    * авантюристу - только чтение;
    * тавернщику - все методы.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_adventurer() and request.method in SAFE_METHODS
        ) or request.user.is_tavern_keeper()
