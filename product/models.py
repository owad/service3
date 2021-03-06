# -* - coding: utf-8 -*-
from decimal import Decimal

from django.utils import timezone
from django.utils.timezone import timedelta
from django.db import models
from django.db.models import Sum, Count


from person.models import User, Client
from django.conf import settings

from .managers import OutdatedManager


class Courier(models.Model):
    name = models.CharField(max_length='64')

    class Meta:
        verbose_name_plural = "kurierzy"
        verbose_name = "kurier"

    def __unicode__(self):
        return self.name


class Product(models.Model):
    DECIMAL_ZERO = '0.00'
    NEW, PROCESSING, COURIER = ('przyjety', 'w_realizacji', 'do_wyslania')
    EXTERNAL, BACK, READY, CLOSED = ('w_serwisie', 'z_serwisu', 'do_wydania', 'wydany')
    STATUSES = (NEW, PROCESSING, COURIER, EXTERNAL, BACK, READY, CLOSED)

    NEW_NICE, PROCESSING_NICE, COURIER_NICE = ('przyjęty', 'w realizacji', 'do wysłania')
    EXTERNAL_NICE, BACK_NICE, READY_NICE, CLOSED_NICE = (
    'w serwisie zew.', 'odebrano z serwisu zew.', 'do wydania', 'wydany')
    STATUS_CHOICES = (
        (NEW, NEW_NICE),
        (PROCESSING, PROCESSING_NICE),
        (COURIER, COURIER_NICE),
        (EXTERNAL, EXTERNAL_NICE),
        (BACK, BACK_NICE),
        (READY, READY_NICE),
        (CLOSED, CLOSED_NICE)
    )

    IN_PROGRESS = (PROCESSING, COURIER, EXTERNAL, BACK, READY)

    FIRST_STATUS = NEW
    LAST_STATUS = CLOSED

    Y, N = ('Y', 'N')
    Y_NICE, N_NICE = ('Tak', 'Nie')
    WARRANTY_CHOICES = (
        (N, N_NICE),
        (Y, Y_NICE)
    )

    name = models.CharField(max_length=128, verbose_name='nazwa')
    producent = models.CharField(max_length=128, blank=True, verbose_name='producent')
    serial = models.CharField(max_length=128, blank=True, verbose_name='numer seryjny')
    invoice = models.CharField(max_length=128, blank=True, verbose_name='numer faktury')
    description = models.TextField(verbose_name='opis usterki')
    additional_info = models.TextField(verbose_name='informacje dodatkowe', blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=32)
    parcel_number = models.CharField(max_length=64, blank=True, verbose_name='numer przesyłki')
    external_service_name = models.CharField(max_length=128, blank=True, verbose_name='nazwa serwisu zewnętrznego')
    max_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='koszt naprawy do',
                                   default=DECIMAL_ZERO)
    warranty = models.CharField(choices=WARRANTY_CHOICES, max_length=16, verbose_name='gwarancja')
    courier = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='data zgłoszenia')
    updated = models.DateTimeField(auto_now=True, verbose_name='ostatnia akutalizajca')

    user = models.ForeignKey(User, verbose_name='pracownik')
    fixed_by = models.IntegerField(null=True, blank=True, verbose_name='wykonane przez')
    client = models.ForeignKey(Client, verbose_name='klient')

    objects = OutdatedManager()

    class Meta:
        verbose_name_plural = "zgłoszenia"
        verbose_name = "zgłoszenie"
        ordering = ['-created']

    def get_next_status(self):
        break_on_next = False
        next_status = self.FIRST_STATUS
        if self.status == self.LAST_STATUS: return self.LAST_STATUS
        if self.status == '':
            return self.FIRST_STATUS
        else:
            for key, status in self.STATUS_CHOICES:
                if (break_on_next):
                    next_status = key
                    break;
                if key == self.status: break_on_next = True
            return next_status

    def set_next_status(self, request):
        old_status = self.status
        POST = request.POST
        if 'status_change' in POST and int(POST['status_change']) == 1 and self.status == self.PROCESSING:
            self.status = Product.READY
        else:
            self.status = self.get_next_status()
        if old_status == self.COURIER:
            self.parcel_number = POST['parcel_number']
            self.courier = POST['courier']
        return self.status

    def get_status_name(self, status=None):
        if status:
            key = status
        else:
            key = self.status
        for statuses in self.STATUS_CHOICES:
            if key == statuses[0]:
                return statuses[1]
        return self.FIRST_STATUS

    def get_next_status_name(self):
        return self.get_status_name(self.get_next_status())

    def get_next_status_name_no_external(self):
        if self.status == self.PROCESSING:
            key = self.READY
        else:
            key = self.status
        return self.get_status_name(status=key)

    def get_hardware_cost(self):
        return self.comment_set.aggregate(sum=Sum('hardware'))['sum'] or Decimal(0)

    def get_software_cost(self):
        return self.comment_set.aggregate(sum=Sum('software'))['sum'] or Decimal(0)

    def get_transport_cost(self):
        return self.comment_set.aggregate(sum=Sum('transport'))['sum'] or Decimal(0)

    def get_cost(self):
        return self.get_hardware_cost() + self.get_software_cost() + self.get_transport_cost()

    def get_cost_totals(self):
        costs = []
        if self.get_hardware_cost():
            costs.append('sprzęt: %szł' % (self.get_hardware_cost(),))
        if self.get_software_cost():
            costs.append('usługa: %szł' % (self.get_software_cost(),))
        if self.get_transport_cost():
            costs.append('dojazd: %szł' % (self.get_transport_cost(),))
        if costs:
            return '(' + ', '.join(costs) + ')'
        return ''

    def get_warranty_name(self):
        if self.warranty == self.N:
            return self.N_NICE
        else:
            return self.Y_NICE

    def save(self, *args, **kwargs):
        if self.warranty is None: self.warranty = self.N
        if self.status is None: self.status = self.FIRST_STATUS
        super(Product, self).save(*args, **kwargs)

    def get_counts(self):
        result = Product.objects.values('status').annotate(count=Count('status'))
        counts = {}
        all = 0
        for status in Product.STATUSES:
            counts[status] = 0
            for row in result:
                if status == row['status']:
                    counts[status] = row['count']
            all += counts[status]
        counts['wszystkie'] = all
        return counts

    def get_alert(self):
        if self.updated_by_someone():
            return '#33ff33'
        if timezone.now() - timedelta(days=10) > self.updated and self.status == self.EXTERNAL:
            return '#ff6666'
        if timezone.now() - timedelta(days=7) > self.updated \
                and self.status in (self.READY,):
            return '#ff3333'
        if timezone.now() - timedelta(days=3) > self.updated \
                and self.status in (self.NEW, self.PROCESSING, self.COURIER):
            return '#ff0000'
        return ''

    def get_signature(self):
        return '/'.join([str(self.id), str(self.created.year)])

    def get_owner(self):
        try:
            return Comment.objects.filter(product=self,
                                          status=Product.PROCESSING,
                                          type=Comment.STATUS_CHANGE)[0].user
        except:
            return None

    def get_owner_name(self):
        user = self.get_owner()
        if user:
            return user.get_full_name()
        return '-'

    def get_processing_date(self):
        return self.get_by_comment_status(Product.PROCESSING)

    def get_ready_date(self):
        return self.get_by_comment_status(Product.READY)

    def get_out_date(self):
        return self.get_by_comment_status(Product.CLOSED)

    def get_processing_user(self):
        try:
            return self.get_by_comment_status(Product.PROCESSING, 'user').get_full_name()
        except:
            return '-'

    def get_ready_user(self):
        try:
            return self.get_by_comment_status(Product.READY, 'user').get_full_name()
        except:
            return '-'

    def get_out_user(self):
        try:
            return self.get_by_comment_status(Product.CLOSED, 'user').get_full_name()
        except:
            return '-'

    def get_by_comment_status(self, status_value, field='created'):
        try:
            return getattr(Comment.objects.get(product=self, status=status_value, type=Comment.STATUS_CHANGE), field)
        except:
            return '-'

    def get_last_update_user(self):
        try:
            return Product.objects.get(pk=self.id).comment_set.order_by('-created')[0].user
        except:
            return None

    def updated_by_someone(self):
        '''
        if self.status != Product.PROCESSING:
            return False

        last_user = self.get_last_update_user()
        owner = self.get_owner()
        current_user = get_request().user
        if owner and last_user and current_user:
            if last_user.id != owner.id:
                if current_user.id == owner.id:
                    return True
        '''
        return False

    def __unicode__(self):
        return self.name


