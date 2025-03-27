library(lme4)
library(lmerTest)
library(ggplot2)
library(dplyr)
library(ggpubr)
library(stargazer)


# Read decision data
df <- read.csv('../exp-data/player_decisions.csv')
# Format factor - network type
df$network_type <- as.factor(df$network_type)
df$network_type <- relevel(df$network_type, 'repr')
# Format factor - poor vs. rich status
df$status <- as.factor(df$status)
df$status <- relevel(df$status, 'R')

df$obsrich <- (df$network_type=='rich') | (df$status=='P' & df$network_type=='hete') | (df$status=='R' & df$network_type=='homo')
df$obspoor <- (df$network_type=='poor') | (df$status=='P' & df$network_type=='homo') | (df$status=='R' & df$network_type=='hete')
df$segr <- (df$network_type=='segr')


# Read demographic data
df2 <- read.csv('../exp-data/player_data.csv')[ ,1:14]

# Gender, reference is "Male"
df2$gender[df2$gender == ''] <- NA
df2$gender <- as.factor(df2$gender)
df2$gender <- relevel(df2$gender, 'M')
barplot(table(df2$gender), ylab = "Frequency", xlab = "Gender")

# Race, reference is most common category "White"
df2$race[df2$race == ''] <- NA
df2$race <- as.factor(df2$race)
df2$race <- relevel(df2$race, 'W')
barplot(table(df2$race), ylab = "Frequency", xlab = "Race")

# Education, reference is most common category "Bachelor's degree"
df2$education[df2$education == ''] <- NA
df2$education <- as.factor(df2$education)
df2$education <- relevel(df2$education, 'BA')
barplot(table(df2$education), ylab = "Frequency", xlab = "Education")

# Religion, reference is most common category "No religion"
df2$religion[df2$religion == ''] <- NA
df2$religion <- as.factor(df2$religion)
df2$religion <- relevel(df2$religion, 'NR')
barplot(table(df2$religion), ylab = "Frequency", xlab = "Religion")

# Merge two datasets
df <- merge(df, df2, by='sid')


### VOTE IN ROUND 1 ################################

df1 <-df[df$round == 1, ]

# The poor vote for more distribution except in segregated networks
m1 <- lm(vote ~ network_type + status 
           + network_type * status, data = df1)
print(summary(m1))

# Results are the same if we use observation samples instead of networks
m11 <- lm(vote ~ obsrich + obspoor + segr + status 
           + obsrich * status + obspoor * status + segr * status, data = df1)
print(summary(m11))

# Females and conservatives vote for lower tax
# Those who perceive themselves in a lower income percentile and
# prefer higher taxation level in the US vote for higher tax
# No effect from race, education, income, religion (except for Mormons but small N)
m2 <- lm(vote ~ network_type + status 
           + network_type * status 
           + age + gender 
           + politics + percentile + tax, data = df1)
print(summary(m2))

# All of the effect for females can be explained with women assigned poor
# in conditions where they observe at least some rich (N=1,119)
# (Women also vote for lower taxation than men when they are rich observing rich)
# This suggests that women have lower alpha (disadvantageous inequality)?
# Alternatively, women may not understand the instructions as well (some evidence for that)
m21 <- lm(vote ~ network_type + status 
           + network_type * status 
           + age + gender 
           + gender*status
           + politics + percentile + tax, data = df1)
print(summary(m21))

#stargazer(m2, m21)

# Plot Male and Female votes by treatment
ggplot(df1[(df1$status=='R') & (df1$gender=='M' | df1$gender=='F'), ], aes(x=network_type, y=vote, fill=gender)) + 
  geom_boxplot()
ggplot(df1[(df1$status=='P') & (df1$gender=='M' | df1$gender=='F'), ], aes(x=network_type, y=vote, fill=gender)) + 
  geom_boxplot()


# Results are replicated when using sex as recorded on Prolific (N=1,430)
df_prol <- read.csv('../exp-data/player_turnout.csv')
# Sex from Prolific
df_prol$p_sex <- as.factor(df_prol$p_sex)
df_prol$p_sex <- relevel(df_prol$p_sex, 'Male')
df_new <- merge(df1, df_prol[c('sid', 'p_sex')], by='sid', all=FALSE)
# There are 9 cases with expired or "prefer not to say" sex, which we will ignore
m22 <- lmer(vote ~ network_type + status 
            + network_type * status 
            + p_sex 
            + p_sex*status
            + (1|batch) + (1|group), data = df_new[(df_new$p_sex=='Male' | df_new$p_sex=='Female'), ])
print(summary(m22))
ggplot(df_new[(df_new$status=='P') & (df_new$p_sex=='Male' | df_new$p_sex=='Female'), ], 
       aes(x=network_type, y=vote, fill=p_sex)) + 
       geom_boxplot()
