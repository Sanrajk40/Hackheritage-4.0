from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import render,redirect
from globalapp.models import DEL_pass,BOM_pass,CCU_pass

def addpass(request):
    if request.method =='POST':
        data= json.loads(request.body)
        v= data.get('value')
        add = redirect('addToBlock')
        request.session['pass_detail']={data}
        if v==5:
            return redirect('delpass')
        elif v==4:
            return redirect('bompass')
        elif v==3:
            return redirect('ccupass')

    else:
        return JsonResponse({'status':'error','value':10})


def delpass(request):
    pass_info= request.session.get('pass_detail',{})
    empid = pass_info.get('empid')
    empname= pass_info.get('empname')
    passport=pass_info.get('passport')
    name=pass_info.get('name')
    nationality=pass_info.get('nationality')
    visa=pass_info.get('visa')
    # later add date and time
    passenger=DEL_pass.objects.create(empid=empid,empname=empname,pas_name=name,passport_no=make_password(passport),nationality=nationality,visa_no=make_password(visa))
    return JsonResponse({'status':'success','value':10})

def bompass(request):
    pass_info= request.session.get('pass_detail',{})
    empid = pass_info.get('empid')
    empname= pass_info.get('empname')
    passport=pass_info.get('passport')
    name=pass_info.get('name')
    nationality=pass_info.get('nationality')
    visa=pass_info.get('visa')
    # later add date and time
    passenger=BOM_pass.objects.create(empid=empid,empname=empname,pas_name=name,passport_no=make_password(passport),nationality=nationality,visa_no=make_password(visa))
    return JsonResponse({'status':'success','value':9})

def ccupass(request):
    pass_info= request.session.get('pass_detail',{})
    empid = pass_info.get('empid')
    empname= pass_info.get('empname')
    passport=pass_info.get('passport')
    name=pass_info.get('name')
    nationality=pass_info.get('nationality')
    visa=pass_info.get('visa')
    # later add date and time
    passenger=DEL_pass.objects.create(empid=empid,empname=empname,pas_name=name,passport_no=make_password(passport),nationality=nationality,visa_no=make_password(visa))
    return JsonResponse({'status':'success','value':8})
