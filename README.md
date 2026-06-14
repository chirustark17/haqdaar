# House Prices: Advanced Regression Techniques

## Competition Overview

This project tackles the Kaggle House Prices competition, which challenges participants to predict residential home sale prices in Ames, Iowa using 79 explanatory variables covering nearly every aspect of the properties.

**Competition Goal:** Predict the final sale price for each house in the test set.

**Evaluation Metric:** Root-Mean-Squared-Error (RMSE) between the logarithm of predicted and observed sale prices.

---

## Project Structure

```
house-prices/
├── train.csv                      # Training data (1,460 samples)
├── test.csv                       # Test data (1,459 samples)
├── data_description.txt           # Feature descriptions
├── sample_submission.csv          # Submission format example
├── house_price_predictor.py       # Main prediction pipeline
├── analysis_visualization.py      # EDA and visualization
├── submission.csv                 # Final predictions
├── house_prices_analysis.png      # Key visualizations
├── correlation_heatmap.png        # Feature correlations
└── README.md                      # This file
```

---

## Dataset Overview

### Target Variable: SalePrice
- **Mean:** $180,921
- **Median:** $163,000
- **Range:** $34,900 - $755,000
- **Distribution:** Right-skewed (skewness = 1.88)

### Features
- **Total Features:** 79 explanatory variables
- **Numerical Features:** 36 (areas, counts, years, etc.)
- **Categorical Features:** 43 (quality ratings, types, etc.)
- **Missing Data:** Ranges from 0.07% to 99.5% across features

### Key Feature Categories

1. **Size/Area Features** (Avg. correlation: 0.52)
   - GrLivArea, TotalBsmtSF, 1stFlrSF, GarageArea, LotArea

2. **Quality Features** (Avg. correlation: 0.43)
   - OverallQual (0.79), ExterQual, KitchenQual, BsmtQual

3. **Garage Features** (Avg. correlation: 0.63)
   - GarageCars (0.64), GarageArea (0.62), GarageType, GarageFinish

4. **Room Count Features** (Avg. correlation: 0.40)
   - FullBath, BedroomAbvGr, TotRmsAbvGrd, Fireplaces

5. **Time Features** (Avg. correlation: 0.39)
   - YearBuilt, YearRemodAdd, GarageYrBlt

---

## Methodology

### 1. Data Preprocessing

#### Missing Value Imputation
- **Categorical NA = "None":** Pool, Garage, Basement, Fireplace features (NA indicates absence)
- **Numerical NA = 0:** MasVnrArea, Basement SF, Garage measurements
- **LotFrontage:** Filled with neighborhood median
- **Other features:** Mode (categorical) or median (numerical)

#### Outlier Handling
- Identified ~4% outliers in key features using IQR method
- Retained outliers as they represent legitimate high-value properties
- Used robust scaling to minimize outlier impact

### 2. Feature Engineering

Created 17 new features to capture additional patterns:

**Aggregate Features:**
- `TotalSF` = TotalBsmtSF + 1stFlrSF + 2ndFlrSF (Correlation: 0.78)
- `TotalBath` = FullBath + 0.5×HalfBath + BsmtFullBath + 0.5×BsmtHalfBath
- `TotalPorchSF` = Sum of all porch areas

**Age Features:**
- `HouseAge` = YrSold - YearBuilt
- `RemodAge` = YrSold - YearRemodAdd  
- `GarageAge` = YrSold - GarageYrBlt

**Binary Indicators:**
- HasPool, Has2ndFloor, HasGarage, HasBsmt, HasFireplace

**Quality Indices:**
- `OverallScore` = OverallQual × OverallCond
- `ExterScore`, `KitchenScore` (mapped quality ratings to numeric)

**Ratios:**
- `LotAreaRatio` = GrLivArea / LotArea
- `GarageRatio` = GarageArea / GrLivArea
- `BasementRatio` = TotalBsmtSF / GrLivArea

### 3. Data Transformation

**Skewness Handling:**
- Applied log1p transformation to 58 highly skewed features (|skew| > 0.75)
- Target variable transformed using log1p for RMSE calculation

**Categorical Encoding:**
- Label encoding for 43 categorical features
- Preserved ordinal relationships in quality ratings

**Feature Scaling:**
- RobustScaler applied to all features
- Reduces influence of outliers while maintaining distributions

### 4. Model Selection & Ensemble

#### Individual Models

| Model | CV RMSE | Weight | Description |
|-------|---------|---------|-------------|
| **Ridge Regression** | 0.1394 | 24.3% | L2 regularization (α=10.0) |
| **Lasso Regression** | 0.1385 | 24.5% | L1 regularization (α=0.0005) |
| **ElasticNet** | 0.1387 | 24.4% | Combined L1+L2 (α=0.0005, l1_ratio=0.9) |
| **Gradient Boosting** | 0.1266 | 26.8% | 3000 trees, learning_rate=0.05 |

#### Ensemble Strategy
- **Weighted Average:** Each model weighted by inverse of its CV RMSE
- **Best Model:** Gradient Boosting (lowest individual CV score)
- **Ensemble Benefit:** Reduces variance and improves generalization

### 5. Cross-Validation
- **Strategy:** 5-Fold KFold with shuffling
- **Scoring:** Negative MSE (for RMSE calculation)
- **Purpose:** Reliable performance estimation and prevent overfitting

---

## Key Findings

### Top 10 Predictive Features

