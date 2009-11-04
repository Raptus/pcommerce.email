from zope.component import getUtility
from zope.interface import implements
from zope.i18n import translate
from Products.Five.browser import BrowserView

from pcommerce.core.interfaces import IPaymentProcessor, IProcessView, IPaymentMethod

from pcommerce.email import eMailPaymentMessageFactory as _

class ProcessEMailPCommercePayment(BrowserView):
    """process eMail payments
    """
    implements(IProcessView)

    def __call__(self):
        processor = IPaymentProcessor(self.context)
        utility = getUtility(IPaymentMethod, name='eMailPayment')
        return translate(_(processor.processPayment(self, utility)), context=self.request)
        
    def getOrderId(self):
        return int(self.request.get('orderid'))