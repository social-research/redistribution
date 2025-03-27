library(lme4)
library(lmerTest)
library(plyr)

### GET DATA ############################################################

# Read data and format factor variables
df <- read.csv('../exp-data/player_turnout.csv')
# Network type
df$network_type <- as.factor(df$network_type)
df$network_type <- relevel(df$network_type, 'repr')
# Poor vs. rich status
df$status <- as.factor(df$status)
df$status <- relevel(df$status, 'P')
# Sex from Prolific
df$p_sex <- as.factor(df$p_sex)
df$p_sex <- relevel(df$p_sex, 'Male')
# Ethnicity from Prolific
df$p_ethnicity <- as.factor(df$p_ethnicity)
df$p_ethnicity <- relevel(df$p_ethnicity, 'White')

# New treatment variables based on perception
df$obsrich <- (df$network_type=='rich') | (df$status=='P' & df$network_type=='hete') | (df$status=='R' & df$network_type=='homo')
df$obspoor <- (df$network_type=='poor') | (df$status=='P' & df$network_type=='homo') | (df$status=='R' & df$network_type=='hete')
df$segr <- (df$network_type=='segr')

# Distribution of participation round count
hist(df$turnout2)
hist(df$turnout3)
prop.table(table(df$turnout2))
hist(df$turnout3)
prop.table(table(df$turnout3))

# Read demographic data
df2 <- read.csv('../exp-data/player_data.csv')[ ,1:14]
# Gender, reference is "Male"
df2$gender[df2$gender == ''] <- NA
df2$gender <- as.factor(df2$gender)
df2$gender <- relevel(df2$gender, 'M')
# Race, reference is most common category "White"
df2$race[df2$race == ''] <- NA
df2$race <- as.factor(df2$race)
df2$race <- relevel(df2$race, 'W')
# Education, reference is most common category "Bachelor's degree"
df2$education[df2$education == ''] <- NA
df2$education <- as.factor(df2$education)
df2$education <- relevel(df2$education, 'BA')
# Religion, reference is most common category "No religion"
df2$religion[df2$religion == ''] <- NA
df2$religion <- as.factor(df2$religion)
df2$religion <- relevel(df2$religion, 'NR')

# Merge two datasets
df <- merge(df, df2, by='sid')


### PREDICT DROPOUT (DEFINED AS MISSING AT LEAST ONE ROUND) ###############
# No significant effects from treatment nor status.

# Logistic regression to predict if participant does not show at least once
df$dropped2 <- df$turnout2 < 2
df$dropped3 <- df$turnout3 < 3

# For voting rounds 2 and 3
m21 <- glmer(dropped2 ~ network_type + status 
             + (1|batch) + (1|group), 
             data = df, 
             family = binomial)
print(summary(m21))

m22 <- glmer(dropped2 ~ network_type + status 
             + network_type * status 
             + (1|batch) + (1|group), 
             data = df, 
             family = binomial)
print(summary(m22))

# For rounds 2, 3, and 4
m31 <- glmer(dropped3 ~ network_type + status 
             + (1|batch) + (1|group), 
             data = df, 
             family = binomial)
print(summary(m31))

m32 <- glmer(dropped3 ~ network_type + status + network_type * status 
             + (1|batch) + (1|group), 
             data = df, 
             family = binomial)
print(summary(m32))


### PREDICT DROPOUT WITH DEMOGRAPGICS ########################################

# The demographic variables come from Prolific. The model shows that 
# more experienced Prolific participants are less likely to drop out 
# and so are Asians. (Results are similar for dropped2 and dropped3.)
m3d1 <- glmer(dropped3 ~ network_type + status 
              + network_type * status 
              + p_time_taken + p_total_approvals
              + p_age + p_sex + p_ethnicity
              + (1|batch) + (1|group), 
              data = df, 
              family = binomial)
print(summary(m3d1))

# Those who missed the final round (including all rounds) did not fill out the 
# exit survey and hence, these data cannot be used reliably to test dropout.
# Nevertheless, among those who completed the exit survey, conservatives are 
# more likely to miss a voting round. (Note that results are the same for
# dropped2 and dropped3 since by definition, all included have completed round 4.)
# **Given that conservatives vote for lower taxation, the lower turnout by
# conservatives means that the group votes are somewhat lower than they could be.**
m3d2 <- glmer(dropped3 ~ network_type + status 
              + network_type * status 
              + age + gender + race 
              + education + income + politics
              + (1|batch) + (1|group), 
              data = df, 
              family = binomial)
print(summary(m3d2))

# Assuming those who do not show up after the first round at all are somehow different
# (e.g. do not read Prolific messages), predict dropout for the rest
# Perhaps the rich are more likely to skip a round (given that they will show
# up at least once) but the effect is not stable.
df_no0 <- df[df$turnout3 != 0, ]
m3no01 <- glmer(dropped3 ~ network_type + status 
                + (1|batch) + (1|group), 
                data = df_no0, 
                family = binomial)
print(summary(m3no01))

m3no02 <- glmer(dropped3 ~ network_type + status 
                + network_type * status 
                + (1|batch) + (1|group), 
                data = df_no0, 
                family = binomial)
print(summary(m3no02))

# The slower are more likely to drop out, the more experienced - less.
m3no03 <- glmer(dropped3 ~ network_type + status 
                + network_type * status 
                + p_time_taken + p_total_approvals
                + p_age + p_sex + p_ethnicity
                + (1|batch) + (1|group), 
                data = df_no0, 
                family = binomial)
print(summary(m3no03))

### PREDICT COUNT OF ABSENCES ########################################
# No significant effects from treatment nor status.

# Poisson regression to predict if participant does not show at least once
df$absent2 <- 2 - df$turnout2
df$absent3 <- 3 - df$turnout3

# For voting rounds 2 and 3
m21 <- glmer(absent2 ~ network_type + status 
            + (1|group) + (1|batch), 
             data = df, 
             family = poisson)
print(summary(m21))

m22 <- glmer(absent2 ~ network_type + status 
             + network_type * status 
              + (1|group) + (1|batch), 
             data = df, 
             family = poisson)
print(summary(m22))

# For rounds 2, 3, and 4
m31 <- glmer(absent3 ~ network_type + status 
             + (1|group) + (1|batch) , 
             data = df, 
             family = poisson)
print(summary(m31))

m32 <- glmer(absent3 ~ network_type + status + network_type * status 
             + (1|group) + (1|batch) , 
             data = df, 
             family = poisson)
print(summary(m32))

### PREDICT COUNT OF ABSENCES FOR ALTERNATIVE OPERATIONALIZATION OF TREATMENTS ###
# No significant effects from treatment nor status.

# For voting rounds 2 and 3
m21 <- glmer(absent2 ~ obsrich + obspoor + segr + status 
             + (1|group) + (1|batch), 
             data = df, 
             family = poisson)
print(summary(m21))

m22 <- glmer(absent2 ~ obsrich + obspoor + segr + status 
             + obsrich * status + obspoor * status + segr * status 
             + (1|group) + (1|batch), 
             data = df, 
             family = poisson)
print(summary(m22))

# For rounds 2, 3, and 4
m31 <- glmer(absent3 ~ obsrich + obspoor + segr + status 
             + (1|group) + (1|batch), 
             data = df, 
             family = poisson)
print(summary(m31))

m32 <- glmer(absent3 ~ obsrich + obspoor + segr + status 
             + obsrich * status + obspoor * status + segr * status 
             + (1|batch) + (1|group), 
             data = df, 
             family = poisson)
print(summary(m32))