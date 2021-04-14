from app.admin import ModelAdmin, admin
from homework.models import Question


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    fields = [
        'course',
        'name',
        'text',
    ]
