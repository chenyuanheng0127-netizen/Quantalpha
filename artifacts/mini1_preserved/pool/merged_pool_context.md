Use the following historical pool as prior knowledge.
Prefer proposing hypotheses that are novel combinations, not minor rewrites.

## Historical Hypotheses (sample up to 40)
1. The daily close location within the high-low range, normalized by the square root of volume, negatively predicts next-day returns due to intraday overextension and low liquidity.
2. Stocks with closing price deviating significantly from VWAP, relative to daily range and accompanied by high volume, will experience a mean-reversion over the next few days.
3. Today's opening price relative to yesterday's VWAP scaled by yesterday's intraday range predicts a short-term mean-reversion in returns.
4. The overnight price gap relative to recent VWAP, adjusted by intraday volatility, predicts short-term return reversal due to market overreaction to overnight news.
5. The divergence between volume-weighted and equal-weighted daily returns over a 20-day lookback captures institutional accumulation/distribution patterns, predicting future returns.
6. Large overnight gaps relative to recent true range, when accompanied by shrinking relative volume, predict short-term price reversals due to exhaustion of the initial shock.
7. Deviation of the 20-day volume-price return correlation from its 60-day historical average signals shifts in trend confirmation, predicting short-term reversals or continuations.
8. The factor is the z-scored product of relative volume and close-to-VWAP deviation, capturing volume-confirmed price conviction to predict short-term returns.
9. The 10-day EWMA of daily (close - VWAP)/VWAP, termed VWAP drift, positively predicts forward returns as it captures persistent informed buying pressure.
10. Price momentum not confirmed by volume-weighted average price (VWAP) momentum over a 10-day window signals an unsustainable trend and predicts future return reversal.
11. The interaction between intraday price location relative to VWAP and relative volume predicts short-term price continuation or reversal.
12. Intraday volatility asymmetry, measured by the ratio of average down-day high-low range to up-day high-low range over a 20-day window, predicts negative future stock returns.

