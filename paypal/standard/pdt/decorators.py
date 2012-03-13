# -*- encoding: utf-8 -*-

from paypal.standard.pdt.models import PayPalPDT
from paypal.standard.pdt.forms import PayPalPDTForm
from django.views.decorators.http import require_GET

def pdt(dummy=None, item_check_callable=None):
    """Parses out GET parameters corresponding to a paypal PDT request and adds `pdt_active`, `pdt_failed` and `pdt` to the call **kwargs.

    Payment data transfer implementation: http://tinyurl.com/c9jjmw

    `item_check_callable` (Optional) is a callable that must take an instance of PayPalPDT
    as a parameter and return a tuple (False, None) if the item is valid. Should return (True, "reason")
    if the item isn't valid. This function should check that `mc_gross`, `mc_currency` `item_name` and
    `item_number` are all correct.

    `dummy` DO NOT set value for this. So when you want to set value for `item_check_callable` use named param.
    So it would be @pdt(item_check_callable=func). When the `dummy` is a callable `f` then it behaves as just @pdt(f).
    """

    def inner_pdt(f):
    #{
        @require_GET
        def aux(request, *args, **kwargs):
            pdt_obj = None
            pdt_active = False
            txn_id = request.GET.get('tx', None)
            if txn_id is not None:
                txn_id = txn_id.strip()
                if not txn_id: #i.e. empty txn_id
                    txn_id = None
            
            failed = False
            pdt_duplicate = False
            if txn_id is not None:
                pdt_active = True
                # If an existing transaction with the id tx exists: use it
                try:
                    pdt_obj = PayPalPDT.objects.get(txn_id=txn_id)
                    pdt_duplicate = True
                except PayPalPDT.DoesNotExist:
                    # This is a new transaction so we continue processing PDT request
                    pass

                if pdt_obj is None:
                    form = PayPalPDTForm(request.GET)
                    if form.is_valid():
                        try:
                            pdt_obj = form.save(commit=False)
                        except Exception, e:
                            error = repr(e)
                            failed = True
                    else:
                        error = form.errors
                        failed = True

                    if failed:
                        pdt_obj = PayPalPDT()
                        pdt_obj.set_flag("Invalid form. %s" % error)

                    pdt_obj.initialize(request)

                    if not failed:
                        # The PDT object gets saved during verify
                        pdt_obj.verify(item_check_callable)
            else:
                pass # we ignore any PDT requests that don't have a transaction id
    
            #pdt_active = True => txn_id was not None
            #pdt_failed = True => pdt_obj has invalid data
            #pdt_duplicate = True => txn_id is known and already processed. pdt_obj contains that data.
            kwargs.update({'pdt_active': pdt_active, 'pdt_failed': failed, 'pdt_obj': pdt_obj, 'pdt_duplicate': pdt_duplicate})
            return f(request, *args, **kwargs)
    
        return aux
    #}
    if hasattr(dummy, '__call__'): #This is to make sure that we can call @pdt without any parenthesis.
        return inner_pdt(dummy) #dummy is function now
    else:
        return inner_pdt
