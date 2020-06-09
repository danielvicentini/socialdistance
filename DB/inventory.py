DeviceInventory = [
  {
   "SerialNumber": "Q2FV-GA8U-S45S",
   "Device": "Camera",
   "Nome": "MV12 Sala",
   "Location": "Sala"
   },
  {
   "SerialNumber": "Q2PD-XNUL-RYYQ",
   "Device": "WiFi",
   "Nome": "MR33 Sala",
   "Location": "Sala"
  },
  {
   "SerialNumber": "Q2FV-CWAD-KJJN",
   "Device": "Camera",
   "Nome": "MV12 Cozinha",
   "Location": "Cozinha"
  },
  {
   "SerialNumber": "Q2ED-PVBD-U859",
   "Device": "WiFi",
   "Nome": "MR24_Cozinha",
   "Location": "Cozinha"
  },
  {
   "SerialNumber": "Q2GD-R9UA-8CJK",
   "Device": "WiFi",
   "Nome": "MR18 Quartos",
   "Location": "Quartos"
  },
]

def DeviceInfo (serialnumber):
  for device in DeviceInventory:
    if device["SerialNumber"] == serialnumber:
      location = device["Location"]
      return (location, device["Device"])
  return (None,None)