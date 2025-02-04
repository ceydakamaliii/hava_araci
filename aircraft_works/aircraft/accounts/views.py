from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.exceptions import ValidationError

from aircraft.accounts.models import Team, User
from aircraft.accounts.serializers import AircraftObtainPairSerializer, CreateUserSerializer, LogoutSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from aircraft.core.permissions import AircraftIsAuthenticated


class UserLogoutView(GenericAPIView): # Sistemde login olmuş kullanıcıyı logout eden view
    serializer_class = LogoutSerializer 
    permission_classes = [AircraftIsAuthenticated]

    def post(self, request, *args):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()  # This will blacklist the token
            return Response(status=HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": e.detail}, status=HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user}) # kullanıcıyı contexte ekler, bu sayede serializer içinde kullanıcıya erişilebiliriz.
        return context
    

class SignUpView(CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def perform_create(self, serializer):
        return serializer.save()


class AircraftTokenObtainPairView(TokenObtainPairView): # Login için oluşturmuş olduğum endpointdir. Login olan kullanıcıya access_token ve refresh_token döndürür.
    serializer_class = AircraftObtainPairSerializer


class MyUserDetailView(RetrieveUpdateAPIView): # Kullanıcı detayını veren endpointdir.
    serializer_class = UserSerializer
    permission_classes = [AircraftIsAuthenticated] # Bu endpointin çalışması için kullanıcının login olması gerekir.

    queryset = User.objects.all()

    def get_object(self) -> User:
        user = self.request.user
        self.check_object_permissions(self.request, user)
        return user