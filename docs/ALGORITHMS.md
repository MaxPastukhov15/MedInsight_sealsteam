# Математические алгоритмы

## Scenario 1: Disease Analysis

### Метод
Агрегация SQL + простая статистика

### Формулы

```
Mortality Rate = (Deaths / Total Cases) * 100%

Trend Percentage = ((Current - Previous) / Previous) * 100%
```

---

## Scenario 2: Trend Analysis

### Метод
Линейная регрессия (scipy.stats.linregress)

### Формула

```
y = mx + b

where:
  y = cases
  x = time (days)
  m = slope (угол наклона)
  b = intercept

Interpretation:
  m > 0 → RISING
  m < 0 → FALLING
  |m| < threshold → STABLE

R-squared:
  Показывает качество аппроксимации
  R² = 1 - (SS_res / SS_tot)
```

---

## Scenario 3: Forecasting

### Ensemble: Prophet (60%) + ARIMA (40%)

#### Prophet (Facebook)

```
y(t) = g(t) + s(t) + h(t) + ε(t)

where:
  g(t) = trend (линейный или логистический)
  s(t) = seasonality (сезонность)
  h(t) = holidays (праздники)
  ε(t) = error term

Seasonality:
  s(t) = Σ [a_n * cos(2πnt/P) + b_n * sin(2πnt/P)]

Confidence Intervals (95%):
  [y_pred - 1.96*σ, y_pred + 1.96*σ]
```

#### ARIMA (p, d, q)

```
ARIMA Model:
  AR (AutoRegressive): y_t = c + Σ φ_i * y_{t-i}
  I (Integrated): differencing to make stationary
  MA (Moving Average): Σ θ_i * ε_{t-i}

Parameters:
  p = AR order (lags)
  d = differencing degree
  q = MA order (lags)

Auto-selection:
  AIC = 2k - 2ln(L)
  Выбираем (p,d,q) с минимальным AIC
```

#### Ensemble Combination

```
final_forecast = 0.6 * prophet_forecast + 0.4 * arima_forecast

final_confidence_lower = min(prophet_lower, arima_lower)
final_confidence_upper = max(prophet_upper, arima_upper)
```

---

## Scenario 4: Recommendations

### RAG Pipeline

```
1. Embedding:
   embedding = SentenceTransformer.encode(query)
   → vector[384] или vector[768]

2. Vector Search:
   similarity = cosine_similarity(query_embedding, doc_embeddings)
   top_k = argsort(similarity)[-5:]

3. LLM Generation:
   context = retrieve_documents(top_k)
   prompt = f"Context: {context}\n\nQuery: {query}"
   response = LLM.generate(prompt)
```

---

## Scenario 5: Pattern Detection

### Anomaly Detection (Z-score)

```
Z-score = (x - μ) / σ

where:
  x = observed value
  μ = mean
  σ = standard deviation

Decision:
  |Z-score| > 2 → anomaly (95% confidence)
  |Z-score| > 3 → severe anomaly (99.7% confidence)
```

### Correlation (Pearson)

```
r = Σ[(x_i - x̄)(y_i - ȳ)] / √[Σ(x_i - x̄)² * Σ(y_i - ȳ)²]

Interpretation:
  r > 0.7 → strong positive correlation
  r < -0.7 → strong negative correlation
  |r| < 0.3 → weak correlation
```

### Seasonality Detection (STL)

```
STL Decomposition:
  Y_t = T_t + S_t + R_t

where:
  T_t = trend
  S_t = seasonal component
  R_t = residual

Seasonality Strength:
  F_s = 1 - Var(R_t) / Var(S_t + R_t)
  F_s > 0.6 → strong seasonality
```
