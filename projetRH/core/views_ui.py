#core/views_ui.py
from django.shortcuts import render
from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

class EmployeesView(TemplateView):
    template_name = 'employees.html'

class ContractsView(TemplateView):
    template_name = 'contracts.html'

class LeavesView(TemplateView):
    template_name = 'leaves.html'

class SalariesView(TemplateView):
    template_name = 'salaries.html'

class EvaluationsView(TemplateView):
    template_name = 'evaluations.html'

class EvaluationReportsView(TemplateView):
    template_name = 'evaluation_reports.html'

class RecruitmentView(TemplateView):
    template_name = 'recruitment.html'

class FavoritesView(TemplateView):
    template_name = 'favorites.html'

