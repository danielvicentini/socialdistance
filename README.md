# Social Distance

This is the social distance project description


## Business/Technical Challenge
#**TODO:** 1-3 paragraphs of the business/technical Challenge
As work environment re-opens after the COVID-19 pandemic peak, a new normal will have to be defined. 
While we all hope that there will not be another pandemic in this proportion, we are all aware that it is extremely likely that similar situations will recur. 

Unfortunately, companies nowadays have no means of reinforcing preventive measures in the workplace, such as wearing facial masks or maximum number of people in a room, let alone tracking the times and locations within their sites that an employee or visitor has passed, once he/she reports being infected.  

## Proposed Solution
#**TODO:** 1-3 paragraphs of the solution in written format
In order to address this challenge, our team proposes building a platform capable of capturing and analyzing information from multiple sources, giving visibility about the issues listed above. 

Platform will be composed of multiple blocks, implementing an architecture that allow the platform to expand.
There will be three kind of modules: 
 -Monitoring modules: responsible for capturing information from multiple sources. 
 -Backend modules: responsible for storing and analyzing this information, extracting insights from it. 
 -Frontend modules: responsible for platform configuration, alerts and reports. 

Webex Teams will be leveraged as the frontend.    

Regarding monitoring modules, the following is being considered: 
 -Detection of people not using facial mask, leveraging video analytic build over Meraki cameras. 
 -Identification and counting of people in a certain site leveraging Meraki cameras native analytics, Meraki WiFi location APIs and others. 
 -Detecting the minimum distance between people in a site (stretch goal), levering video analytiac build over Meraki cameras.  

As a stretch goal, we plan to build a backend module for determining the people with whom an infected person had contact within the work environment during the period when he was supposed to have had the virus incubated.  

### Cisco Products Technologies/ Services

#**TODO:** List out major technologies included in the solution (ACI, DNAC, third party, etc) e.g

Our solution will levegerage the following Cisco technologies

#* [Application Centric Infrastructure (ACI)](http://cisco.com/go/aci)
#* [DNA Center (DNA-C)](http://cisco.com/go/dna)

* Meraki Cameras and Access-Point (http://meraki.cisco.com)
* Webex Teams (http://teams.webex.com)

## Team Members
#**TODO:** ASIC projects must consist of a minimum of 2 SE’s
#representing a minimum of 2 segments. List names here

#* team member1 <email> - Segment Name
#* team member2 <email> - Segment Name
* Marcos Alves <maralves@cisco.com> - TSS-GVE
* Daniel Vicentini <dvicenti@cisco.com> - PSE
* Andrey Cassemiro <acassemi@cisco.com> - SE
* Flavio Correa <flcorrea@cisco.com> - TSA


## Solution Components


<!-- This does not need to be completed during the initial submission phase  

Provide a brief overview of the components involved with this project. e.g Python /  -->


## Usage

<!-- This does not need to be completed during the initial submission phase  

Provide a brief overview of how to use the solution  -->



## Installation

How to install or setup the project for use.


## Documentation

Pointer to reference documentation for this project.


## License

Provided under Cisco Sample Code License, for details see [LICENSE](./LICENSE.md)

## Code of Conduct

Our code of conduct is available [here](./CODE_OF_CONDUCT.md)

## Contributing

See our contributing guidelines [here](./CONTRIBUTING.md)
