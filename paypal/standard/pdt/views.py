#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.http import require_GET
from paypal.standard.pdt.decorators import pdt 
 
@require_GET
@pdt
def pdt(request, pdt_active=True, pdt_failed=False, pdt_obj=None, template="pdt/pdt.html", context=None):
    """Payment data transfer implementation: http://tinyurl.com/c9jjmw"""
    context = context or {} 
    context.update({"failed":pdt_failed, "pdt_obj":pdt_obj})
    return render_to_response(template, context, RequestContext(request))
