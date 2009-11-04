from zope.interface import implements

from pcommerce.core.order import Order
from pcommerce.core.interfaces import IOrder

class eMailPaymentOrder(Order):
    """"""
    implements(IOrder)
    
    billing = None
    billing_as_delivery = True
    message = ''
    
    def __init__(self,
                 orderid,
                 userid='',
                 price=0.0,
                 currency='',
                 date=None,
                 zone=None,
                 products=[],
                 delivery=None,
                 billing=None,
                 billing_as_delivery=True,
                 message=''):
        """"""
        Order.__init__(self, orderid, userid, price, currency, date, zone, products, delivery)
        self.billing = billing
        self.billing_as_delivery = billing_as_delivery
        self.message = message
    
    