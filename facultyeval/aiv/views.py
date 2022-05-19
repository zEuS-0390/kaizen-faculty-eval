from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from accounts.models import Member
from django.contrib import messages
from .models import *
from .decorators import *
from .forms import *

# Create your views here.
class Index(View):

    @method_decorator(login_required(login_url="accounts:login"))
    @method_decorator(admin_only)
    def get(self, request, SEM, SY):
        members = Member.objects.all()
        school_year = SchoolYear.objects.filter(school_year=SY).first()
        sy_group = SchoolYear.objects.all()
        context = {"aiv_data": [], "SEM": SEM, "SY":SY, "sy_group": sy_group}
        for member in members:
            result = AIVRating.objects.filter(member=member, school_year=school_year, semester=SEM)
            if result.exists():
                context["aiv_data"].append([member, True])
                continue
            context["aiv_data"].append([member, False])
        return render(request, template_name="aiv/index.html", context=context)

    @method_decorator(login_required(login_url="accounts:login"))
    @method_decorator(admin_only)
    def post(self, request, SEM, SY):
        return redirect("/")

class EvalScores(View):

    @method_decorator(login_required(login_url="accounts:login"))
    @method_decorator(admin_only)
    def get(self, request, SEM, SY, ID):
        member = Member.objects.filter(id=ID).first()
        school_year = SchoolYear.objects.filter(school_year=SY).first()
        aivrating = AIVRating.objects.filter(member=member, school_year=school_year, semester=SEM).first()
        aivcriterionscores = AIVCriterionScores.objects.filter(aivrating=aivrating).all()
        context = {
            "aivcriterionscores": aivcriterionscores,
            "member_id": ID,
            "SY": SY,
            "SEM": SEM
        }
        return render(request, template_name="aiv/updateaivevalscores.html", context=context)

    @method_decorator(login_required(login_url="accounts:login"))
    @method_decorator(admin_only)
    def post(self, request, SEM, SY, ID):
        return redirect("/")

class CriterionScores(View):

    @method_decorator(login_required(login_url="accounts:login"))
    @method_decorator(admin_only)
    def get(self, request, SEM, SY, ID, CRITERIONID):
        member = Member.objects.filter(id=ID).first()
        school_year = SchoolYear.objects.filter(school_year=SY).first()
        aivrating = AIVRating.objects.filter(member=member, school_year=school_year, semester=SEM).first()
        aivcriterion = AIVCriterion.objects.filter(id=CRITERIONID).first()
        aivcriterionscores = AIVCriterionScores.objects.filter(aivrating=aivrating, aivcriterion=aivcriterion)
        if aivcriterionscores.exists():
            result = aivcriterionscores.first()
            form = AIVCriterionScoresForm(initial={
                "first_visit": result.first_visit,
                "second_visit": result.second_visit,
                "average_score": result.average_score,
                "remarks": result.remarks
            })
        else:
            form = AIVCriterionScoresForm()
        return render(request, template_name="aiv/criterionscores.html", context={"form": form})

    @method_decorator(login_required(login_url="accounts:login"))
    @method_decorator(admin_only)
    def get(self, request, SEM, SY, ID, CRITERIONID):
        return redirect("/")

@login_required(login_url="accounts:login")
@admin_only
def ListofCriteria(request):
    criteria = AIVCriterion.objects.all()
    context = {
        "criteria": criteria
    }
    return render(request, template_name="aiv/listofcriteria.html", context=context)

class AIVRatingEntry(View):

    @method_decorator(login_required(login_url="accounts:login"))
    @method_decorator(admin_only)
    def get(self, request, SEM, SY):
        form = AIVRatingForm()
        context = {"form": form}
        return render(request, template_name="aiv/aivrating.html", context=context)
    
    @method_decorator(login_required(login_url="accounts:login"))
    @method_decorator(admin_only)
    def post(self, request, SEM, SY):
        form = AIVRatingForm(request.POST)
        if form.is_valid():
            aivrating = form.save(commit=False)
            member = form.cleaned_data.get("member")
            semester = form.cleaned_data.get("semester")
            school_year = form.cleaned_data.get("school_year")
            if AIVRating.objects.filter(member=member, semester=semester, school_year=school_year).exists():
                messages.error(request, "AIV evaluation entry already exist!")
                return redirect("aiv:aiv_rating_entry", SEM=semester, SY=school_year)
            aivrating.save()
            criteria = AIVCriterion.objects.all()
            for criterion in criteria:
                criterion_scores = AIVCriterionScores(aivrating=aivrating, aivcriterion=criterion)
                criterion_scores.save()
            messages.success(request, "AIV evaluation entry successfully created!")
            return redirect("aiv:index", SEM=semester, SY=school_year)
        return redirect("aiv:aiv_rating_entry", SEM=SEM, SY=SY)

@login_required(login_url="accounts:login")
@admin_only
def DeleteAIVRating(request, SEM, SY, ID):
    member = Member.objects.filter(id=ID).first()
    school_year = SchoolYear.objects.filter(school_year=SY).first()
    aivrating = AIVRating.objects.filter(member=member, school_year=school_year, semester=SEM)
    if aivrating.exists():
    #     #ActivityLogs
        # logs = ActivityLogs(member=member, activity_log=ActivityLogs.DELETED, eval_log=ActivityLogs.HR)
        # logs.save()
        #End of ActivityLogs
        aivrating.delete()
        messages.success(request, "AIV evaluation entry was successfully deleted!")
        return redirect("aiv:index", SEM=SEM, SY=SY)
    else:
        messages.error(request, f"ID {ID} does not exist!")
    return redirect("aiv:index", SEM=SEM, SY=SY)