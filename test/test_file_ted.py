from framework import file_ted

code = 'PT'
language = "por"

TED = file_ted.TEDfiles()
query = TED.read(code, language)
filt_GPP = TED.gpp_oriented_filt()
TED.GTR()
