# -*- encoding: utf-8 -*-

from paypal.standard.pdt.models import PayPalPDT
from paypal.standard.pdt.forms import PayPalPDTForm


def pdt(f):
    """Parses out GET parameters corresponding to a paypal PDT request and adds `pdt_active`, `pdt_failed` and `pdt` to the call **kwargs.

    Payment data transfer implementation: http://tinyurl.com/c9jjmw"""

    def aux(request, *args, **kwargs):
        if request.method == 'POST':
            return f(request, *args, **kwargs) 
        
        pdt_obj = None
        pdt_active = False
        txn_id = request.GET.get('tx')
        failed = False
        if txn_id is not None:
            pdt_active = True
            # If an existing transaction with the id tx exists: use it
            try:
                pdt_obj = PayPalPDT.objects.get(txn_id=txn_id)
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

        kwargs.update({'pdt_active': pdt_active, 'pdt_failed': failed, 'pdt_obj': pdt_obj})
        return f(request, *args, **kwargs)
    
    return aux
