from django.views.generic.edit import CreateView
from django.views.generic import DetailView, ListView, FormView, TemplateView, View
from bowling_entry.models import Match, Team, Bowler, Game
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory, ModelForm
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, QueryDict
from django.forms.widgets import HiddenInput
from django.contrib import messages
from django import forms


class MatchList(ListView):
    model = Match
    context_object_name = 'matches'

    def get_queryset(self):
        return self.model.objects.filter(creator=self.request.user)


class MatchCreate(CreateView):
    model = Match
    fields = ['date', 'lanes', 'players_per_team', 'number_of_games', ]
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        """
        Override to insert the user into the match
        :param form:
        :return:
        """
        form.instance.creator = self.request.user
        return super(MatchCreate, self).form_valid(form)


class MatchMixin():

    def get_match(self, identifier):
        return get_object_or_404(Match, pk=identifier, creator=self.request.user)


class StartGames(View, MatchMixin):

    def get(self, request, *args, **kwargs):
        self.match = self.get_match(kwargs['match_pk'])

        if not self.match.games_created:
            self.match.start_games()

        return HttpResponseRedirect(self.match.get_absolute_url())


class TeamMixin(MatchMixin):

    def get_team(self, identifier):
        return get_object_or_404(Team, pk=identifier, match=self.match)


class MatchDetails(DetailView):
    """
    Return the match detail page.
    """
    model = Match
    context_object_name = 'match'

    def get_queryset(self):
        """
        Override the queryset to only return the objects that are found by the user.
        :return:
        """
        return super(MatchDetails, self).get_queryset().filter(creator=self.request.user)


