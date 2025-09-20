"""Price views"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from eveuniverse.models import EveType

from metenox.prices import MOON_GOOS_GROUP_ID, get_fuels_type_ids
from metenox.views.general import add_common_context


@login_required
def prices(request):
    """Displays moon goo prices"""
    # TODO rewrite the template
    eve_types = list(EveType.objects.filter(eve_group__id=MOON_GOOS_GROUP_ID))
    eve_types.extend(EveType.objects.filter(id__in=get_fuels_type_ids()))
    return render(
        request,
        "metenox/prices.html",
        add_common_context(
            {
                "eve_types": eve_types,
            }
        ),
    )
