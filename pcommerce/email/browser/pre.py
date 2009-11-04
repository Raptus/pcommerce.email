import re
from Acquisition import aq_inner

from zope.component import getUtility, getMultiAdapter
from zope.interface import implements
from zope.i18n import translate

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _

from Products.validation.validators.BaseValidators import EMAIL_RE
email_re = re.compile(EMAIL_RE)

from pcommerce.core.address import Address
from pcommerce.core.interfaces import IPaymentMethod, IOrderRegistry, IPreOrderView, ITaxes

class EMailPaymentForm(BrowserView):
    """eMail payment form
    """
    implements(IPreOrderView)
    template = ViewPageTemplateFile('templates/email_form.pt')
    required = ('name', 'address1', 'city', 'country',)
    errors = {}

    def __call__(self):
        if not self.request.get('pcommerce.pre', 0):
            self.request.form = {}
            self.as_delivery = self.order.billing_as_delivery
        else:
            self.as_delivery = self.request.get('as_delivery', 0)
        return self.template()
    
    def process(self, order):
        if self.request.get('as_delivery', 0):
            order.billing_as_delivery = True
        else:
            order.billing_as_delivery = False
            order.billing = Address(name=self.request.get('name').decode('utf-8'),
                                    address1=self.request.get('address1').decode('utf-8'),
                                    address2=self.request.get('address2', '').decode('utf-8'),
                                    zip=self.request.get('zip', '').decode('utf-8'),
                                    city=self.request.get('city').decode('utf-8'),
                                    country=self.request.get('country').decode('utf-8'),
                                    zone=self.request.get('zone', '').decode('utf-8'),
                                    email=self.request.get('email', '').decode('utf-8'),
                                    phone=self.request.get('phone', '').decode('utf-8'))
        order.message = self.request.get('message', '').decode('utf-8')
        
    @property
    @memoize
    def order(self):
        utility = getUtility(IPaymentMethod, name=u'eMailPayment')
        registry = IOrderRegistry(self.context)
        orderid = utility.getOrderId(self.context)
        return registry[orderid]
    
    @property
    @memoize
    def address(self):
        return self.order.billing_as_delivery and self.order.delivery or self.order.billing
    
    @property
    @memoize
    def zones(self):
        taxes = ITaxes(self.context)
        return [{'name': name,
                 'tax': tax} for name, tax in taxes.items()]
    
    @memoize
    def getMemberInfo(self):
        mship = getToolByName(self.context, 'portal_membership')
        return mship.getMemberInfo()
    
    def validate(self, order):
        self.errors = {}
        if self.request.get('as_delivery', 0):
            if order.delivery:
                return True
        for field in self.required:
            if not self.request.get(field, ''):
                self.errors[field] = _(u'This field is required, please provide some information.')
        if self.request.get('email', 0):
            if not email_re.match(self.request.get('email', '')):
                self.errors['email'] = _(u'Please submit a valid email address.')
        return len(self.errors) == 0
        
        