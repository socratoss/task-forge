from django.db import models


class IndustryChoices(models.TextChoices):
    IT = "IT", "IT"
    MARKETING = "Marketing", "Marketing"
    EDUCATION = "Education", "Education"
    HEALTHCARE = "Healthcare", "Healthcare"
    FINANCE = "Finance", "Finance"
    OTHER = "Other", "Other"


class RoleChoices(models.TextChoices):
    MEMBER = "member", "Member"
