from Acquisition import aq_inner

from zope.component import getUtility, getMultiAdapter
from zope.interface import implements
from zope.i18n import translate

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone import PloneMessageFactory as _

from pcommerce.core.currency import CurrencyAware
from pcommerce.core.address import Address
from pcommerce.core.interfaces import IPaymentMethod, IOrderRegistry, IPreOrderView, ITaxes

class EMailPaymentInfo(BrowserView):
    """eMail payment form
    """
    implements(IPreOrderView)
    template = ViewPageTemplateFile('templates/email_info.pt')

    def __call__(self):
        utility = getUtility(IPaymentMethod, name=u'eMailPayment')
        registry = IOrderRegistry(self.context)
        orderid = utility.getOrderId(self.context)
        self.order = registry[orderid]
        return self.template()
    
    @property
    @memoize
    def address(self):
        return self.order.billing_as_delivery and self.order.delivery or self.order.billing
    
    @property
    @memoize
    def message(self):
        return self.order.message
        
        