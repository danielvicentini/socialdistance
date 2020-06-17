DeviceInventory = [
  {
   "SerialNumber": "Q2FV-GA8U-S45S",
   "Device": "Camera",
   "Nome": "MV12 Sala",
   "Location": "Sala"
   },
  {
   "SerialNumber": "MR33_Sala",
   "Device": "WiFi",
   "Nome": "MR33_Sala",
   "Location": "Sala"
  },
  {
   "SerialNumber": "Q2FV-CWAD-KJJN",
   "Device": "Camera",
   "Nome": "MV12 Cozinha",
   "Location": "Cozinha"
  },
  {
   "SerialNumber": "MR24_Cozinha",
   "Device": "WiFi",
   "Nome": "MR24_Cozinha",
   "Location": "Cozinha"
  },
  {
   "SerialNumber": "MR18_Quartos",
   "Device": "WiFi",
   "Nome": "MR18_Quartos",
   "Location": "Quartos"
  },
  {
  "SerialNumber": "Q2GV-7HEL-HC6C",
  "Device": "Camera",
  "Nome": "MV_Sandbox",
  "Location": "Sandbox"
  },
]

def DeviceInfo (serialnumber):
  for device in DeviceInventory:
    if device["SerialNumber"] == serialnumber:
      location = device["Location"]
      return (location, device["Device"])
  return (None,None)