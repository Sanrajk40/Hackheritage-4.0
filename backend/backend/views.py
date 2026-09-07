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
        userid = empdata.get('userid')
        status =False
        airport_no = empdata.get('airport')
        password = empdata.get('password')
        hp= make_password(password)
        if globe_employee.objects.filter(empid= userid).exists():
            return JsonResponse({'status':'error','value':'5'})
        else:
            globe_employee.objects.create(name= username, empid= userid, airport_no=airport_no,password=hp, active_staus=status)
            return JsonResponse({'status':'success','value':'0'})
    else:
        return JsonResponse({'status':'warning','value':'3'})