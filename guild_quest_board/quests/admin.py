from django.contrib import admin

from .models import Quest, QuestType, QuestReport


admin.site.empty_value_display = 'Не задано'


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    """
    Модель квестов в админке.

    Настройки интерфейса:
    - list_display: вид в таблице списка пользователей;
    - list_filter: поля для фильтрации;
    - search_fields: поля для поиска;
    - ordering: поля для сортировки списка.

    Значения полей:
    * name - название квеста;
    * min_level - минимальный уровень авантюриста;
    * status - статус квеста;
    * description - описание квеста;
    * reward - награда за выполнение квеста.
    """

    list_display = ('name', 'description', 'min_level', 'reward', 'status')
    search_fields = ('name', 'min_level', 'status')
    list_filter = ('name',)
    ordering = ('name',)


@admin.register(QuestType)
class QuestTypeAdmin(admin.ModelAdmin):
    """
    Модель типов квестов в админке.

    Настройки интерфейса:
    - list_display: вид в таблице списка пользователей;
    - list_filter: поля для фильтрации;
    - search_fields: поля для поиск;
    - ordering: поля для сортировки списка.

    Значения полей:
    * name - название квеста;
    * description - описание квеста;
    """

    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)


@admin.register(QuestReport)
class QuestReportAdmin(admin.ModelAdmin):
    """
    Модель отчетов квестов в админке.

    Настройки интерфейса:
    - list_display: вид в таблице списка пользователей;
    - list_filter: поля для фильтрации;
    - search_fields: поля для поиск;
    - ordering: поля для сортировки списка.

    Значения полей:
    * result - результат выполнения квеста;
    * comment - комментарий к квесту;
    * quest - квест.
    """

    list_display = ('result', 'comment', 'quest')
    search_fields = ('result',)
    list_filter = ('result',)
    ordering = ('comment',)
