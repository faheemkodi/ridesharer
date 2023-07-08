from rest_framework import permissions


class IsDriverOrRiderElseReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        permit = False
        if obj.driver == request.user or obj.rider == request.user:
            permit = True
        return permit


class UpdateIfDriverDeleteIfRiderElseCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        permit = False
        if request.method == "POST":
            permit = True
        if request.method == "DELETE" and obj.rider == request.user:
            permit = True
        if request.method == "PUT" or request.method == "PATCH":
            if obj.ride.driver == request.user:
                permit = True
        return permit
