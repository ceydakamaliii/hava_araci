from aircraft.accounts.models import User

from rest_framework.request import Request

 # 'user' özelliği, request objesinin User modeline ait olduğunu belirtir. Bu, type checking ve kod tamamlama için kullanılır.
class AuthenticatedRequest(Request):
    user: User
