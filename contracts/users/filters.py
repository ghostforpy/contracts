import django_filters

from .models import Contract


class ContractFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Contract
        fields = ["start", "end"]