## Historical Expressions (sample up to 80)
1. TS_ZSCORE(SUMIF($volume, 20, $return < 0) / (SUMIF($volume, 20, $return > 0) + 1e-8), 60)
2. TS_ZSCORE(SUMIF($volume, 20, $return < 0) / (TS_SUM($volume, 20) + 1e-8), 60)
3. TS_ZSCORE((SUMIF($volume, 20, $return < 0) - SUMIF($volume, 20, $return > 0)) / (TS_SUM($volume, 20) + 1e-8), 60)
4. TS_ZSCORE(SUMIF($volume, 20, $close < DELAY($close,1)) / (SUMIF($volume, 20, $close > DELAY($close,1)) + 1e-8), 60)
5. TS_ZSCORE(SUMIF($volume, 20, $close < DELAY($close, 1)) / (TS_SUM($volume, 20) + 1e-8), 60)
6. TS_ZSCORE((SUMIF($volume, 20, DELTA($close, 1) < 0) - SUMIF($volume, 20, DELTA($close, 1) > 0)) / (TS_SUM($volume, 20) + 1e-8), 60)
7. (TS_SUM($return * $volume, 20) / (TS_SUM($volume, 20) + 1e-8)) / (TS_MEAN($return, 20) + 1e-8)
8. (SUMIF($volume, 20, $return > 0) - SUMIF($volume, 20, $return < 0)) / (TS_SUM($volume, 20) + 1e-8)
9. (TS_SUM($return * $volume, 20) / (TS_SUM($volume, 20) + 1e-8) - TS_MEAN($return, 20)) / (TS_STD($return, 20) + 1e-8)
10. (($close - (($high + $low + $close) / 3)) / MAX($high - $low, 1e-8)) * ($volume / (TS_MEAN($volume, 20) + 1e-8))
11. (($close - EMA($close, 20)) / MAX($high - $low, 1e-8)) * ($volume / (TS_MEAN($volume, 20) + 1e-8))
12. RANK((($close - $low) / ($high - $low + 1e-8)) * ($volume / TS_MEAN($volume, 20)))
13. RANK((($close - $low) / ($high - $low + 1e-8)) - TS_MEAN(($close - $low) / ($high - $low + 1e-8), 5))
14. ZSCORE((($close - $low) / ($high - $low + 1e-8)) * ($volume / TS_MEAN($volume, 20)))
15. RANK((($close - $open) / ($high - $low + 1e-8)) * ($volume / TS_MEDIAN($volume, 20)))
16. RANK(($close - $open) / ($high - $low + 1e-8)) * RANK($volume / TS_MEDIAN($volume, 20))
17. RANK((($close - $open) / ($high - $low + 1e-8)) * TS_ZSCORE($volume, 20))
18. EMA(SIGN($close - $open) * (ABS($close - $open) / (ABS($high - $low) + 1e-8)) * (($volume - TS_MEAN($volume, 20)) / (TS_STD($volume, 20) + 1e-8)), 5)
19. EMA(SIGN($close - $open) * (ABS($close - $open) / (ABS($high - $low) + 1e-8)) * ($volume / (TS_MEDIAN($volume, 20) + 1e-8) - 1), 5)
20. EMA(SIGN($close - $open) * (RANK(ABS($close - $open) / (ABS($high - $low) + 1e-8)) + RANK(($volume - TS_MEAN($volume, 20)) / (TS_STD($volume, 20) + 1e-8))), 5)
21. ($open - DELAY($close, 1)) / (DELAY($high, 1) - DELAY($low, 1) + 1e-6)
22. ($open - (DELAY($high,1)+DELAY($low,1)+DELAY($close,1))/3) / (DELAY($high,1) - DELAY($low,1) + 1e-6)
23. (2*$close - $high - $low) / (($high - $low) + 1e-8) / (SQRT($volume) + 1e-8)
24. ZSCORE((2*$close - $high - $low) / (($high - $low) + 1e-8) / (SQRT($volume) + 1e-8))
25. TS_MEAN((2*$close - $high - $low) / (($high - $low) + 1e-8) / (SQRT($volume) + 1e-8), 5)
26. TS_CORR(TS_RANK($return, 10), TS_RANK(TS_PCTCHANGE($volume, 1), 10), 10)
27. TS_CORR($return, TS_PCTCHANGE($volume, 1), 10)
28. (TS_SUM(TS_PCTCHANGE($close, 1) * $volume, 20) / (TS_SUM($volume, 20) + 1e-8)) / (TS_MEAN(TS_PCTCHANGE($close, 1), 20) + 1e-8)
29. ($close - (TS_SUM($close * $volume, 10) / TS_SUM($volume, 10))) / (TS_STD($close, 10) + 1e-8)
30. ($close - ($high + $low + $close) / 3) / (TS_STD($close, 10) + 1e-8)
31. (SUMIF($volume, 20, DELTA($close, 1) > 0) - SUMIF($volume, 20, DELTA($close, 1) < 0)) / (TS_SUM($volume, 20) + 1e-8)
32. EMA(($close - $open) / ($high - $low + 1e-8), 10)
33. EMA(($close - ($high + $low)/2) / ($high - $low + 1e-8), 10)
34. (($close - (($high + $low)/2)) / (($high - $low) + 1e-8)) * ($volume / (TS_MEAN($volume, 20) + 1e-8))
35. (($close - (($high + $low + $close)/3)) / (($high - $low) + 1e-8)) * ($volume / (TS_MEAN($volume, 20) + 1e-8))
36. RANK((($close - (($high + $low)/2)) / (($high - $low) + 1e-8)) * ($volume / (TS_MEAN($volume, 20) + 1e-8)))
37. TS_COVARIANCE($volume, $return, 20) / (TS_VAR($return, 20) + 1e-8)
38. RANK(TS_COVARIANCE($volume, $return, 20) / (TS_VAR($return, 20) + 1e-8))
39. TS_COVARIANCE($volume, $return, 10) / (TS_VAR($return, 10) + 1e-8)
40. -(DELTA(DELTA(3*$close/($high+$low+$close)-1, 1), 1)) / (TS_STD(3*$close/($high+$low+$close)-1, 20) + 1e-8)
41. ($close / TS_MEAN($close, 20) - 1) * ($volume / TS_MEAN($volume, 20))
42. -(DELTA(DELTA($close/$open-1, 1), 1)) / (TS_STD($close/$open-1, 20) + 1e-8)
43. ($close / (($high + $low + $close) / 3) - 1) * ($volume / TS_MEAN($volume, 20))
44. (($close - $open) / $open) * ($volume / TS_MEAN($volume, 20))
45. -(DELTA(DELTA($close/TS_MEAN($close,5)-1, 1), 1)) / (TS_STD($close/TS_MEAN($close,5)-1, 20) + 1e-8)
46. ABS($close - DELAY($close, 20)) / (TS_SUM(ABS($high - $low), 20) + 1e-8)
47. ABS($close - DELAY($close, 20)) / (TS_STD($return, 20) * SQRT(20) + 1e-8)
48. RSI($close, 14)
49. -( (($close - $low)/($high - $low + 1e-8) - TS_MEAN(($close - $low)/($high - $low + 1e-8), 20)) * (TS_RANK($volume, 20) / 20) )
50. TS_SUM($return, 20) / (TS_SUM(ABS($return) / ($close * $volume), 20) + 1e-8)
51. ZSCORE(TS_SUM($return, 20) / (TS_SUM(ABS($return) / ($close * $volume), 20) + 1e-8))
52. TS_COVARIANCE($volume, TS_PCTCHANGE($close, 1), 20) / (TS_VAR(TS_PCTCHANGE($close, 1), 20) + 1e-8)
53. RANK((($open - SMA($close, 10, 1)) / (TS_MEAN($high - $low, 10) + 1e-8)))
54. RANK(TS_ZSCORE($open - DELAY($close, 1), 10))
55. RANK(($high - $low)/$close * MAX($volume / SMA($volume, 20) - 1, 0))
56. RANK(TS_MEAN(($high - $low)/$close * ($volume / SMA($volume, 20) - 1), 5))
57. RANK(($volume / SMA($volume, 20) - 1) * TS_STD($close, 20) / ($high - $low + 1e-8))
58. RANK(TS_COVARIANCE($volume, TS_PCTCHANGE($close, 1), 20) / (TS_VAR(TS_PCTCHANGE($close, 1), 20) + 1e-8))
59. TS_COVARIANCE($volume, TS_PCTCHANGE($close, 1), 10) / (TS_VAR(TS_PCTCHANGE($close, 1), 10) + 1e-8)
60. TS_SUM($volume * $return, 20) / TS_SUM($volume, 20) - TS_MEAN($return, 20)
61. TS_SUM($volume * $return, 10) / TS_SUM($volume, 10) - TS_MEAN($return, 10)
62. TS_SUM($volume * $return, 20) / TS_SUM($volume, 20)
63. TS_PCTCHANGE($close, 20) / (TS_SUM(ABS(TS_PCTCHANGE($close, 1)) / ($close * $volume), 20) + 1e-8)
64. TS_MEAN(($high+$low+$close)/3/$close - 1, 10)
65. TS_MEAN(($high+$low+$close)/3/$close - 1, 20)
66. EMA(($high+$low+$close)/3/$close - 1, 10)
67. RANK((($open - TS_MEAN(DELAY($close, 1), 10)) / (TS_MEAN(DELAY($high - $low, 1), 10) + 1e-8)))
68. RANK((EMA($high - $low, 10) / (EMA($close, 10) + 1e-8)) * ($volume / (TS_MEAN($volume, 20) + 1e-8)))
69. COUNT($high - $low > TS_MEAN($high - $low, 20) && $volume > TS_MEAN($volume, 20), 10)
70. RANK(EMA($high - $low, 10) * TS_ZSCORE($volume, 20))
71. ZSCORE(($close / DELAY($close, 20) - 1) / (TS_MEAN(ABS($close / DELAY($close, 1) - 1) / ($close * $volume), 20) + 1e-8))
72. ABS($close - DELAY($close, 20)) / (TS_STD(($close / (DELAY($close, 1) + 1e-8) - 1), 20) * SQRT(20) + 1e-8)
73. -(DELTA(DELTA(3*$close/($high+$low+$close)-1, 5), 5)) / (TS_STD(3*$close/($high+$low+$close)-1, 20) + 1e-8)
74. TS_SUM($volume * TS_PCTCHANGE($close, 1), 20) / TS_SUM($volume, 20) - TS_MEAN(TS_PCTCHANGE($close, 1), 20)
75. RANK(($high - $low)/$close * MAX($volume / SMA($volume, 20, 1) - 1, 0))
76. TS_SUM($volume * TS_PCTCHANGE($close, 1), 10) / TS_SUM($volume, 10) - TS_MEAN(TS_PCTCHANGE($close, 1), 10)
77. -(DELTA(DELTA($close/$open-1, 5), 5)) / (TS_STD($close/$open-1, 20) + 1e-8)
78. RANK(TS_MEAN(($high - $low)/$close * ($volume / TS_MEAN($volume, 20) - 1), 5))
79. TS_SUM($volume * TS_PCTCHANGE($close, 1), 20) / TS_SUM($volume, 20)
80. TS_SUM(TS_PCTCHANGE($close, 1), 20) / (TS_SUM(ABS(TS_PCTCHANGE($close, 1)) / ($close * $volume), 20) + 1e-8)


