# capstone1-predict-streamflow
capstone 1: predict streamflow from SNOTEL network sensor data

## project workflow

### Science Question:

Can I predict stream discharge (cfs) from snow station data?

Preliminary look: hard to predict because discharge is variable, BUT there is a clear relationship between nightly low air temperature (at the snow stations) and max possible discharge for that day.

So, can I predict daily max potential discharge in the river from nightly low air temp at the stations in the hydrologic basin that feed the river?

### 1. download data:
colorado stream gages: https://waterdata.usgs.gov/co/nwis/current/?type=flow

historic colorado snotel data: https://wcc.sc.egov.usda.gov/nwcc/tabget?state=CO

all snotel products: https://www.nrcs.usda.gov/wps/portal/nrcs/detail/co/snow/products/data/?cid=NRCSEPRD1307872

interactive map to find station names:
https://www.wcc.nrcs.usda.gov/webmap/#version=80.1&elements=&networks=!&states=!&counties=!&hucs=&minElevation=&maxElevation=&elementSelectType=all&activeOnly=true&activeForecastPointsOnly=true&hucLabels=false&hucParameterLabels=false&stationLabels=&overlays=&hucOverlays=&mode=data&openSections=dataElement,parameter,date,basin,elements&controlsOpen=true&popup=&popupMulti=&base=esriNgwm&displayType=station&basinType=6&dataElement=WTEQ&parameter=PCTMED&frequency=DAILY&duration=I&customDuration=&dayPart=E&year=2018&month=3&day=12&monthPart=E&forecastPubMonth=3&forecastPubDay=1&forecastExceedance=50&seqColor=1&divColor=3&scaleType=D&scaleMin=&scaleMax=&referencePeriodType=POR&referenceBegin=1991&referenceEnd=2016&minimumYears=20&hucAssociations=true&lat=38.802&lon=-106.926&zoom=8.0


#### gunnison river stream gage in Delta, CO
#### gunnison river drainage SNOTEL stations:
SNOTEL 680: Park Cone, CO
SNOTEL 701: Porphyry Creek, CO
SNOTEL 762: Slumgullion, CO
SNOTEL 737: Schofield Pass, CO
SNOTEL 682: Park Reservoir, CO
SNOTEL 1059: Cochetopa Pass, CO
SNOTEL 669: North Lost Trail, CO

data record: 1985 - present (38 years)

### 2. clean data
operations:

convert 15-min timeseries to daily average flow

convert units to SI

remove records with swe=0 (no snow)

match timestamps so data record is by day

concatenate snotel data for whole basin, merge with flow data

remove records with nan values

### 3. model
#### regression 1: all data, not very good (R2 = 0.2)

#### binned regression:

need the envelope of max potential streamflow, so bin on degrees F and extract max Q for each degree

(86 bins from -36F to 50F)

X: swe at start of day, min airtemp, precip at start of day

y: Q

for 7 stations, r2 = 0.77, not bad

### next step: polyomial fit

relationship is not linear...

I can fit this better with a polynomial, using all features

Fit using sklearn PolynomialFeatures and Ridge, with 6 features

Model fit is really good with order 2 or 3 (R2 = 0.93, 0.96), probably over-fit...

### predict q (peak, sum) from swe (peak, sum) at all stations in basin

Good fit on training data ... too good

need to impute some values