class TeamCreate(CreateView, MatchMixin):
    """
    Create a new team object in order to start populating scores.
    """
    model = Team
    fields = ['name']

    def get_success_url(self):
        return reverse('bowling_entry_bowlercreate', args=[self.match.pk, self.object.pk])

    def validate_match(self):
        result = True
        if len(self.match.teams.all()) > 2:
            messages.error(self.request, 'Match already contains two teams')
        return result

    def form_valid(self, form):
        form.instance.match = self.match
        return super(TeamCreate, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.match = self.get_match(kwargs['match_pk'])

        if not self.validate_match():
            return HttpResponseRedirect(self.match.get_absolute_url())

        return super(TeamCreate, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.match = self.get_match(kwargs['match_pk'])

        if not self.validate_match():
            return HttpResponseRedirect(self.match.get_absolute_url())

        return super(TeamCreate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TeamCreate, self).get_context_data(**kwargs)
        context['match'] = self.match
        return context


class TeamDetails(DetailView, MatchMixin):
    model = Team

    def get_queryset(self):
        return self.model.objects.filter(match=self.match)

    def get(self, request, *args, **kwargs):
        self.match = self.get_match(kwargs['match_pk'])
        return super(TeamDetails, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TeamDetails, self).get_context_data(**kwargs)
        context['match'] = self.match
        return context


class BowlerCreate(TemplateView, TeamMixin):
    template_name = 'bowling_entry/create_bowlers.html'

    def get_success_url(self):
        return self.team.get_absolute_url()

    def get_formset(self, form_data=None):

        bowler_form_set = modelformset_factory(Bowler,
                                               extra=self.match.players_per_team,
                                               max_num=self.match.players_per_team,
                                               fields=('name', 'handicap', 'type'))
        formset = bowler_form_set(form_data, queryset=Bowler.objects.filter(team=self.team))

        return formset

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        instances = form.save(commit=False)
        order = 1
        for instance in instances:
            instance.order = order
            order += 1
            instance.team = self.team
            instance.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(form=form))

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        self.match = self.get_match(self.kwargs['match_pk'])
        self.team = self.get_team(self.kwargs['team_pk'])
        form = self.get_formset()
        return self.render_to_response(self.get_context_data(formset=form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.match = self.get_match(self.kwargs['match_pk'])
        self.team = self.get_team(self.kwargs['team_pk'])

        form = self.get_formset(form_data=self.request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(BowlerCreate, self).get_context_data(**kwargs)
        context['match'] = self.match
        context['team'] = self.team
        return context


class GameDisplay(TemplateView, TeamMixin):
    template_name = 'bowling_entry/game_details.html'

    def get(self, request, *args, **kwargs):
        self.match = self.get_match(self.kwargs['match_pk'])

        self.game_id = int(self.kwargs['game_id'])

        return super(GameDisplay, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GameDisplay, self).get_context_data(**kwargs)

        context['match'] = self.match
        context['game_id'] = self.game_id

        context['game_data'] = self.match.get_game_data(self.game_id)

        return context


class FrameForm(forms.Form):
    bowler_id = forms.CharField(widget=HiddenInput())
    bowler_name = forms.CharField(widget=HiddenInput())
    score = forms.CharField(required=False)
    split = forms.BooleanField(required=False)


class TenthFrameForm(forms.Form):
    bowler_id = forms.CharField(widget=HiddenInput())
    bowler_name = forms.CharField(widget=HiddenInput())
    score = forms.CharField(required=False)
    split10 = forms.BooleanField(required=False)
    split11 = forms.BooleanField(required=False)
    split12 = forms.BooleanField(required=False)


class FrameEdit(TemplateView, MatchMixin):
    template_name = 'bowling_entry/frame_edit.html'

    def get_success_url(self):
        return reverse('bowling_entry_gamedisplay', args=[self.match.pk, self.game_id])

    def get_formset(self, form_data=None):
        if self.frame_id < 10:
            bowler_form_set = formset_factory(FrameForm, extra=0)
        else:
            bowler_form_set = formset_factory(TenthFrameForm, extra=0)

        game_data = self.match.get_game_data(self.game_id)

        formsets = []

        for team, team_data in game_data:
            frame_data = []
            for bowler, game in team_data:
                if self.frame_id < 10:
                    frame_data.append({'bowler_id': bowler.pk, 'bowler_name': bowler.name,
                                       'score': game.get_frame(self.frame_id),
                                       'split': game.is_split(self.frame_id-1)})
                else:
                    frame_data.append({'bowler_id': bowler.pk, 'bowler_name': bowler.name,
                                       'score': game.get_frame(self.frame_id),
                                       'split10': game.is_split(9),
                                       'split11': game.is_split(10),
                                       'split12': game.is_split(11)})

            formset = bowler_form_set(form_data, prefix=team.pk, initial=frame_data)
            formsets.append((team, formset))

        return formsets

    def form_valid(self, formsets):
        """
        If the form is valid, redirect to the supplied URL.
        """
        for team, formset in formsets:
            for form in formset:
                bowler_id = form.cleaned_data['bowler_id']
                score = form.cleaned_data['score']

                bowler = Bowler.objects.get(pk=bowler_id)
                game = Game.objects.get(bowler=bowler, game_number=self.game_id)

                if self.frame_id < 10:
                    # Splits are 0 indexed frame values.
                    game.set_split(self.frame_id-1, form.cleaned_data['split'])
                else:
                    game.set_split(9, form.cleaned_data['split10'])
                    game.set_split(10, form.cleaned_data['split11'])
                    game.set_split(11, form.cleaned_data['split12'])

                game.set_frame(self.frame_id, score)
                game.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(formsets=form))

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        self.match = self.get_match(self.kwargs['match_pk'])
        self.game_id = int(self.kwargs['game_id'])
        self.frame_id = int(self.kwargs['frame_id'])
        form = self.get_formset()
        return self.render_to_response(self.get_context_data(formsets=form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.match = self.get_match(self.kwargs['match_pk'])
        self.game_id = int(self.kwargs['game_id'])
        self.frame_id = int(self.kwargs['frame_id'])

        formsets = self.get_formset(self.request.POST)

        valid = True

        for team, formset in formsets:
            valid = valid and formset.is_valid()

        if valid:
            return self.form_valid(formsets)
        else:
            return self.form_invalid(formsets)

    def get_context_data(self, **kwargs):
        context = super(FrameEdit, self).get_context_data(**kwargs)
        context['match'] = self.match
        context['game_id'] = self.game_id
        context['frame_id'] = self.frame_id
        return context


class FrameBowlerEdit(FormView, MatchMixin):
    template_name = 'bowling_entry/frame_bowler_edit.html'

    def get_form_class(self):
        if self.frame_id == 10:
            return TenthFrameForm
        else:
            return FrameForm

    def get_initial(self):
        bowler = Bowler.objects.get(pk=self.bowler_id)
        game = Game.objects.get(game_number=self.game_id, bowler=bowler)

        result = {'bowler_id': bowler.pk,
                  'bowler_name': bowler.name,
                  'score': game.get_frame(self.frame_id),
                  'split': game.is_split(self.frame_id-1),
                  'split10': game.is_split(9),
                  'split11': game.is_split(10),
                  'split12': game.is_split(11)}

        return result

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        bowler_id = form.cleaned_data['bowler_id']
        score = form.cleaned_data['score']

        bowler = Bowler.objects.get(pk=bowler_id)
        game = Game.objects.get(bowler=bowler, game_number=self.game_id)

        if self.frame_id < 10:
            # Splits are 0 indexed frame values.
            game.set_split(self.frame_id-1, form.cleaned_data['split'])
        else:
            game.set_split(9, form.cleaned_data['split10'])
            game.set_split(10, form.cleaned_data['split11'])
            game.set_split(11, form.cleaned_data['split12'])

        game.set_frame(self.frame_id, score)
        game.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('bowling_entry_gamedisplay', args=[self.match.pk, self.game_id])

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        self.match = self.get_match(self.kwargs['match_pk'])
        self.game_id = int(self.kwargs['game_id'])
        self.frame_id = int(self.kwargs['frame_id'])
        self.bowler_id = int(self.kwargs['bowler_id'])
        return super(FrameBowlerEdit, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.match = self.get_match(self.kwargs['match_pk'])
        self.game_id = int(self.kwargs['game_id'])
        self.frame_id = int(self.kwargs['frame_id'])
        self.bowler_id = int(self.kwargs['bowler_id'])

        return super(FrameBowlerEdit, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FrameBowlerEdit, self).get_context_data(**kwargs)

        context['match'] = self.match
        context['bowler_id'] = self.bowler_id
        context['frame_id'] = self.frame_id
        context['game_id'] = self.game_id

        return context