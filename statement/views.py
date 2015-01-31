from datetime import datetime

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.db.models import Q
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from product.models import Product, Comment
from .forms import StatementForm


class StatementView(ListView):
    template_name = 'statement/main.html'
    form_class = StatementForm
    # paginate_by = PRODUCTS_PER_PAGE

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super(StatementView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('product-list'))

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        if self.request.GET:
            form = self.form_class(data=self.request.GET)
        else:
            form = self.form_class()

        context['form'] = form

        if form.is_valid():
            context['report'] = self.get_report_sum()

        return context

    def get_queryset(self):
        return Product.objects.get_for_report(self.request.GET)

    def get_report_sum(self):
        if self.request.GET:
            data = Comment.objects.filter(product__in=self.get_queryset()).aggregate(soft=Sum('software'), hard=Sum('hardware'), tran=Sum('transport'))
            total = 0.00
            for key, value in data.items():
                val = float(value) if value is not None else 0.00
                data[key] = val
                total += val
            data['sum'] = total
            return data
        return None
