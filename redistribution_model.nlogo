extensions [ rnd ]

globals [
  hardness             ;; strength of weights in softmax choice (equivalent to beta in https://bookdown.org/amesoudi/ABMtutorial_bookdown/model17.html)
  wealths              ;; list of wealths for sorted turtles
  utilities            ;; list of current utilities for sorted turtles
  votes                ;; list of votes of sorted turtles
  num-observers        ;; list of number of others who observe sorted turtles
  observed-mean-wealth ;; list of neighbors' wealths observed by sorted turtles
  observed-gini        ;; list of observed gini by sorted turtles
  observed-subj-ineq   ;; inequality as experienced differences; list of values by sorted turtles
  median-vote          ;; the median voter determines the enacted redistribution rule for the next period
  gini-index-reserve   ;; helps estimate Gini coefficient
  gini                 ;; Gini coefficient, adjusted for population size as per https://doi.org/10.1016/j.econlet.2019.108789
  behavior-error       ;; small probability that turtle does not vote for best taxrate but picks one at random; only used for deterministic decisions
  max-wealth           ;; used for normalization
  min-wealth           ;; used for normalization
  max-delta-wealth     ;; used for normalization
]

turtles-own [
  alpha                ;; aversion to disadvantageous inequality
  beta                 ;; aversion to advantageous inequality, will assume it's independent from alpha
  income               ;; used if differentiating between income and wealth (sum of taxed incomes) and taxting income vs. wealth
  wealth               ;; the amount of wealth this turtle has
  utility              ;; turtle's current utility
  best-utility         ;; best possible utility under a redistribution rule
  vote-decision        ;; final decision what tax rate to support
  vote-history         ;; list of vote decisions in all periods until now
  utility-history      ;; list of actual utility in all periods until now
  best-utility-history ;; list of best-utility in all periods until now
]


;;;;;;;;;;;;;;;;;;;;;;
;; Setup Procedures ;;
;;;;;;;;;;;;;;;;;;;;;;

to setup
  clear-all
  create-turtles population-size [turtle-setup]
  ;; Estimate normalizing constants before creating observation network
  set max-wealth (max [wealth] of turtles)
  set min-wealth (min [wealth] of turtles)
  set max-delta-wealth (max-wealth - min-wealth)
  network-setup

  set hardness 0.1
  set behavior-error 0.01    ;; only needed if decisions are determininistic

  ;; Estimate these before voting
  set num-observers (map [?t -> [count my-in-links] of ?t] sort turtles)
  set wealths (map [?t -> [wealth] of ?t] sort turtles)  ;; ([wealth] of turtles) gets them in random order, so need to sort
  set observed-mean-wealth (map [?t -> [mean [wealth] of out-link-neighbors] of ?t] sort turtles)
  set observed-gini (map [?t -> [local-gini [wealth] of out-link-neighbors] of ?t] sort turtles)
  set observed-subj-ineq (map [?t -> [subj-ineq wealth ([wealth] of out-link-neighbors)] of ?t] sort turtles)
  update-gini
  ;; Estimate initial utility of each turtle and record in their utility-history
  ask turtles [
    set utility calculate-utility wealth ([wealth] of out-link-neighbors) 0
    set utility-history lput utility utility-history
  ]
  set utilities (map [?t -> [utility] of ?t] sort turtles)

  layout
  if resize-nodes?
    [resize-nodes]
  reset-ticks
end


to turtle-setup
  set color white
  set shape "circle"

  ;; Use estimates from Fehr and Schmidt (1999) to randomly assign alpha and beta values
  ;; alpha: 30% - 0, 30% - 0.5, 30% - 1, 10% - 4
  ;; beta: 30% - 0, 30% - 0.25, 40% - 0.6
  set alpha one-of [ 0 0 0 0.5 0.5 0.5 1 1 1 4 ]
  set beta one-of [ 0 0 0 0.25 0.25 0.25 0.6 0.6 0.6 0.6]

  ;; Wealth is drawn from a beta distribution with certain initial Gini
  ;; See Pham-Gia and Rurkkan, 1992, Derermination of the beta distribution from its Lorenz curve
  ;; This is quite complex, so easiest is to vary alpha and beta to get different Ginis
  ;; b > a for right-skewed distribution, b > 5 for exponential tails
  ;; mean is a / (a + b) so use multiplier to adjust mean wealth = 100
  set income ( 100 * ( random-beta a b ) / (a / (a + b)) )
  ;; will not differentiate between income and wealth in this model but this allows for extensions
  set wealth income

  ;; Initialize list variables
  set vote-history []
  set utility-history []
  set best-utility-history []

  ;; For visual reasons, we don't put any nodes *too* close to the edges
  setxy (random-xcor * 0.95) (random-ycor * 0.95)
end


to network-setup

  clear-links
  ask turtles [

    ifelse (random-float 1) < (abs wealth-visibility)
    [  ifelse (random-float 1) < (abs wealth-assortativity)
         [connect-salient-similar] ;; VISBILITY AND ASSORTATIVITY
         [connect-salient] ;; ONLY VISIBILITY
    ]

    [  ifelse (random-float 1) < (abs wealth-assortativity)
         [connect-similar] ;; ONLY ASSORTATIVITY
         [connect-random] ;; RANDOM
    ]
  ]
end


to connect-random
  create-links-to (n-of num-observed other turtles)
end


to connect-salient
  ;; Normalize sampling weights for wealth so that they start from 0 and increase to max-delta-wealth
  ifelse wealth-visibility > 0
  [ ;; The wealthy are more visible, so higher sampling weight for higher wealth
    create-links-to (rnd:weighted-n-of num-observed other turtles [wealth - min-wealth])
  ]
  [ ;; The poor are more visible, so higher sampling weight for lower wealth
    create-links-to (rnd:weighted-n-of num-observed other turtles [max-wealth - wealth])
  ]
end


to connect-similar

  let my-wealth wealth

  ifelse wealth-assortativity > 0
  [ ;; Homophily - prefer those similar in wealth
    ;; Sampling weight is max-delta-wealth for those with identical wealth and 0 for those with wealth difference of max-delta-wealth
    create-links-to (rnd:weighted-n-of num-observed other turtles [max-delta-wealth - abs (wealth - my-wealth)])
  ]
  [ ;; Heterophily - prefer those with more different wealth
    ;; Sampling weight is max-delta-wealth between the poorest and the wealthiest agents and 0 for those with identical wealth
    create-links-to (rnd:weighted-n-of num-observed other turtles [abs (wealth - my-wealth)])
  ]
end


to connect-salient-similar

  let my-wealth wealth

  ;; Combine salience and similarity by multiplying the sampling weights for each
  ifelse wealth-visibility > 0
  [
    ifelse wealth-assortativity > 0
    [ ;; Wealthy visible + homophily
      create-links-to (rnd:weighted-n-of num-observed other turtles [(wealth - min-wealth)  * (max-delta-wealth - abs (wealth - my-wealth))])
    ]
    [ ;; Wealthy visible + heterophily
      create-links-to (rnd:weighted-n-of num-observed other turtles [(wealth - min-wealth) * abs (wealth - my-wealth)])
    ]
  ]
  [
    ifelse wealth-assortativity > 0
    [ ;; Poor visible + homophily
      create-links-to (rnd:weighted-n-of num-observed other turtles [(max-wealth - wealth) * (max-delta-wealth - abs (wealth - my-wealth))])
    ]
    [ ;; Poor visible + heterophily
      create-links-to (rnd:weighted-n-of num-observed other turtles [(max-wealth - wealth) * abs (wealth - my-wealth)])
    ]
  ]

end



;;;;;;;;;;;;;;;;;;;;;;;;
;; Runtime Procedures ;;
;;;;;;;;;;;;;;;;;;;;;;;;

to go
  ;; Update wealths based on vote from previous period
  if ticks > 0 [
    redistribute
  ]
  update-gini

  ;; Vote based on estimates of future post-tax wealths
  ask turtles [vote]
  set votes (map [?t -> [vote-decision] of ?t] sort turtles)
  set median-vote (round (median votes))

  if resize-nodes? [resize-nodes]
  color-nodes
  tick
end


to-report get-possible-utilities
  ;; Calculate utility for all possible tax rates 0-100% based on own reference group

  ;; Initialize to empty
  let possible-utilities []

  ;; Populate for any possible tax rates from 0 to 100%
  foreach (range 101) [ taxrate ->
    ;; Assume fixed tax rate (not progressive by income)
    ;; Estimate tax benefit from local sample
    let tax-benefit ((taxrate / 100) * (sum [wealth] of out-link-neighbors) / num-observed)

    let my-tax-loss (taxrate * wealth / 100)
    let my-wealth (wealth + tax-benefit - my-tax-loss)

    let neighbors-wealths ([wealth + tax-benefit - (taxrate * wealth / 100)] of out-link-neighbors)

    ;; Save all possible utilities to select the most preferable tax rate
    set possible-utilities lput (calculate-utility my-wealth neighbors-wealths my-tax-loss) possible-utilities
  ]
  report possible-utilities
end


to vote
  ;; Calculate utility for all possible tax rates 0-100% based on own reference group
  ;; in order to select best for vote
  let possible-utilities get-possible-utilities

  ifelse probabilistic?
  [
    ;; Luce's choice axiom - see https://naomi.princeton.edu/wp-content/uploads/sites/744/2021/03/RevLeoTASE2016.pdf
    ;; See also: https://bookdown.org/amesoudi/ABMtutorial_bookdown/model17.html
    let sumexp sum (map [p -> exp (hardness * p)] possible-utilities)
    set best-utility (rnd:weighted-one-of-list possible-utilities [[p] -> (exp (hardness * p)) / sumexp])
  ]
  [set best-utility (max possible-utilities)]

  set vote-decision (position best-utility possible-utilities)

  set best-utility-history lput best-utility best-utility-history
  set vote-history lput vote-decision vote-history

end


to-report calculate-utility [ #my-wealth #neighbors-wealths #tax-loss ]
  ;; Loss aversion based on amount to be paid in taxes
  let disadvantageous-ineq ( alpha * (sum (map [?val -> max (list 0 (?val - #my-wealth))] #neighbors-wealths) ) / num-observed )
  let advantageous-ineq ( beta * (sum (map [?val -> max (list 0 (#my-wealth - ?val))] #neighbors-wealths) ) / num-observed )

  let util (#my-wealth - disadvantageous-ineq - advantageous-ineq)
  report util

end


to redistribute
  ;; Update wealth based on last period's vote
  ask turtles [
    set wealth ( wealth - (median-vote * wealth / 100) + ( median-vote * (sum wealths) / (population-size * 100) ) )
  ]
  set wealths (map [?t -> [wealth] of ?t] sort turtles)
  set observed-mean-wealth (map [?t -> [mean [wealth] of out-link-neighbors] of ?t] sort turtles)
  set observed-gini (map [?t -> [local-gini [wealth] of out-link-neighbors] of ?t] sort turtles)
  set observed-subj-ineq (map [?t -> [subj-ineq wealth ([wealth] of out-link-neighbors)] of ?t] sort turtles)
end



;;;;;;;;;;;;;;;
;; Reporting ;;
;;;;;;;;;;;;;;;

to update-gini
  let sorted-wealths sort [wealth] of turtles
  let total-wealth sum sorted-wealths
  ifelse total-wealth = 0
  [
    set gini-index-reserve 0
  ]
  [
    let wealth-sum-so-far 0
    let index 0
    set gini-index-reserve 0
    let lorenz-points []
    repeat population-size [
      set wealth-sum-so-far (wealth-sum-so-far + item index sorted-wealths)
      set lorenz-points lput ((wealth-sum-so-far / total-wealth) * 100) lorenz-points
      set index (index + 1)
      set gini-index-reserve
        gini-index-reserve +
        (index / population-size) -
        (wealth-sum-so-far / total-wealth)
    ]
  ]
  ;; The multiplier (population-size / (population-size - 1)) adjusts for downward bias when population is small
  set gini (gini-index-reserve / population-size) * 2 * (population-size / (population-size - 1))
end

to-report local-gini [neighbor-wealths]
  let local-gini-reserve 0
  let sorted-wealths sort neighbor-wealths
  let total-wealth sum sorted-wealths
  ifelse total-wealth = 0
  [
    set local-gini-reserve 0
  ]
  [
    let wealth-sum-so-far 0
    let index 0
    set local-gini-reserve 0
    let lorenz-points []
    repeat num-observed [
      set wealth-sum-so-far (wealth-sum-so-far + item index sorted-wealths)
      set lorenz-points lput ((wealth-sum-so-far / total-wealth) * 100) lorenz-points
      set index (index + 1)
      set local-gini-reserve
        local-gini-reserve +
        (index / num-observed) -
        (wealth-sum-so-far / total-wealth)
    ]
  ]
  ;; The multiplier (num-observed / (num-observed - 1)) adjusts for downward bias when population is small
  report (local-gini-reserve / num-observed) * 2 * (num-observed / (num-observed - 1))
end

to-report subj-ineq [own-wealth neighbor-wealths]
  let mean-wealth-egonet (own-wealth + sum neighbor-wealths) / (num-observed + 1)
  let sum-diffs sum (map [x -> abs (x - own-wealth)] neighbor-wealths)
  report sum-diffs / (num-observed * mean-wealth-egonet)
end

to-report random-beta [ #alpha #beta ]
  let XX random-gamma #alpha 1
  let YY random-gamma #beta 1
  report XX / (XX + YY)
end




;;;;;;;;;;;;
;; Layout ;;
;;;;;;;;;;;;

to resize-nodes
  ask turtles [ set size 0.2 + sqrt max (list 1 (10 * wealth / max-wealth)) ]  ;;log (max (list 1 wealth)) 10
end

to color-nodes
  ;; Change color to be redder the higher the tax rate the turtle votes for
  ask turtles [
    set color scale-color red vote-decision 225 25
  ]
end

to layout
  ;; The number 3 here is arbitrary; more repetitions slow down the
  ;; model, but too few give poor layouts
  repeat 3 [
    ;; The more turtles we have to fit into the same amount of space,
    ;; the smaller the inputs to layout-spring we'll need to use
    let factor sqrt population-size
    ;; Numbers here are arbitrarily chosen for pleasing appearance
    layout-spring turtles links (1 / factor) (50 / factor) (20 / factor)
    display  ;; for smooth animation
  ]
end

to-report limit-magnitude [number limit]
  if number > limit [ report limit ]
  if number < (- limit) [ report (- limit) ]
  report number
end
@#$#@#$#@
GRAPHICS-WINDOW
225
10
692
478
-1
-1
9.2
1
10
1
1
1
0
0
0
1
0
49
0
49
1
1
1
ticks
30.0

BUTTON
10
380
90
420
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
10
430
100
470
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

BUTTON
110
430
200
470
go once
go
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

PLOT
710
10
950
175
Wealth distribution
NIL
NIL
0.0
10.0
0.0
10.0
true
false
"" "set-histogram-num-bars 10\nset-plot-x-range 0 (max list (max [wealth] of turtles) 1)\nset-plot-pen-interval ((max [wealth] of turtles) / 10)"
PENS
"default" 1.0 1 -16777216 true "" "histogram ([wealth] of turtles)"

SLIDER
10
10
205
43
population-size
population-size
10
1000
200.0
10
1
NIL
HORIZONTAL

PLOT
960
10
1200
175
Gini index vs. time
Time
Gini
0.0
100.0
0.0
1.0
true
false
"" ""
PENS
"default" 1.0 0 -955883 true "" "plot gini"

SWITCH
10
340
140
373
resize-nodes?
resize-nodes?
0
1
-1000

SLIDER
10
180
210
213
wealth-assortativity
wealth-assortativity
-1
1
1.0
0.1
1
NIL
HORIZONTAL

SLIDER
10
50
205
83
num-observed
num-observed
1
20
8.0
1
1
NIL
HORIZONTAL

PLOT
710
190
950
340
Vote decisions
Vote decision
Frequency
0.0
10.0
0.0
10.0
true
false
"" "set-histogram-num-bars 10\nset-plot-x-range 0 101\nset-plot-y-range 0 20\nset-plot-pen-interval 1"
PENS
"default" 1.0 1 -13345367 true "" "histogram ([vote-decision] of turtles)"

SLIDER
10
240
210
273
wealth-visibility
wealth-visibility
-1
1
0.0
0.1
1
NIL
HORIZONTAL

SLIDER
10
125
102
158
a
a
0.5
5
1.0
0.5
1
NIL
HORIZONTAL

SLIDER
115
125
207
158
b
b
1
20
6.0
1
1
NIL
HORIZONTAL

TEXTBOX
10
95
230
136
a, b determine initial Gini\nb > a for right-skewed distribution
11
0.0
1

PLOT
915
360
1105
500
Visibility by wealth
Wealth
Indegree
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 2 -16777216 true "ask turtles [plotxy wealth (count my-in-links)]" ""

PLOT
710
360
905
500
Assortativity by wealth
Own wealth
Neighbors' mean wealth
0.0
10.0
0.0
10.0
true
false
"" ""
PENS
"default" 1.0 2 -16777216 true "ask turtles [plotxy wealth (mean [wealth] of out-link-neighbors)]" ""

PLOT
960
190
1200
340
Agreed tax rate
NIL
NIL
0.0
10.0
0.0
100.0
true
false
"" ""
PENS
"default" 1.0 0 -16777216 true "" "plot median-vote"

PLOT
1115
360
1375
560
Observed Gini by wealth
Own wealth
Observed Gini
0.0
100.0
0.0
1.0
true
false
"" ""
PENS
"default" 1.0 2 -16777216 true "" "ask turtles [plotxy wealth (local-gini [wealth] of out-link-neighbors)]"

SWITCH
10
285
140
318
probabilistic?
probabilistic?
0
1
-1000

TEXTBOX
10
165
220
191
>0 for homophily, <0 for heterophily
11
0.0
1

TEXTBOX
10
225
235
251
> 0 for rich visible, < 0 for poor visible
11
0.0
1

PLOT
1210
190
1410
340
Observed subjective inequality by wealth
Own wealth
Experienced differences
0.0
100.0
0.0
1.0
true
false
"" ""
PENS
"default" 1.0 2 -16777216 true "" "ask turtles [plotxy wealth (subj-ineq wealth [wealth] of out-link-neighbors)]"

@#$#@#$#@
## WHAT IS IT?

This model explores the effects of network structure on individual perception of inequality, individual preferences for redistribution, and voted redistirbution policy. 


## HOW IT WORKS

The agents in the model observe the wealth of a subsample of the population and vote on a tax rate with probability proportional to the utility they obtain from redistributing wealth. The agents value more wealth but are also inequity averse, disliking having much less than their neighbors and, to a lesser extent, having much more than them. Once everyone in the population has cast their vote, the median M% vote is selected and implemented, such that everyone pays M% of their wealth as tax and receives a benefit back. The benefit comes from equally splitting the collected tax revenue among the population.

## HOW TO USE IT

The POPULATION-SIZE slider sets how many agents are in the world.

The NUM-OBSERVED slider sets the average number of neighbors (reference sample) that agents observe.

The A and B sliders are the two parameters in the Beta distribution that defines how initial wealth is distributed.

WEALTH-ASSORTATIVITY determines the level of positive assortativity (if > 0) or negative assortativity (if < 0) in the network. Positiive assortativity implies that agents are more likely to observe others with similar wealth while negative assortativity suggests that agents are more likely to observe others with dissimilar wealth.

WEALTH-VISIBILITY determines who is more likely to be observed, regardless of the observer's own wealth. Values > 0 make agents more likely to observe the wealthy, while values < 0 make agents more likely to observe the poor.

Press SETUP to populate the world with agents. GO will run the simulation continuously, while GO ONCE will run one tick.

When RESIZE-NODES is selected, the agents with higher wealth will be represented with larger nodes.

The WEALTH-DISTRIBUTION histogram on the right shows the distribution of wealth.

The GINI INDEX VS. TIME plot shows a measure of the inequity of the distribution over time.  A GINI INDEX of 0 equates to everyone having the exact same amount of wealth, and a GINI INDEX of 1 equates to the most skewed wealth distribution possible, where a single person has all the wealth, and no one else has any.

The VOTE DECISIONS plot shows the distributions of votes from 0 to 100% tax rate.

The AGREED TAX RATE plot shows the change in the median vote over time.

The ASSORTATIVITY BY WEALTH plot shows the mean wealth of one's neighbors versus one's own wealth.

The VISIBILITY BY WEALTH plot shows the number of times one is observed by others versus one's own wealth.


## HOW TO CITE

For the model itself:

* Tsvetkova, M., Olsson, H., & Galesic, M. (2024). Social networks affect redistribution decisions and polarization. https://doi.org/10.31219/osf.io/bw7ux

Please cite the NetLogo software as:

* Wilensky, U. (1999). NetLogo. http://ccl.northwestern.edu/netlogo/. Center for Connected Learning and Computer-Based Modeling, Northwestern University, Evanston, IL.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.4.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="high-ineq" repetitions="100" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="3"/>
    <metric>gini</metric>
    <metric>median-vote</metric>
    <metric>num-observers</metric>
    <metric>observed-mean-wealth</metric>
    <metric>observed-gini</metric>
    <metric>observed-subj-ineq</metric>
    <metric>wealths</metric>
    <metric>utilities</metric>
    <metric>votes</metric>
    <enumeratedValueSet variable="population-size">
      <value value="200"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-observed">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="resize-nodes?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="probabilistic?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="gamma">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="a">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="b">
      <value value="6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="wealth-assortativity">
      <value value="-1"/>
      <value value="-0.5"/>
      <value value="0"/>
      <value value="0.5"/>
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="wealth-visibility">
      <value value="-1"/>
      <value value="-0.5"/>
      <value value="0"/>
      <value value="0.5"/>
      <value value="1"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="low-ineq" repetitions="100" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="3"/>
    <metric>gini</metric>
    <metric>median-vote</metric>
    <metric>num-observers</metric>
    <metric>observed-mean-wealth</metric>
    <metric>observed-gini</metric>
    <metric>observed-subj-ineq</metric>
    <metric>wealths</metric>
    <metric>utilities</metric>
    <metric>votes</metric>
    <enumeratedValueSet variable="population-size">
      <value value="200"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-observed">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="resize-nodes?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="probabilistic?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="gamma">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="a">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="b">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="wealth-assortativity">
      <value value="-1"/>
      <value value="-0.5"/>
      <value value="0"/>
      <value value="0.5"/>
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="wealth-visibility">
      <value value="-1"/>
      <value value="-0.5"/>
      <value value="0"/>
      <value value="0.5"/>
      <value value="1"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
1
@#$#@#$#@
