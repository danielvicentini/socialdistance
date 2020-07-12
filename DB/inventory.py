DeviceInventory = [
  {
   "SerialNumber": "Q2HV-9RTC-ZWMN",
   "Device": "Camera",
   "Nome": "Camera do Andrey",
   "Location": "Sala",
   "NetworkID": "L_711568741124547888"
   },
  {
   "SerialNumber": "Q2FV-GA8U-S45S",
   "Device": "Camera",
   "Nome": "MV12 Sala",
   "Location": "Sala",
   "NetworkID": "L_711568741124547888"
   },
  {
   "SerialNumber": "MR33_Sala",
   "Device": "WiFi",
   "Nome": "MR33_Sala",
   "Location": "Sala",
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
   "NetowrkID": "L_711568741124547888"
  },
  {
  "SerialNumber": "Q2GV-7HEL-HC6C",
  "Device": "Camera",
  "Nome": "MV_Sandbox",
  "Location": "Sandbox",
  "NetowrkID": "L_711568741124547888"
  },
]

def DeviceInfo (serialnumber):
  for device in DeviceInventory:
    if device["SerialNumber"] == serialnumber:
      location = device["Location"]
      return (location, device["Device"])
  return (None,None)
