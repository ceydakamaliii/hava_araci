from django.urls import path

from aircraft.plane_management import views

urlpatterns = [
    path("v1/parts/", views.PartView.as_view(), name="part_management"),
    path('v1/parts/<int:pk>/', views.PartRetrieveUpdateDestroyView.as_view(), name='part_details'),
    path('v1/planes/', views.PlaneAssemblyCreateView.as_view(), name='plane_management'),
    path('v1/parts/score/', views.PartScoreView.as_view(), name='parts_score'),
]