ggplot(df_new[(df_new$status=='R') & (df_new$p_sex=='Male' | df_new$p_sex=='Female'), ], 
       aes(x=network_type, y=vote, fill=p_sex)) + 
  geom_boxplot()

# Women also appear to have difficulty understanding the instructions
df_quiz <- read.csv('../exp-data/quiz_answers.csv')
df_quiz$p_sex <- as.factor(df_quiz$p_sex)
df_quiz$p_sex <- relevel(df_quiz$p_sex, 'Male')
df_quiz$a1_wrong <- (df_quiz$a1 != '50')
df_quiz$a2_wrong <- (df_quiz$a2 != '248')
df_quiz$a3_wrong <- (df_quiz$a3 != '3324')

# They take more attempts on average 
df_attempt <- df_quiz %>%
    group_by(participant_id) %>%
    slice(which.max(attempt))
df_attempt <- df_attempt[(df_attempt$p_sex=='Male' | df_attempt$p_sex=='Female'), ]

df_attempt %>%
  group_by(p_sex) %>%
  summarise_at(c('attempt'), mean, na.rm=TRUE)

wilcox.test(df_attempt$attempt ~ df_attempt$p_sex)
m23 = lm(attempt ~ p_sex, data = df_attempt)
summary(m23) 

# Women get two questions more often wrong than men - calculating median vote (Q1) 
# and calculating the benefit (Q2)
df_wrong <- df_quiz %>%
            group_by(participant_id) %>%
            summarise_at(c("a1_wrong", "a2_wrong", 'a3_wrong'), sum, na.rm = TRUE)
df_wrong <- merge(df_wrong, df_attempt[c('participant_id', 'p_sex')], by='participant_id')

df_wrong %>%
  group_by(p_sex) %>%
  summarise_at(c('a1_wrong', 'a2_wrong', 'a3_wrong'), 
               mean, na.rm=TRUE)
wilcox.test(df_wrong$a1_wrong ~ df_wrong$p_sex)
wilcox.test(df_wrong$a2_wrong ~ df_wrong$p_sex)
wilcox.test(df_wrong$a3_wrong ~ df_wrong$p_sex)


### REPEATED VOTES ################################

# The poor increase vote over subsequent rounds, the rich stay their course
m1dyn <- lmer(vote ~ network_type + status 
              + network_type * status + round + round * status
              + (1|batch) + (1|group) + (1|sid), data = df)
print(summary(m1dyn))

# As before, all vote for less redistribution when segregated
# The poor vote for more redistribution than the rich, 
# especially when observing more rich others
# The poor increase vote over subsequent rounds
m11dyn <- lmer(vote ~ obsrich + obspoor + segr + status 
              + obsrich * status + obspoor * status
              + round + round * status
              + (1|batch) + (1|group) + (1|sid), data = df)
print(summary(m11dyn))


### CHANGE IN VOTE ################################

dfDelta <- df[order(df$sid, df$round), ]
# New variable for change in vote from previous round
dfDelta <- dfDelta %>% 
  group_by(sid) %>% 
  mutate(vote_change = vote - lag(vote)) 
# New variable for distance of vote from median vote
dfDelta$vote_distance <- dfDelta$vote - dfDelta$median_vote
# Keep rounds 2 and 3 only
dfDelta <-dfDelta[dfDelta$round != 1, ]


# Participants double-down - if they disagree with the median vote, next 
# they vote even more extremely
# The effect is the same for the rich and poor
dfDelta$status <- relevel(dfDelta$status, 'R')
m1Delta <- lmer(vote_change ~ network_type + status + vote_distance
              + vote_distance * status
              + (1|batch) + (1|group) + (1|sid) + (1|round), data = dfDelta)
print(summary(m1Delta))

# Evidence of radicalization (upward diagonal) and rigidity (horizontal line at vote_change=0)
# Little evidence of conformity (it should show as a strong vertical line at vote_distance=0)
plot(dfDelta$vote_distance, dfDelta$vote_change)


### SATISFACTION AND FAIRNESS ################################

# Satisfaction with result
mFsat1 <- lmer(result_satisfied ~ network_type + status 
           + network_type * status 
           + (1|batch) + (1|group), data = df1)
print(summary(mFsat1))

mFsat2 <- lmer(result_satisfied ~ obsrich + obspoor + segr + status 
              + obsrich * status + obspoor * status
              + (1|batch) + (1|group), data = df1)
print(summary(mFsat2))

# Perception of fairness
mFfair1 <- lmer(result_dist_fair ~ network_type + status 
              + network_type * status
              + (1|batch) + (1|group), data = df1)
print(summary(mFfair1))

mFfair2 <- lmer(result_dist_fair ~ obsrich + obspoor + segr + status 
               + obsrich * status + obspoor * status
               + (1|batch) + (1|group), data = df1)
print(summary(mFfair2))

