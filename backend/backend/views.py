from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.hashers import make_password,check_password
from globalapp.models import globe_employee

@csrf_exempt
def addGlobalemp (request):
    if request.method == 'POST':
        empdata = json.loads(request.body)
        username =empdata.get('username')
        userid = empdata.get('user_id')
        status =False
        airport_no = empdata.get('airport_id')
        password = empdata.get('password')
        mail= empdata.get('email')
        
        if globe_employee.objects.filter(empid= userid).exists():
            e=globe_employee.objects.get(empid= userid)
            if e.active_status== True:
                return JsonResponse({'status':'error','value':'5'})
            elif e.password!=password:
                return JsonResponse({'status':'error','value':'4'})
            elif e.airport_no != airport_no:
                return JsonResponse({'status':'error','value':'2'})
            else:
                tus=True
                globe_employee.objects.update(active_status=tus)
                return JsonResponse({'status':'success','value':'1'})

            
        else:
            
            return JsonResponse({'status':'warning','value':'0'})
    else:
        return JsonResponse({'status':'warning','value':'3'})
@csrf_exempt
def logout_global(request):
    m=json.loads(request.body)
    empid=m.get('userid')
    e=globe_employee.objects.get(empid=empid)
    tus= False
    globe_employee.objects.update(active_status=tus)
    return JsonResponse({'status':'success'})