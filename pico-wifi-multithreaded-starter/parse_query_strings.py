def qs_parse(qs):
 
  parameters = {}

  removeQuestionMark = qs.replace('/?', '')
  ampersandSplit = removeQuestionMark.split("&")
 
  for element in ampersandSplit:
 
    equalSplit = element.split("=")
 
    parameters[equalSplit[0]] = equalSplit[1]
 
  return parameters