from django.conf.urls import url, patterns
from django.contrib.auth.decorators import login_required

from .views import StatementView


urlpatterns = patterns('statement.views',
    url(r'^$', login_required(StatementView.as_view()) , name='statements'),
)
