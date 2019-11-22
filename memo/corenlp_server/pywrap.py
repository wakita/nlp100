from corenlp_pywrap import pywrap

annotators = ["pos", "ner", "depparse"]

cn = pywrap.CoreNLP(url='http://localhost:9000', annotator_list=annotators)

# Calling basic function which would return a 'requests' object

DATA = "CoreNLP includes a simple web API server for servicing your human language understanding needs (starting with version 3.6.0). This page describes how to set it up. CoreNLP server provides both a convenient graphical way to interface with your installation of CoreNLP and an API with which to call CoreNLP using any programming language. If you're writing a new wrapper of CoreNLP for using it in another language, you're advised to do it using the CoreNLP Server."

out = cn.basic(DATA, out_format='json')
print(out.json())

out = cn.basic(DATA, out_format='text')
print(out.text)