## From mine_step3_poolA refresh (2026-05-06, cleaned)
### Hypotheses from last run

1. Concurrent alignment of overnight gap direction and intraday return direction, amplified by volume deviation, predicts short-term continuation when aligned and reversal when directions conflict.
2. Volume-weighted skewness of daily returns over a 20-day window, normalized by a 60-day rolling z-score, may capture asymmetric informed flow; verify operators supported in your function library.
3. When daily price acceleration (second difference) is large versus its 20-day volatility and volume is below its 5-day average, mean-reversion is more likely.
4. Five-day acceleration of intraday closing bias, normalized by 20-day volatility, may proxy institutional pressure exhaustion (directional hypothesis for further testing).

### Expressions (AST/regulator-evaluated, unique vs prior pool)

1. TS_ZSCORE(TS_SKEW($return, 20), 60)
2. TS_ZSCORE(SUMIF($volume, 20, $return > 0) - SUMIF($volume, 20, $return < 0), 60)
3. TS_ZSCORE(TS_SKEW($return * $volume / (TS_MEAN($volume, 20) + 1e-8), 20), 60)
4. TS_ZSCORE((TS_MEAN(POW($close / DELAY($close, 1) - 1, 3), 20) - 3 * TS_MEAN($close / DELAY($close, 1) - 1, 20) * TS_MEAN(POW($close / DELAY($close, 1) - 1, 2), 20) + 2 * POW(TS_MEAN($close / DELAY($close, 1) - 1, 20), 3)) / POW(TS_STD($close / DELAY($close, 1) - 1, 20), 3), 60)
5. TS_ZSCORE(SUMIF($volume, 20, $close > DELAY($close,1)) - SUMIF($volume, 20, $close < DELAY($close,1)), 60)
6. TS_ZSCORE(TS_MEAN(POW((($close / DELAY($close, 1) - 1) * $volume / (TS_MEAN($volume, 20) + 1e-8) - TS_MEAN(($close / DELAY($close, 1) - 1) * $volume / (TS_MEAN($volume, 20) + 1e-8), 20)), 3), 20) / (POW(TS_STD(($close / DELAY($close, 1) - 1) * $volume / (TS_MEAN($volume, 20) + 1e-8), 20), 3) + 1e-8), 60)
7. RANK(SIGN($open - DELAY($close, 1)) * SIGN($close - $open) * ($volume / TS_MEAN($volume, 20) - 1))
8. RANK(SIGN($open - DELAY($close, 1)) * SIGN($close - $open) * TS_ZSCORE($volume, 20))
9. COUNT((SIGN($open - DELAY($close, 1)) == SIGN($close - $open)) && ($volume > TS_MEAN($volume, 20)), 5)
10. COUNT((SIGN($open - DELAY($close, 1)) * SIGN($close - $open) > 0) && ($volume > TS_MEAN($volume, 20)), 5)
11. TS_ZSCORE(TS_MEAN(POW(TS_ZSCORE(($close / DELAY($close, 1) - 1) * $volume / (TS_MEAN($volume, 20) + 1e-8), 20), 3), 20), 60)
12. TS_ZSCORE(TS_MEAN(POW(($close/DELAY($close,1)-1) - TS_MEAN($close/DELAY($close,1)-1,20), 3), 20) / POW(TS_STD($close/DELAY($close,1)-1, 20), 3), 60)
13. TS_ZSCORE(TS_SKEW(($close / DELAY($close, 1) - 1) * $volume / (TS_MEAN($volume, 20) + 1e-8), 20), 60)
14. TS_ZSCORE(TS_MEAN(POW(($close / DELAY($close, 1) - 1) * $volume / (TS_MEAN($volume, 20) + 1e-8) - TS_MEAN(($close / DELAY($close, 1) - 1) * $volume / (TS_MEAN($volume, 20) + 1e-8), 20), 3), 20) / (POW(TS_STD(($close / DELAY($close, 1) - 1) * $volume / (TS_MEAN($volume, 20) + 1e-8), 20), 3) + 1e-8), 60)
