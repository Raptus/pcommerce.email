from time import time
from zope.interface import implements
from zope.component import getUtility, getMultiAdapter
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName

from pcommerce.core.interfaces import IPaymentMethod
from pcommerce.core.currency import CurrencyAware

from pcommerce.email.order import eMailPaymentOrder
from pcommerce.email import eMailPaymentMessageFactory as _

SESSION_KEY = 'pcommerce.email_orderid'

class eMailPaymentPCommercePluginUtility(object):
    implements(IPaymentMethod)

    pre_view_name = 'pcommerce_email_form'
    info_view_name = 'pcommerce_email_info'
    post_view_name = None
    
    __name__ = 'eMailPayment'

    title = _('title', default=u'On account')
    description = _('description', default=u'Payment on account')
    icon = u'++resource++pcommerce_email_icon.gif'
    logo = u'++resource++pcommerce_email_logo.gif'

    def getOrderId(self, context):
        return context.REQUEST.SESSION.get(SESSION_KEY, 0)
    
    def getOrder(self, context):
        return eMailPaymentOrder(self.getOrderId(context))
    
    def convertAmount(self, amount):
        return amount

    def startCheckout(self, context):
        """start the payment process"""
        context.REQUEST.SESSION.set(SESSION_KEY, int(time()*100))
        
    def checkout(self, context, order):
        """"""
        request = context.REQUEST
        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        address = order.billing_as_delivery and order.delivery or order.billing
        msg = translate(_('email_body', default=\
"""
New payment request by ${name}

${name} requested a payment on account for the order with id ${orderid}

Price: ${price}
VAT: ${tax}
Total incl. VAT: ${total}

Currency: ${currency}

Address informations:
Name: ${name}
Address 1: ${address1}
Address 2: ${address2}
ZIP: ${zip}
City: ${city}
Country: ${country}
Zone: ${zone}

Phone: ${phone}
eMail: ${email}

Message:
${message}

To process the payment click the following link:
${link}
""", mapping={'orderid': order.orderid,
              'price': CurrencyAware(order.price).valueToString(order.currency),
              'tax': '%s (%s %% - %s)' % (CurrencyAware(order.price_tax).valueToString(order.currency), order.tax, order.delivery.zone),
              'total': CurrencyAware(order.total).valueToString(order.currency),
              'currency': order.currency,
              'name': address.name,
              'address1': address.address1,
              'address2': address.address2,
              'zip': address.zip,
              'city': address.city,
              'country': address.country,
              'zone': address.zone,
              'phone': address.phone,
              'email': address.email,
              'message': order.message,
              'link': '%s/processEMailPCommercePayment?orderid=%s&currency=%s&price=%s&tax=%s' % (portal_state.portal_url(), order.orderid, order.currency, order.price, order.tax)}), context=request)
        mailhost = getToolByName(context, 'MailHost')
        mailhost.secureSend(msg,
                            mto=portal_state.portal().getProperty('email_from_address', ''),
                            mfrom='%s <%s>' % (address.name, address.email),
                            subject=translate(_('email_title', default='Payment request [${orderid}]', mapping={'orderid': order.orderid}), context=request),
                            charset='utf-8')
        context.REQUEST.SESSION.set(SESSION_KEY, 0)

    def cancelCheckout(self, context, order):
        """cancel the payment process"""
        return context.REQUEST.SESSION.set(SESSION_KEY, 0)

    def verifyPayment(self, context, order):
        """checks whether the payment was successfull or not"""
        request = context.REQUEST
        return order.currency == request.get('currency') and \
               order.price == float(request.get('price', 0)) and \
               order.orderid == int(request.get('orderid', 0)) and \
               order.tax == float(request.get('tax'))