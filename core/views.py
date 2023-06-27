
from rooms.models import Section

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from users.models import PlayerUser, CroupierUser


class HomePageView(View):
    template_name = 'home.html'

    def get(self, request):
        section_dict = Section.objects.values('id', 'section_name')
        section = [elemento['section_name'] for index, elemento in enumerate(section_dict)]

        if request.user.is_authenticated and request.user.is_croupier:
            croupier = CroupierUser.objects.filter(user=request.user)
            return render(request, self.template_name, {'section': section, 'croupier': croupier})

        if request.user.is_authenticated and request.user.is_player:
            print(request.user)
            player = PlayerUser.objects.get(user_id=request.user.id)
            return render(request, self.template_name, {'section': section, 'player': player})
        else:
            return render(request, self.template_name, {'section': section})




