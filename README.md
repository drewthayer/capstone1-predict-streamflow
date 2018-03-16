# capstone1-predict-streamflow
capstone 1: predict streamflow from SNOTEL network sensor data

#### Science Question:

Can I predict stream discharge (cubic feet per second, a.k.a. _cfs_) from snow station data?

Data availble: USGS stream gages and NRCS SNOTEL network

<img alt="alpha sensitivity test" src="/figures/co_swe_current.png" width='500'>

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

<img alt="alpha sensitivity test" src="/figures/gunnison_river_7stations_nobins.png" width='600'>

## Question: can you predict max potential Q as a function of nightly low air temp?
#### model: max Q per degree C

To get the envelope of max potential streamflow, I binned on degrees C and extract max Q for each degree

(86 bins from -04C to 18C)


for 7 stations, r2 = 0.77, not bad

<img alt="alpha sensitivity test" src="/figures/linear_binnedq/linear_binnedq_1.png" width='500'>

but the relationship is not linear...

#### next step: polyomial fit

I can fit this better with linear regression with polynomial features, using all features

Fit using sklearn PolynomialFeatures and Ridge regression, with all 6 SNOTEL features

Model fit is really good with order 2 or 3 (R2 = 0.93, 0.96), probably over-fit...

![figure](/figures/poly_models_all_snotel/gunnison_river_7stations_skpoly2.png)

## Question: predicting the maximum _potential streamflow_ is interesting, but predicting streamflow directly would be more useful
### Can I predict streamflow in the Gunnison River using all the SNOTEL stations in the Gunnison River hydrologic basin?

#### modeling approach: predict Q from SNOTEL data aggregated from all 10 stations in basin

#### train and test: train model on 1985 to 2016, test model on 2016, 2017, 2018 data

preliminary model: not capturing the high flows in late spring very well

<img alt="alpha sensitivity test" src="/figures/predict_q/gunnison_river_predict_q_alpha50.png" width='500'>

predict sum Q for all months
<img alt="alpha sensitivity test"
src="/figures/predict_q/gunnison_river_predict_sum_q_all_months.png" width='500'>

better prediction but I don't understand the complexity

### test for correct alpha:
Did a cross-validation operation for a ridge regression analagous to k-folds for timeseries: sklearn's TimeSeriesSplit
with 30 splits

Performed alpha optimization across a range of alphas: 10^-5 to 10^10
initially getting very large errors errors

<img alt="alpha sensitivity test" src="/figures/alpha_tests/alpha_test_10000_records.png" width='300'>

but after standardizing and scaling X...errors got reasonable and I can pick an alpha value for the ridge regression

<img alt="alpha sensitivity test" src="/figures/alpha_tests/alpha_test_scaled.png" width='300'>

**optimal alpha = 2848**
This model requires a high level of regularization to perform, thus it will have a hard time predicting the peak flow behavior in late spring.

### run ridge regression with scaled X and optimal alpha

this model does not do a good job of predicting lower, less variable flows in winter,

but it's not good at predicting the high flows in may and june when runoff is pumping.

<img alt="ridge with scaled X" src="/figures/predict_q/gunnison_river_predict_q_alpha2848.png" width='500'>

sure enough, it's unable to characterize those late spring peak flows

### assess coefficients
pipeline: standardize using StandardScalar() and Ridge regression

turns out 'cfs' feature has a very high coeffiecient (duh)

removed 'cfs', 'year', and 'month'...'cfs' is not from the SNOTEL sensors, and 'year' and 'month' will correlate but not have predictive value since I want to be able to predict just from meteorological data.

features with highest influece are both aggregate quantities. The behavior of the coefficients demonstrates some of my time-domain problems

_(I really  need to be predicting **summer** flow from winter snow data)_
1.  total accumulated precip by the given day
  * very high correlation...because it rains a lot in the spring

2.  SWE on the given day
 * inverse relationship... because during the 'melt season', which generates most of the streamflow, SWE is getting lower by the day


3.  3rd most influential feature is nightly low air temp, which make sense cause cold nights produce less runoff

4.   stations, with no particular pattern
  * I searched for patterns in both elevation and distance from the gage

![figure](/figures/coefs/coeffs_q_alpha2848.png)

### still some outliers affecting the model
I noticed that the model predicts variable values in September when the actual flows are quite low.

Reason: September snow is rare, but it happens. It is highly variable and uncharacteristic of September weather, so I removed records from September.

This improved the error a lot, down to an rmse error of 1325 cfs at an alpha of 559. This is a **much less regularized model**, which gives me more confidence that it can capture those spring melt magnitudes.

<img alt="alpha sensitivity test" src="/final_noseptember/alpha_test_no_september.png" width='300'>

### linear model

Linear model to predict streamflow at the Delta gage in the Gunnison River for last 3 years:
![final model](/final_noseptember/gunnison_river_predict_streamflow_rmse.png)

total RMSE = 1083 cfs

The model performs well at low flows during winter and not very well during spring melt and runoff.

### linear model with polynomial features
### increase complexity, try to capture the spring peaks

2nd order polynomial features:

<img alt="poly model" src="/polynomial/gunnison_river_predict_streamflow_poly_2.png" width='600'>

3rd order polynomial features:

<img alt="poly model" src="/polynomial/gunnison river predict streamflow poly 3.png" width='600'>

These models both do better at capturing the spring peaks. 3rd order does not do much better than 2nd order, so I'll apply Occam's razor and choose the 2nd order polynomial model.

alpha optimization for poly 2:

<img alt="alpha optimization" src="/polynomial/alpha_test_poly2_5folds.png" width='400'>

Not surprisingly, this requires much more regularization (linear alpha = 330, poly2 alpha > 10^5)

The model performs well at low flows during winter and not very well during spring melt and runoff.

## moving forward
* use an appropriate technique for time-lagged processes
  * what we _really_ want to predict is cumulative volumes of streamflow in the summer
* regression that takes lag-time into account
* characterize errors: assess error as a function of flow magnitude