1. **OverallQual** (0.79) - Overall material and finish quality
2. **GrLivArea** (0.71) - Above grade living area
3. **GarageCars** (0.64) - Garage capacity
4. **GarageArea** (0.62) - Garage size in sq ft
5. **TotalBsmtSF** (0.61) - Total basement area
6. **1stFlrSF** (0.61) - First floor area
7. **FullBath** (0.56) - Number of full bathrooms
8. **TotRmsAbvGrd** (0.53) - Total rooms above grade
9. **YearBuilt** (0.52) - Original construction date
10. **YearRemodAdd** (0.51) - Remodel date

### Insights

1. **Quality Over Quantity:** Overall quality rating is the strongest predictor (0.79 correlation)
2. **Living Space Matters:** Combined living area (TotalSF) shows 0.78 correlation
3. **Garage Impact:** Garage features collectively contribute significantly
4. **Age Effect:** Newer homes (0-10 years) command ~70% premium over 50+ year old homes
5. **Neighborhood Premium:** Top neighborhoods (NridgHt, NoRidge) have 2.5x higher median prices

---

## Model Performance

### Cross-Validation Results
- **Gradient Boosting:** 0.1266 RMSE (Best single model)
- **Ensemble Average:** ~0.127 RMSE (estimated)
- **Variance:** ±0.021 RMSE across folds

### Prediction Statistics
- **Range:** $48,297 - $569,624
- **Mean:** $177,833
- **Distribution:** Similar to training data (aligned with $180,921 train mean)

---

## Usage

### Run Complete Pipeline
```bash
python house_price_predictor.py
```

**Output:**
- `submission.csv` - Competition predictions
- Console logs with detailed progress and metrics

### Run Analysis & Visualizations
```bash
python analysis_visualization.py
```

**Output:**
- `house_prices_analysis.png` - Key visualizations
- `correlation_heatmap.png` - Feature correlation matrix
- Detailed statistical analysis in console

### Requirements
```python
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=1.0.0
matplotlib>=3.4.0
seaborn>=0.11.0
scipy>=1.7.0
```

---

## Advanced Techniques Applied

1. **Smart Missing Value Imputation**
   - Domain-specific logic (NA = "None" for absent features)
   - Neighborhood-based imputation for LotFrontage

2. **Comprehensive Feature Engineering**
   - Aggregate metrics (TotalSF shows 0.78 correlation)
   - Interaction features (quality × condition scores)
   - Temporal features (house age, remodel age)

3. **Distribution Normalization**
   - Log transformation for skewed features
   - Target transformation for symmetric loss function

4. **Ensemble Learning**
   - Multiple regression algorithms (Linear + Tree-based)
   - Weighted averaging by performance
   - Combines strengths of different model types

5. **Robust Scaling**
   - Minimizes outlier influence
   - Preserves feature distributions
   - Improves model convergence

---

## Model Comparison

### Why This Ensemble Works

**Linear Models (Ridge/Lasso/ElasticNet):**
- ✅ Handle multicollinearity well
- ✅ Fast training and prediction
- ✅ Interpretable coefficients
- ❌ Assume linear relationships

**Gradient Boosting:**
- ✅ Captures non-linear patterns
- ✅ Handles feature interactions
- ✅ Robust to outliers
- ❌ More complex, risk of overfitting

**Combined Ensemble:**
- ✅ Best of both worlds
- ✅ More robust predictions
- ✅ Reduced variance
- ✅ Better generalization

---

## Future Improvements

1. **Advanced Feature Engineering**
   - Polynomial features for key predictors
   - More sophisticated interaction terms
   - Geographic clustering of neighborhoods

2. **Additional Models**
   - XGBoost (alternative boosting algorithm)
   - LightGBM (faster gradient boosting)
   - Neural networks for deep feature learning
   - Stacking ensemble with meta-learner

3. **Hyperparameter Tuning**
   - Grid search for optimal parameters
   - Bayesian optimization
   - Cross-validated parameter selection

4. **Outlier Treatment**
   - Separate modeling for high-value properties
   - Outlier removal and impact analysis
   - Robust loss functions

5. **External Data**
   - Economic indicators (interest rates, GDP)
   - School district ratings
   - Crime statistics
   - Local amenities and infrastructure

---

## Competition Tips

1. **Public vs Private Leaderboard:**
   - Public: Based on 50% of test data
   - Private: Remaining 50% (determines final ranking)
   - Avoid overfitting to public leaderboard

2. **Submission Strategy:**
   - Select 2 submissions for final judging
   - Choose models with best CV scores
   - Diversify selection (e.g., one conservative, one aggressive)

3. **Best Practices:**
   - Always use cross-validation
   - Monitor training vs validation performance
   - Keep track of feature engineering experiments
   - Document model versions and parameters

---

## References

- **Competition:** [Kaggle House Prices](https://www.kaggle.com/c/house-prices-advanced-regression-techniques)
- **Dataset Source:** Dean De Cock, Ames Housing Dataset
- **Original Paper:** [Alternative to Boston Housing Data](http://jse.amstat.org/v19n3/decock.pdf)

---

## Author Notes

This solution demonstrates end-to-end machine learning workflow:
- ✅ Thorough exploratory data analysis
- ✅ Intelligent feature engineering
- ✅ Multiple modeling approaches
- ✅ Robust validation strategy
- ✅ Production-ready code structure

**Key Takeaway:** In real estate prediction, quality (OverallQual) and total living space (TotalSF) are the most critical factors, with newer homes and desirable neighborhoods commanding significant premiums.

---

## License

This project is for educational purposes as part of the Kaggle House Prices competition.
