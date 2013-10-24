from django.http import Http404, HttpResponse
from django.template import Template,RequestContext, Context
from django.template.loader import get_template
import datetime
import ampelControl

def current_date(request,hours):
	try: 
		hours = int(hours)
	except ValueError:
		raise Http404()	
	now = datetime.datetime.now() + datetime.timedelta(hours=hours)
	html = "<html> <body> time %s </body> </html>" % now
	return HttpResponse(html)


def hello(request):
	return HttpResponse("deine mudda tanzt quadrat")


def ampel(request):
	checkStatusRed = _getCheckedStatus( ampelControl.status("red") )
	checkStatusGreen = _getCheckedStatus( ampelControl.status("green") )
	
	c = Context({'date': datetime.datetime.now(),
		'checkStatusRed': checkStatusRed,
		'checkStatusGreen': checkStatusGreen, })
	t = get_template('raw_template.html')
	html = t.render(c)
	return HttpResponse(html)


def switch(request):
	print request.POST
	print "ok"
	switchColor = request.POST['color']
	if switchColor == 'green':
		switchColor = 2
	else:
		switchColor = 1
	if request.POST['switchStatus'] == 'on':
		ampelControl.switchOn(switchColor)
	else:
		ampelControl.switchOff(switchColor)
	return HttpResponse("ok")


def _getCheckedStatus(status):
		if int(status) == 0: 
			return "unchecked"
		else:
			return "checked"
