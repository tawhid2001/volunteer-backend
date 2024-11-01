from rest_framework import permissions

class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow organizers of a volunteer work to edit or delete it.
    """

    def has_permission(self, request, view):
        def has_permission(self, request, view):
            # Allow any user to list or retrieve
            if view.action in ['list', 'retrieve']:
                return True
            # For other actions, check if the user is authenticated
            return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the organizer of the volunteer work
        return obj.organizer == request.user



class IsOrganizer(permissions.BasePermission):
    """
    Custom permission to only allow organizers of a volunteer work to manage join requests.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the user is the organizer of the volunteer work
        return obj.volunteer_work.organizer == request.user