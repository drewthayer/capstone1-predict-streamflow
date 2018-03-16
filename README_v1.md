# capstone1-predict-streamflow
capstone 1: predict streamflow from SNOTEL network sensor data

#### Science Question:

Can I predict stream discharge (cubic feet per second, a.k.a. _cfs_) from snow station data?

Data availble: USGS stream gages and NRCS SNOTEL network

![figure](/figures/co_swe_current.pdf)

Preliminary look: hard to predict because discharge is variable, BUT there is a clear relationship between nightly low air temperature (at the snow stations) and max possible discharge for that day.

So, can I predict daily max potential discharge in the river from nightly low air temp at the stations in the hydrologic basin that feed the river?

### 1. acquire data:
colorado stream gages: https://waterdata.usgs.gov/co/nwis/current/?type=flow

historic colorado snotel data: https://wcc.sc.egov.usda.gov/nwcc/tabget?state=CO

all snotel products: https://www.nrcs.usda.gov/wps/portal/nrcs/detail/co/snow/products/data/?cid=NRCSEPRD1307872

interactive map to find station names:
https://www.wcc.nrcs.usda.gov/webmap/#version=80.1&elements=&networks=!&states=!&counties=!&hucs=&minElevation=&maxElevation=&elementSelectType=all&activeOnly=true&activeForecastPointsOnly=true&hucLabels=false&hucParameterLabels=false&stationLabels=&overlays=&hucOverlays=&mode=data&openSections=dataElement,parameter,date,basin,elements&controlsOpen=true&popup=&popupMulti=&base=esriNgwm&displayType=station&basinType=6&dataElement=WTEQ&parameter=PCTMED&frequency=DAILY&duration=I&customDuration=&dayPart=E&year=2018&month=3&day=12&monthPart=E&forecastPubMonth=3&forecastPubDay=1&forecastExceedance=50&seqColor=1&divColor=3&scaleType=D&scaleMin=&scaleMax=&referencePeriodType=POR&referenceBegin=1991&referenceEnd=2016&minimumYears=20&hucAssociations=true&lat=38.802&lon=-106.926&zoom=8.0

#### gunnison river drainage SNOTEL stations:
SNOTEL 680: Park Cone, CO
SNOTEL 701: Porphyry Creek, CO
SNOTEL 762: Slumgullion, CO
SNOTEL 737: Schofield Pass, CO
SNOTEL 682: Park Reservoir, CO
SNOTEL 1059: Cochetopa Pass, CO
SNOTEL 669: North Lost Trail, CO

data record: 1985 - present (38 years)

SNOTEL data include:
1.  SWE
2.  accumulated precip up to that day (in water year, starts in october)
3.  air temp : daily high
4.  air temp: nightly low
5.  air temp: mean
6.  precip that day  


### 2. clean the data
operations:

1.  make records comparable:
  * 1a convert 15-min timeseries to daily average flow to match SNOTEL daily data

2.  remove records with swe=0 (no snow)

3.  concatenate snotel data for whole basin and merge with stream flow data by date

4.  remove records with nan values for regression

### 3. exploratory model
#### regression 1: all data, not a very good fit (R2 = 0.2)
Can't predict Q from swe or air temp very well, Q is too variable.

However, it looks like the **upper envelope of Q for each air temp is a well-constrained relationship...**

![figure](/figures/gunnison_river_7stations_nobins.png)

## Question: can you predict max potential Q as a function of nightly low air temp?
#### model: max Q per degree C

To get the envelope of max potential streamflow, I binned on degrees C and extract max Q for each degree

(86 bins from -36F to 50F) UPDATE

X: swe at start of day, min airtemp, precip at start of day

y: Q

for 7 stations, r2 = 0.77, not bad

![figure](/figures/gunnison_river_7stations_precip.png)

but the relationship is not linear...

#### next step: linear regression with polynomial features

I can fit this better with linear regression with polynomial features, using all features

Fit using sklearn PolynomialFeatures and Ridge regression, with all 6 SNOTEL features

Model fit is really good with order 2 or 3 (R2 = 0.93, 0.96), probably over-fit...

![figure](/figures/poly_models_all_snotel/gunnison_river_7stations_skpoly2.png)

## Question: predicting the maximum _potential streamflow_ is interesting, but predicting streamflow directly would be more useful
### Can I predict streamflow in the Gunnison River using all the SNOTEL stations in the Gunnison River hydrologic basin?

#### modeling approach: predict Q from SNOTEL data aggregated from all 10 stations in basin

#### train model on 1985 to 2016, test model on 2016, 2017, 2018 data

Good fit on training data ... too good

![figure](/figures/predict_sumq/gunnison_river_predict_peak_q_impute0.png)

![figure](/figures/predict_sumq/gunnison_river_predict_sum_q_impute0.png)

#### split data on time range to train/test
split on 2009

![figure](/figures/predict_q_traintest/gunnison_river_predict_peak_q_train+test_10st_alpha5000.png)

![figure](/figures/predict_q_traintest/gunnison_river_predict_sum_q_train+test_10st_alpha5000.png)

### after re-posing question:
just predict cfs

![figure](/figures/predict_q/gunnison_river_predict_q_alpha50.png)

baaa!!!! not the point to predict cfs for each day during the winter!!!

predict sum Q for all months
![figure](/figures/predict_q/gunnison_river_predict_sum_q_all_months.png)

### test for correct alpha:
did a k-folds-like crossval operation for timeseries: sklearn's TimeSeriesSplit
with 30 splits

tested across a range of alphas: 10**-2 to 10**8
getting horrible errors
![figure](/figures/alpha_tests/alpha_test_10000_records.png)

but after scaling X...
![figure](/figures/alpha_tests/alpha_test_scaled.png)

optimal alpha = 2848

### run ridge model with scaled X and optimal alpha

model does not do a good job of predicting lower, less variable flows in winter,

but it's not good at predicting the high flows in may and june when runoff is pumping.

![figure](/figures/predict_q/gunnison_river_predict_q_alpha2848.png)

### assess coefficients
pipeline: standardize and ridge regression

turns out 'cfs' feature has a very high coeffiecient (duh)

removed 'cfs', 'year', and 'month'

features with highest influece are both aggregate quantities:
1.total accumulated precip by a given day
2.SWE on that given day

3rd most influential feature is nightly low airtemp, which make sense cause cold nights produce less runoff

![figure](/figures/coefs/coeffs_q_alpha2848.png)

### still some outliers

noticed variable values in september

september snow is highly variable and uncharacteristic so I removed records from september

this improved the error a lot, down to an rmse error of 1325 cfs at an alpha of 559, much less regularized, which gives me more condidence in the model

![figure](/final_noseptember/alpha_test_no_september.png)


### final model

final model to predict streamflow at delta gage for last 3 years:
![final model](/final_noseptember/gunnison_river_predict_streamflow_rmse.png)
