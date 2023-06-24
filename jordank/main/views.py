from django.shortcuts import render
from django.views import View
from main.golf_scripts import leaderboard


# Create your views here.
class HomeView(View):
    def get(self, request):
        data = leaderboard.get_data()
        return render(request, 'home.html', context=data)