''' stats tests: fairness of a coin '''
import os,sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc3 as pm
import scipy.stats as st

%matplotlib inline
%precision 4
plt.style.use('bmh')

# is coin biased?

"""model a coin toss """
# model each flip from distribution from random values
n =1000
pcoin = 0.62 # unfair coin
# predict: bernoulli(p), rvs(n)
results = st.bernoulli(pcoin).rvs(n)
print("We observed %s heads out of %s"%(h,n))

# model the expected distribution mu, sigma
n = 1000
p = 0.5
rv = st.binom(n,p)
mu = rv.mean()
sd = rv.std()
print("The expected distribution for a fair coin is mu=%s, sd=%s"%(mu,sd))

# simulate the p-value
n_samples = 10000
xs = np.random.binomial(n, p, samples)
print("Simulation p-value - %s"%(2*np.sum(xs >= h)/(xs.size + 0.0)))

## p-value by binomial test
print("Binomial test - %s"%st.binom_test(h, n, p))

## MLE
# likelihood = p(event)/p(all)
print("Maximum likelihood %s"%(np.sum(results)/float(len(results))))

## bootstrap
# make samples from 'results'
bs_samples = np.random.choice(results, (nsamples, len(results)), replace=True)
bs_ps = np.mean(bs_samples, axis=1) # posterior...mean of samples
bs_ps.sort()
print("Bootstrap CI: (%.4f, %.4f)" % (bs_ps[int(0.025*nsamples)], bs_ps[int(0.975*nsamples)]))
#vis:
plt.hist(bs_ps)
plt.show()

'''inference with pymc3'''
print("n = %s"%n)
print("h = %s"%h)
alpha = 2
beta = 2

niter = 1000
with pm.Model() as model: # context management
    # define priors
    # define for distribution (here, using Binomial(n,p))
    p = pm.Beta('p', alpha=alpha, beta=beta) # use a beta because it's wide and doesn't make many assuptions
    # n = known in this case

    # define priors as uniform
    #mu = pm.Uniform('mu', lower=0, upper=100, shape=_mu.shape)
    #sigma = pm.Uniform('sigma', lower=0, upper=10, shape=_sigma.shape)


    # define likelihood
    y = pm.Binomial('y', n=n, p=p, observed=h) # n from above cell

    # define likelihood as uniform
    #y_obs = pm.Normal('Y_obs', mu=mu, sd=sigma, observed=y)

    # inference
    start = pm.find_MAP() # Use MAP estimate (optimization) as the initial state for MCMC (e.g. starting model)
    step = pm.Metropolis() # Have a choice of samplers
    trace = pm.sample(niter, step, start, random_seed=123, progressbar=True)

# plot prior and posterior
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111)

ax.hist(trace['p'], 15, histtype='step', normed=True, label='post');
x = np.linspace(0, 1, 100)
ax.plot(x, st.beta.pdf(x, alpha, beta), label='prior');
ax.legend(loc='best');
