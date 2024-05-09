from typing import Iterable
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail


class User(AbstractUser):
    """
    Default custom user model for Contracts.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    supervisor = models.BooleanField("Руководитель", default=False)
    it_staff = models.BooleanField("IT персонал", default=False)

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def __str__(self) -> str:
        # r = super().__str__()
        # if self.get_full_name():
        #     r = self.get_full_name()
        return self.name or super().__str__()


class Company(models.Model):
    name = models.CharField("Наименование", max_length=50, unique=True)

    class Meta:
        verbose_name_plural = _("Компании")
        verbose_name = _("Компания")

    def __str__(self) -> str:
        return self.name


class Town(models.Model):
    name = models.CharField("Наименование", max_length=50, unique=True)

    class Meta:
        verbose_name_plural = _("Города")
        verbose_name = _("Город")

    def __str__(self) -> str:
        return self.name


class Contract(models.Model):
    number = models.BigIntegerField("Номер контракта")
    object = models.CharField("Наименование объекта", max_length=150)
    state = models.CharField(
        "Статус",
        max_length=50,
        choices=[
            ("in_process", "В процессе"),
            ("restored", "Восстановлен"),
            ("contract_organization", "Организация контракта"),
        ],
        default="in_process",
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name="Предприятие"
    )
    town = models.ForeignKey(Town, on_delete=models.CASCADE, verbose_name="Город")
    description = models.TextField("Описание работ")
    start = models.DateField("Дата начала работ", blank=True, null=True)
    end = models.DateField("Плановая дата окончания работ", blank=True, null=True)
    creator = models.ForeignKey(
        User,
        verbose_name="Создатель",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_contracts",
        editable=False,
    )
    gip = models.ForeignKey(
        User,
        verbose_name="Руководитель",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="gip_contracts",
    )
    users = models.ManyToManyField(
        User,
        blank=True,
        null=True,
        verbose_name="Пользователи",
        related_name="contracts",
    )
    ada = models.BooleanField(default=False)
    mpe = models.BooleanField(default=False)
    mpm = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = _("Контракты")
        verbose_name = _("Контракт")

    def __str__(self) -> str:
        return f"Контракт №{self.number}"

    def get_absolute_url(self):
        return reverse("contracts:contract-detail", kwargs={"pk": self.pk})

    def get_admin_url(self):
        return reverse(
            "admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name),
            args=(self.id,),
        )


class UserContractFolders(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="contract_folders",
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        verbose_name="Контракт",
        related_name="user_folders",
    )
    ada = models.BooleanField(default=False)
    mpe = models.BooleanField(default=False)
    mpm = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = _("Доступы к директориям")
        verbose_name = _("Доступы к директориям")

    # def __str__(self) -> str:
    #     return f"Контракт №{self.number}"


class PermissionRequest(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="permission_requests",
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        verbose_name="Контракт",
        related_name="permission_requests",
    )
    ada = models.BooleanField(default=False)
    mpe = models.BooleanField(default=False)
    mpm = models.BooleanField(default=False)
    creator = models.ForeignKey(
        User,
        verbose_name="Создатель",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_permission_requests",
        editable=False,
    )
    created = models.DateTimeField("Создано", auto_now_add=True)
    done = models.DateTimeField("Исполнено", null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Заявки")
        verbose_name = _("Заявка")

    def save(self, *args, **kwargs) -> None:
        s = super().save(*args, **kwargs)
        send_mail(
            "Новая заявка",
            f"http://0.0.0.0:8000{self.contract.get_absolute_url()}\nhttp://0.0.0.0:8000{self.contract.get_admin_url()}",
            "from@example.com",
            ["to@example.com"],
            fail_silently=False,
        )
        return s

    def get_admin_url(self):
        return reverse(
            "admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name),
            args=(self.id,),
        )
