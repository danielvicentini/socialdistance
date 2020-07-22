DeviceInventory = [
  {
   "SerialNumber": "XXX-YYYY-ZZZ",
   "Device": "Camera",
   "Nome": "Device Name",
   "Location": "Device Location",
   "NetworkID": "L_XXXXXXXXXXXXXXXXX"
   },
  {
   "SerialNumber": "XXX-YYYY-ZZZ",
   "Device": "Camera",
   "Nome": "Device Name",
   "Location": "Device Location",
   "NetworkID": "L_XXXXXXXXXXXXXXXXX"
   }
 ]


def getDeviceInfoName (item,Nome):
  # Devole o valor de uma chave, após encontrar o nome do device correspondente
  for device in DeviceInventory:
    if device["Nome"].lower() == Nome.lower():
      try:
        itemData = device[item]
        return itemData
      except:
        return "nodata"
  return "erro"


def getDeviceInfoSerial (item,serialnumber):
  # Devole o valor de uma chave, após encontrar o Serial correspondente
  for device in DeviceInventory:
    if device["SerialNumber"].lower() == serialnumber.lower():
      try:
        itemData = device[item]
        return itemData
      except:
        return "nodata"
  return "erro"


def DeviceInfo (serialnumber):
  for device in DeviceInventory:
    if device["SerialNumber"] == serialnumber:
      location = device["Location"]
      return (location, device["Device"])
  return (None,None)
