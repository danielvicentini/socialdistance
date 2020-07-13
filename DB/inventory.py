DeviceInventory = [
  {
   "SerialNumber": "Q2HV-9RTC-ZWMN",
   "Device": "Camera",
   "Nome": "Camera do Andrey",
   "Location": "Sala de Entrada",
   "NetworkID": "L_711568741124547888"
   },
  {
   "SerialNumber": "Q2FV-GA8U-S45S",
   "Device": "Camera",
   "Nome": "MV12 Sala",
   "Location": "Sala 1",
   "NetworkID": "L_711568741124547888"
   },
  {
   "SerialNumber": "MR33_Sala",
   "Device": "WiFi",
   "Nome": "MR33_Sala",
   "Location": "Sala 1",
   "NetworkID": "L_711568741124547888"
  },
  {
   "SerialNumber": "Q2FV-CWAD-KJJN",
   "Device": "Camera",
   "Nome": "MV12 Cozinha",
   "Location": "Cozinha",
   "NetworkID": "L_711568741124547888"
  },
  {
   "SerialNumber": "MR24_Cozinha",
   "Device": "WiFi",
   "Nome": "MR24_Cozinha",
   "Location": "Cozinha",
   "NetworkID": "L_711568741124547888"
  },
  {
   "SerialNumber": "MR18_Quartos",
   "Device": "WiFi",
   "Nome": "MR18_Quartos",
   "Location": "Quartos",
   "NetworkID": "L_711568741124547888"
  },
  {
  "SerialNumber": "Q2GV-7HEL-HC6C",
  "Device": "Camera",
  "Nome": "MV_Sandbox",
  "Location": "Sandbox",
  "NetworkID": "L_711568741124547888"
  },
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