from django.template import Template

def ampel_template():
	hauptseite_template = """
	<html>
	<head>
	<p> Ampelsteuerung </p>
	</head>

	<body>
	<p> Heute ist es {{ date }} </p>
	</body>

	</html>
	"""
	return hauptseite_template
