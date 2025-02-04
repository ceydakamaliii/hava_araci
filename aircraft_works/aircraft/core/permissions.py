from rest_framework.permissions import BasePermission
from aircraft.core.types import AuthenticatedRequest
from rest_framework.views import APIView
from rest_framework.request import Request
from aircraft.accounts.models import Team

# Burada oluşturduğum permission classlar sayesinde oluşturmuş olduğum endpointlere gerekli permission classlarını veriyorum

class AircraftIsAuthenticated(BasePermission): # Bu permission sisteme login olmuş kullanıcılara izin verir.
    def has_permission(self, request: AuthenticatedRequest, view: APIView) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_active)
    

class IsNotAircraftAssemblyTeam(BasePermission): # Bu permission sistemem login olmuş kullanıcılardan takımı montaj olmayan kullanıcılara izin verir.
    def has_permission(self, request: Request, view: APIView) -> bool:
        # Önce kimlik doğrulaması kontrolü
        if not bool(request.user and request.user.is_authenticated):
            return False
            
        # Takım kontrolü
        if not hasattr(request.user, 'team') or not request.user.team:
            return False
            
        # Montaj takımı kontrolü
        return request.user.team.team_type != "ASSEMBLY"

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        # Önce has_permission kontrolü
        if not self.has_permission(request, view):
            return False

        # Kullanıcının takımı ile parçanın takımı aynı olmalı
        return obj.user.team == request.user.team


class IsAircraftWingTeam(BasePermission): # Bu permission sistemem login olmuş ve takımı kanat olan kullanıcılara izin verir.
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.user and request.user.team:
            return bool(request.user and request.user.is_authenticated and request.user.is_active and (request.user.team.team_type == Team.Team.WING))
        return False


class IsAircraftTailTeam(BasePermission): # Bu permission sistemem login olmuş ve takımı kuyruk olan kullanıcılara izin verir.
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.user and request.user.team:
            return bool(request.user and request.user.is_authenticated and request.user.is_active and (request.user.team.team_type == Team.Team.TAIL))
        return False
        

class IsAircraftAssemblyTeam(BasePermission): # Bu permission sistemem login olmuş ve takımı montaj olan kullanıcılara izin verir.
    def has_permission(self, request: Request, view: APIView) -> bool:
        if not bool(request.user and request.user.is_authenticated):
            return False
            
        if not hasattr(request.user, 'team') or not request.user.team:
            return False
            
        return request.user.team.team_type == "ASSEMBLY"
        

class IsAircraftAvionicsTeam(BasePermission): # Bu permission sisteme login olmuş ve takımı aviyonik olan kullanıcılara izin verir.
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.user and request.user.team:
            return bool(request.user and request.user.is_authenticated and request.user.is_active and (request.user.team.team_type == Team.Team.AVIONICS))
        return False
        

class IsAircraftFuselageTeam(BasePermission): # Bu permission sisteme login olmuş ve takımı gövde olan kullanıcılara izin verir.
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.user and request.user.team:
            return bool(request.user and request.user.is_authenticated and request.user.is_active and (request.user.team.team_type == Team.Team.FUSELAGE))
        return False


class HasTeamAndNotAssembly(BasePermission):
    """
    Kullanıcının bir takımı olmalı ve montaj takımında olmamalı.
    Ayrıca sadece kendi takımının parçalarına erişebilmeli.
    """
    def has_permission(self, request: Request, view: APIView) -> bool:
        # Önce kimlik doğrulaması kontrolü
        if not bool(request.user and request.user.is_authenticated):
            return False
            
        # Takım kontrolü
        if not hasattr(request.user, 'team') or not request.user.team:
            return False
            
        # Montaj takımı kontrolü
        if request.user.team.team_type == Team.Team.ASSEMBLY:
            return False

        return True

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        # Önce has_permission kontrolü
        if not self.has_permission(request, view):
            return False

        # Kullanıcının takımı ile parçanın takımı aynı olmalı
        return obj.user.team == request.user.team