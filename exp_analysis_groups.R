library(lme4)
library(lmerTest)
library(ggplot2)
library(dplyr)

# Parametric tests for differences between treatments
# Findings from non-parametric Mann Whitney U tests are largely confirmed 

# Read group data
df <- read.csv('../exp-data/group_outcomes.csv')
# Format factor - network type
df$network_type <- as.factor(df$network_type)
df$network_type <- relevel(df$network_type, 'repr')


### ALL ROUNDS ###

# Only segr has significantly lower median vote than the rest
m1 <- lmer(median_vote ~ network_type + round 
           + (1|batch) + (1|group), data = df)
print(summary(m1))

# Polarization increases over time for hete but not for poor and homo
df$network_type <- relevel(df$network_type, 'hete')
m2 <- lmer(vote_mad ~ network_type + round 
           + network_type * round
           + (1|batch) + (1|group), data = df)
print(summary(m2))

# Restore reference category
df$network_type <- relevel(df$network_type, 'repr')


### FIRST ROUND ###
dff <- df[df$round == 1, ]

# segr is significantly lower than the rest
m3 <- lmer(median_vote ~ network_type + (1|batch), data = dff)
print(summary(m3))

# Change reference category to rich or poor 
# rich is significantly higher than poor
dff$network_type <- relevel(dff$network_type, 'poor')
m3 <- lmer(median_vote ~ network_type + (1|batch), data = dff)
print(summary(m3))

dff$network_type <- relevel(dff$network_type, 'repr')
# Only segr is significantly lower than the rest
m4 <- lmer(vote_mad ~ network_type + (1|batch), data = dff)
print(summary(m4))


### LAST ROUND ###
dfl <- df[df$round == 3, ]

# Only segr is significantly lower than the rest
m5 <- lmer(median_vote ~ network_type + (1|batch), data = dfl)
print(summary(m5))

# Change reference category to see significant differences
# rich and hete are significantly higher than homo, poor, and segr 
dfl$network_type <- relevel(dfl$network_type, 'hete')
m6 <- lmer(vote_mad ~ network_type + (1|batch), data = dfl)
print(summary(m6))

dfl$network_type <- relevel(dfl$network_type, 'rich')
m6 <- lmer(vote_mad ~ network_type + (1|batch), data = dfl)
print(summary(m6))


