# Django DRF Academy - Разграничение прав доступа и авторизация

## Контекст

Для разграничения прав доступа в любом сервисе используются настройки, которые в DRF предоставляет пакет `permissions`.
Задача разграничения прав доступа — очень частая в рамках работы над растущими и развивающимися проектами.

Продолжаем работать с проектом. Переходим к описанию прав доступа и авторизации пользователей.

---

## Критерий выполнения

✅ Результат всех заданий залит на GitHub и сдан в виде ссылки на репозиторий.

---

## Чек-лист заданий

### Задание 1: JWT-авторизация и CRUD пользователей

- [x] Реализовать CRUD для пользователей
- [x] Реализовать регистрацию пользователей
- [x] Настроить JWT-авторизацию в проекте
- [x] Закрыть все эндпоинты авторизацией
- [x] Оставить доступными эндпоинты авторизации и регистрации для неавторизованных пользователей
- [x] Протестировать через Postman

### Задание 2: Группа модераторов

- [x] Создать группу модераторов
- [x] Создать класс разрешений для модераторов в `permissions.py`
- [x] Реализовать проверку через `has_permission()`
- [x] Создать фикстуру или кастомную команду для групп
- [x] Настроить права для ViewSet через `get_permissions()`
- [x] Разрешить модераторам просмотр и редактирование уроков и курсов
- [x] Запретить модераторам создание и удаление уроков и курсов
- [x] Протестировать через Postman

### Задание 3: Права доступа для владельцев объектов

- [x] Добавить поле владельца в модели курсов и уроков
- [x] Создать и применить миграции
- [x] Создать класс разрешений `IsOwner` в `permissions.py`
- [x] Реализовать автопривязку объектов через `perform_create()`
- [x] Настроить права доступа с логическими операторами
- [x] Разрешить пользователям видеть, редактировать и удалять только свои объекты
- [x] Протестировать через Postman

---

## Задание 1: JWT-авторизация и CRUD пользователей

### Описание

Реализуйте CRUD для пользователей, в том числе регистрацию пользователей, настройте в проекте использование
JWT-авторизации и закройте каждый эндпоинт авторизацией.

### Требования

- Эндпоинты для авторизации и регистрации должны остаться доступны для неавторизованных пользователей
- Все остальные эндпоинты должны быть закрыты авторизацией

---

## Задание 2: Группа модераторов

### Описание

Заведите группу модераторов и опишите для нее права работы с любыми уроками и курсами, но без возможности их удалять и
создавать новые.

### Требования

- Модератор может **просматривать и редактировать** любые уроки и курсы
- Модератор **не может удалять и создавать** уроки и курсы

### Подсказки

#### 1. Создание класса разрешений для модераторов

Заведите отдельный класс в `permissions.py`:

```python
from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Moderators').exists()
```

#### 2. Создание фикстуры для групп

Создайте группу через админ-панель, затем выгрузите фикстуру:

```bash
python manage.py dumpdata auth.group --indent 2 > users/fixtures/groups.json
```

Загрузка фикстуры:

```bash
python manage.py loaddata users/fixtures/groups.json
```

#### 3. Разграничение прав во ViewSet

Используйте метод `get_permissions()` для разделения прав по actions:

```python
def get_permissions(self):
    if self.action == 'create':
        self.permission_classes = [IsAuthenticated, ~IsModerator]
    elif self.action in ['list', 'retrieve', 'update', 'partial_update']:
        self.permission_classes = [IsAuthenticated]
    elif self.action == 'destroy':
        self.permission_classes = [IsAuthenticated, ~IsModerator]
    return [permission() for permission in self.permission_classes]
```

**Список actions ViewSet:**

- `list` - GET /resource/
- `create` - POST /resource/
- `retrieve` - GET /resource/{id}/
- `update` - PUT /resource/{id}/
- `partial_update` - PATCH /resource/{id}/
- `destroy` - DELETE /resource/{id}/

[Документация по ViewSet actions](https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions)

[Документация по get_permissions()](https://www.django-rest-framework.org/api-guide/viewsets/#introspecting-viewset-actions)

#### 4. Настройка прав для Generic Views

Для закрытия контроллера для неавторизованных пользователей:

```python
class SomeListAPIView(generics.ListAPIView):
    # ...
    permission_classes = [IsAuthenticated]
```

Для разрешения доступа только модераторам:

```python
class SomeListAPIView(generics.ListAPIView):
    # ...
    permission_classes = [IsAuthenticated, IsModerator]
```

[Документация по настройке permissions](https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy)

---

## Задание 3: Права доступа для владельцев объектов

### Описание

Опишите права доступа для объектов таким образом, чтобы пользователи, которые не входят в группу модераторов, могли
видеть, редактировать и удалять только свои курсы и уроки.

### Требования

- Пользователи (не модераторы) могут работать только со своими объектами
- Модераторы могут работать с любыми объектами

### Подсказки

#### 1. Добавление поля владельца в модель

Добавьте поле в модели курсов и уроков:

```python
from django.conf import settings


class Course(models.Model):
    # ...
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец'
    )
```

**Не забудьте выполнить миграции:**

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 2. Автоматическая привязка объекта к пользователю

Используйте метод `perform_create()`:

```python
class LessonCreateAPIView(generics.CreateAPIView):
    # ...

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

Этот метод также работает во ViewSet с идентичной логикой.

[Документация - Save and deletion hooks](https://www.django-rest-framework.org/api-guide/generic-views/#methods)

#### 3. Создание класса разрешений IsOwner

```python
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
```

#### 4. Логические операторы для комбинирования прав

DRF поддерживает логические операторы:

- `&` — логическое И (AND)
- `|` — логическое ИЛИ (OR)
- `~` — логическое отрицание (NOT)

**Пример 1:** Доступ для авторизованных пользователей, кроме модераторов:

```python
class SomeListAPIView(generics.ListAPIView):
    # ...
    permission_classes = [IsAuthenticated, ~IsModerator]
```

**Пример 2:** Доступ для модераторов ИЛИ владельцев объектов:

```python
class SomeRetrieveAPIView(generics.RetrieveAPIView):
    # ...
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]
```

**Пример 3:** Настройка прав во ViewSet:

```python
def get_permissions(self):
    if self.action in ['update', 'partial_update', 'destroy']:
        self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
    elif self.action == 'create':
        self.permission_classes = [IsAuthenticated, ~IsModerator]
    else:
        self.permission_classes = [IsAuthenticated]
    return [permission() for permission in self.permission_classes]
```

---

## Важные напоминания

1. Группы назначайте пользователям через админ-панель
2. Всегда проверяйте работоспособность через Postman
3. Не забывайте выполнять и пушить миграции при изменении моделей
4. Тестируйте разные сценарии: авторизованные/неавторизованные пользователи, модераторы, владельцы объектов

---

## Полезные ссылки

- [DRF ViewSet Actions](https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions)
- [DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [DRF Generic Views - Hooks](https://www.django-rest-framework.org/api-guide/generic-views/#methods)