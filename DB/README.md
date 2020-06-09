# Social Distance Project DATABASE  

## Directory Content  
**DB.py:** Python module that handles DB write and query.  It assumes that a database has already been created and is available as specified by values in DBconst.py.  

**DBconst.py:** Defines all alias to be used in DB.py.  For instance: name of the database, location of the database, name of the measurements.  The proposal is that all "strings" are constant values are defined here, making it easier to change them and avoiding misconfiguration.  

**DBtest.py** Module to exemplify and test the use of DB.py.  

</br>
</br> 

## Time Series Database  

The social distance project deploys InfluxDB to store its time series.  

**DB name:** socialdistance  
**Host:** localhost  (actual host to be defined)  
**Port:** 8086  

</br>
</br> 

## Measurements  
### PeopleCount Measurement  

**Measurement** = RawPeopleCount  
| Name        | tag/field | Description                       | Type | Values              |
| ----------- |:---------:| ------------------ | ------------ | ------------ |
| location | tag | Location associated to this count | string | TBD  |
| origin | tag | Origin of the measurement | string | camera, wifi, ??? | 
| count | field | Number of peple detected at this moment at this location | integer |  |


**PLEASE DOCUMENT OTHER MEASUREMENTS AS THEY ARE CREATED**  

</br>
</br> 

## Testing Environment

While the actual Database to be used is not available, pelase install a local copy of InfluxDB to allow testing.

1. Download InfluxDB as described here: https://docs.influxdata.com/influxdb/v1.8/introduction/download/
2. Install InfluxDB as specified here: https://docs.influxdata.com/influxdb/v1.8/introduction/install/
3. Make sure that Influxd is running
4. Enter in Influx console via the following command:  *influx -precision rfc3339*
5. Create the database from the console: *> CREATE DATABASE socialdistance*

</br>
</br> 

## InfluxDB tutorial  

A brief summary of InfluxDB concepts are presented next:
- **Influx database:** Contains one or more series 
- **Series:** time ordered collection of values/timestamp pairs thats shares the same **measurement**
- **Measurement:** Acts as container for fields and their types. Loosely equivalent to the concept of a table in SQL where the primary key is always time. There are two types of fields (equivalent to *columns* in the SQL table):
  - **fields** - the measured values itself
  - **tags** - any metadada about the value (equivalent to indexed columns)
- **Point:** combination of a **timestamp** + **measurement** + **tag-set** + **field-set**
  - **tag-set:** collection of **tag-key** + **tag-value**
  - **filed-set:** collection of **field-key** + **field-value**

With InfluxDB, you can have millions of measurements, you don’t have to define schemas up-front, and null values aren’t stored.

## Basic commands

| Task                                  | Command                       |
| ------------------------------------- | ----------------------------- |
| Connecting to InfluxDB | $ influx -precision rfc3339 |
| Verifying exiting databases | > show databases |
| Specifying the database | > USE socialdistance  |
| Verifying existing measurements | > show measurements |
| Querying existing points | > SELECT * from "peoplecount" |
| | > SELECT * from "peoplecount" WHERE "origin"="camera" |
| Inserting poin in the measurement | > INSERT peoplecount,location="xxx",origin="camera",count=0 |
