from framework import sustainability_framework

#Control variables
year = 2017
ISO_code = 'PT'

#Run the framework
sf = sustainability_framework.sustainability(year, ISO_code, proc_obj='cantinas escolares')
#sf = sustainability_framework.sustainability(year, ISO_code, ID=3603343)
report = sf.run()

#TODO: Testar com mais de um basegov e mais de um IOT exiobase
#TODO: mapear as atividades CPV para EXIOBASE com mais acurácia

