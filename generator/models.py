from django.db import models

class IncidentPlaybook(models.Model):
    INCIDENT_TYPES = (
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('ddos', 'DDoS'),
        ('databreach', 'Data Breach'),
    )
    
    SEVERITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    affected_systems = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    playbook_text = models.TextField(blank=True)  # Generated playbook content
    workflow = models.JSONField(default=dict, blank=True) # e.g., {"step1": {"action": "Isolate", "next": "step2"}}
    incident_detected_at = models.DateTimeField(null=True, blank=True)
    incident_fixed_at = models.DateTimeField(null=True, blank=True)

    def mttd(self):  # Mean Time To Detect
        if self.incident_detected_at and self.created_at:
            return (self.incident_detected_at - self.created_at).total_seconds() / 60  # Minutes
        return None

    def mttf(self):  # Mean Time To Fix
        if self.incident_fixed_at and self.incident_detected_at:
            return (self.incident_fixed_at - self.incident_detected_at).total_seconds() / 60
        return None

    def __str__(self):
        return f"{self.incident_type} - {self.severity}"


class CustomStep(models.Model):
    playbook = models.ForeignKey(IncidentPlaybook, on_delete=models.CASCADE, related_name='custom_steps')
    step_description = models.TextField()
    step_order = models.IntegerField(default=0)  # For sorting steps

    def __str__(self):
        return f"Step {self.step_order}: {self.step_description[:20]}"


class DecisionPoint(models.Model):
    playbook = models.ForeignKey(IncidentPlaybook, on_delete=models.CASCADE, related_name='decision_points')
    condition = models.CharField(max_length=200)  # e.g., "If malware spreads to >10 systems"
    action = models.TextField()  # e.g., "Escalate to senior team"

    def __str__(self):
        return self.condition


class ComplianceRule(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    applicable_incidents = models.CharField(max_length=20, choices=IncidentPlaybook.INCIDENT_TYPES)

    def __str__(self):
        return self.name


class PlaybookTemplate(models.Model):
    name = models.CharField(max_length=100)
    incident_type = models.CharField(max_length=20, choices=IncidentPlaybook.INCIDENT_TYPES)
    template_text = models.TextField()
    created_by = models.CharField(max_length=100)  # Or link to Django User model

    def __str__(self):
        return self.name