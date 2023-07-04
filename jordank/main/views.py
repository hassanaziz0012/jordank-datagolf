from django.shortcuts import render
from django.views import View
from main.golf_scripts import leaderboard, sample


# Create your views here.
class HomeView(View):
    def get(self, request):
        data = leaderboard.get_data()
        return render(request, 'home.html', context=data)


class SampleView(View):
    def get(self, request):
        data = sample.get_data()
        return render(request, 'sample.html', context={"data": data})
