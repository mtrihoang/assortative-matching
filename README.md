OSE Data Science Project | Minh Tri Hoang | Summer Semester 2021
================================================================

For my final project, I replicate results from the following paper ``Abramitzky, Ran, Adeline Delavande, and Luis Vasconcelos. 2011. "Marrying Up: The Role of Sex Ratio in Assortative Matching." American Economic Journal: Applied Economics, 3 (3): 124-57``.

## Project overview

Abramitzky et al. (2011) investigate the impact of male scarcity on marital assortative matching and marriage market outcomes. Using the difference-in-differences and IV approaches, they find that in regions with higher mortality rates, women were more likely to remain single postwar, out-of-wedlock births increased, divorce rates and the age gap decreased. 

To verify whether individuals married those within their social classes or randomly, Abramitzky et al. (2011) come up with usage of prewar data to investigate the distribution of social distance, which is defined as the class of the bride minus the class of the groom. The authors then construct the well-known null hypothesis, the random matching, which specifies that prewar couples married randomly. In the project, I created function ``bootstrap_sm`` to replicate authors' bootstrapping approach, constructing 95 percent bootstrap confidence intervals for the distribution of social difference under the null hypothesis.

Overall, the results in this notebook strongly support the empirical findings reported by Abramitzky et al. (2011). Based on the transparent research methods and Stata code, I can replicate and produce outputs similar to those in the original paper, including OLS, IV regressions, and bootstrap simulation.

## Structure of notebook

A typical project notebook has the following structure:

* Presentation of baseline article with proper citation and brief summary.
* Using causal graphs to illustrate the authors' identification strategy.
* Replication of selected key results.
* Critical assessment of quality.
* Independent contribution, e.g. additional external evidence, robustness checks, visualization.