class Comment(models.Model):
    COMMENT, STATUS_CHANGE, HARDWARE_ADD = ('komentarz', 'zmiana_statusu', 'sprzet')
    COMMENT_NICE, STATUS_CHANGE_NICE, HARDWARE_ADD_NICE = ('komenatrz', 'zmiana statusu', 'sprzęt')
    TYPES = (
        (COMMENT, COMMENT_NICE),
        (STATUS_CHANGE, STATUS_CHANGE_NICE),
        (HARDWARE_ADD, HARDWARE_ADD_NICE)
    )

    DECIMAL_ZERO = '0.00'

    note = models.TextField(verbose_name='notatka')
    type = models.CharField(choices=TYPES, max_length=32, verbose_name='typ')
    status = models.CharField(choices=Product.STATUS_CHOICES, blank=True, max_length=32)
    hardware = models.DecimalField(max_digits=10, decimal_places=2, default=DECIMAL_ZERO, verbose_name='koszt sprzętu')
    software = models.DecimalField(max_digits=10, decimal_places=2, default=DECIMAL_ZERO, verbose_name='koszt usługi')
    transport = models.DecimalField(max_digits=10, decimal_places=2, default=DECIMAL_ZERO, verbose_name='koszt dojazdu')
    created = models.DateTimeField(auto_now_add=True, verbose_name='data zgłoszenia')

    user = models.ForeignKey(User, verbose_name='pracownik')
    product = models.ForeignKey(Product, verbose_name='produkt')

    class Meta:
        verbose_name_plural = "komentarze"
        verbose_name = "komentarz"
        ordering = ['-created']

    def save(self, *args, **kwargs):
        if self.hardware is None: self.hardware = self.DECIMAL_ZERO
        if self.software is None: self.software = self.DECIMAL_ZERO
        if self.transport is None: self.transport = self.DECIMAL_ZERO
        super(Comment, self).save(*args, **kwargs)

    def set_comment_type(self, type_id):
        if float(self.hardware) > 0.0:
            self.type = self.HARDWARE_ADD
        elif type_id > 0:
            self.type = self.STATUS_CHANGE
        else:
            self.type = self.COMMENT

    def get_status_name(self):
        for statuses in Product.STATUS_CHOICES:
            if self.status == statuses[0]:
                return statuses[1]

    def __unicode__(self):
        return self.note


class File(models.Model):
    product = models.ForeignKey(Product, blank=True)
    obj = models.FileField(upload_to=settings.UPLOAD_URL, verbose_name='plik', blank=True)
    title = models.CharField(max_length=100, verbose_name='nazwa', blank=True)

    def get_file_name(self):
        chunks = self.obj.path.split('/')
        if chunks:
            return chunks[-1]
        else:
            return self.id

    def get_extension(self):
        chunks = self.obj.path.split('.')
        if chunks:
            return chunks[-1]
        else:
            return 'unknown'

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.get_file_name()
