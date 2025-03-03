from django.shortcuts import render, redirect
from .forms import PlaybookForm, CustomStepFormSet
from .models import IncidentPlaybook, ComplianceRule, PlaybookTemplate
from .tasks import automate_response

# def generate_playbook(request):
#     if request.method == 'POST':
#         form = PlaybookForm(request.POST)
#         if form.is_valid():
#             playbook = form.save(commit=False)
            
#             # Simple playbook generation logic
#             incident_type = playbook.incident_type
#             severity = playbook.severity
#             systems = playbook.affected_systems
            
#             playbook_text = f"""
#             Incident Response Playbook
#             =========================
#             Type: {incident_type.upper()}
#             Severity: {severity.upper()}
#             Affected Systems: {systems}
            
#             Steps:
#             """
            
#             if incident_type == 'malware':
#                 playbook_text += """
#                 1. Isolate infected systems.
#                 2. Scan with antivirus tools.
#                 3. Remove malicious files.
#                 4. Restore from backups.
#                 """
#             elif incident_type == 'phishing':
#                 playbook_text += """
#                 1. Identify phishing email source.
#                 2. Block sender domain.
#                 3. Educate users on phishing signs.
#                 4. Reset compromised credentials.
#                 """
#             elif incident_type == 'ddos':
#                 playbook_text += """
#                 1. Activate DDoS mitigation tools.
#                 2. Reroute traffic.
#                 3. Monitor network performance.
#                 4. Investigate attack source.
#                 """
#             elif incident_type == 'databreach':
#                 playbook_text += """
#                 1. Contain breach by securing systems.
#                 2. Assess data exposure.
#                 3. Notify affected parties.
#                 4. Conduct forensic analysis.
#                 """
            
#             playbook_text += f"""
#             Notes: Adjust steps based on {severity} severity. Escalate if needed.
#             """
            
#             playbook.playbook_text = playbook_text
#             playbook.save()
#             return render(request, 'generator/playbook_result.html', {'playbook': playbook})
#     else:
#         form = PlaybookForm()
    
#     return render(request, 'generator/playbook_form.html', {'form': form})


def generate_playbook(request):
    if request.method == 'POST':
        form = PlaybookForm(request.POST)
        step_formset = CustomStepFormSet(request.POST)
        if form.is_valid() and step_formset.is_valid():
            playbook = form.save()
            step_formset.instance = playbook
            step_formset.save()
            # Append custom steps to playbook_text
            playbook.playbook_text += "\nCustom Steps:\n"
            for step in playbook.custom_steps.all():
                playbook.playbook_text += f"{step.step_order}. {step.step_description}\n"

            playbook.playbook_text += "\nDecision Points:\n"
            for dp in playbook.decision_points.all():
                playbook.playbook_text += f"- {dp.condition}: {dp.action}\n"

            rules = ComplianceRule.objects.filter(applicable_incidents=playbook.incident_type)
            playbook.playbook_text += "\nCompliance Requirements:\n"
            for rule in rules:
                playbook.playbook_text += f"- {rule.description}\n"

            # Example workflow generation
            workflow = {
                "step1": {"action": "Isolate systems", "next": "step2"},
                "step2": {"action": "Scan for malware", "next": "decision1"},
                "decision1": {"condition": "If clean", "yes": "end", "no": "step3"}
            }
            playbook.workflow = workflow
            playbook.save()

            if form.is_valid():
                playbook = form.save()
                automate_response.delay(playbook.id)  # Run automation in background
            return render(request, 'generator/playbook_result.html', {'playbook': playbook})
    else:
        form = PlaybookForm()
        step_formset = CustomStepFormSet()
    return render(request, 'generator/playbook_form.html', {'form': form, 'step_formset': step_formset})


def update_metrics(request, playbook_id):
    playbook = IncidentPlaybook.objects.get(id=playbook_id)
    if request.method == 'POST':
        playbook.incident_detected_at = request.POST.get('detected_at')
        playbook.incident_fixed_at = request.POST.get('fixed_at')
        playbook.save()
    return render(request, 'generator/metrics.html', {'playbook': playbook})


def save_as_template(request, playbook_id):
    playbook = IncidentPlaybook.objects.get(id=playbook_id)
    if request.method == 'POST':
        template = PlaybookTemplate(
            name=request.POST.get('template_name'),
            incident_type=playbook.incident_type,
            template_text=playbook.playbook_text
        )
        template.save()
    return redirect('generate_playbook')