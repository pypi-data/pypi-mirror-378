
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.outliers_influence import variance_inflation_factor

def plot_corr_matrix(df, target=None, figsize=(12, 12), cmap="coolwarm", annot=False):
    """
    Plots a correlation matrix heatmap for numeric columns in a dataframe.
    
    Parameters:
        df (pd.DataFrame): The dataframe to analyze.
        target (str, optional): Column name of target variable. Excluded from features, 
                                but included in correlation. Default is None.
        figsize (tuple): Size of the matplotlib figure. Default (12,12).
        cmap (str): Colormap for heatmap. Default 'coolwarm'.
        annot (bool): Whether to annotate correlation values. Default False.
    """
    # Get numeric columns
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    
    # Ensure target is at the end if provided
    if target and target in numeric_cols:
        numeric_cols.remove(target)
        numeric_cols = numeric_cols + [target]
    
    # Compute correlation matrix
    corr_matrix = df[numeric_cols].corr()
    
    # Plot heatmap
    plt.figure(figsize=figsize)
    sns.heatmap(corr_matrix, annot=annot, fmt=".2f", cmap=cmap)
    plt.title("Correlation Matrix of Numeric Features", fontsize=14)
    plt.show()



def correlation_filter(df, threshold=0.90):
    """
    Removes highly correlated features above a given threshold.

    Parameters:
        df (pd.DataFrame): DataFrame with numeric features.
        threshold (float): Correlation threshold. Default is 0.90.

    Returns:
        pd.DataFrame: Reduced dataframe with low multicollinearity.
        list: Dropped features.
    """
    corr_matrix = df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    
    print(f"[INFO] Correlation filter applied. Dropped {len(to_drop)} features (>|{threshold}|).")
    return df.drop(columns=to_drop), to_drop


def vif_filter(df, thresh=10.0):
    """
    Removes features with high Variance Inflation Factor (VIF).

    Parameters:
        df (pd.DataFrame): DataFrame with numeric features.
        thresh (float): VIF threshold above which variables are dropped. Default is 10.0.

    Returns:
        pd.DataFrame: Reduced dataframe after removing high-VIF features.
        list: Dropped features.
    """
    variables = list(df.columns)
    dropped = []

    while True:
        vif = pd.Series(
            [variance_inflation_factor(df[variables].values, i) 
             for i in range(len(variables))],
            index=variables
        )
        max_vif = vif.max()
        
        if max_vif > thresh:
            drop_var = vif.idxmax()
            print(f"[INFO] Dropping '{drop_var}' with VIF={max_vif:.2f}")
            variables.remove(drop_var)
            dropped.append(drop_var)
        else:
            break

    print(f"[INFO] VIF filter applied. Dropped {len(dropped)} features (VIF > {thresh}).")
    return df[variables], dropped

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from xgboost import XGBRegressor, XGBClassifier

def get_feature_importance(X, y, model_type="rf_regressor", n_estimators=100, random_state=33, 
                           top_n=None, plot=False):
    """
    Train a model (RandomForest or XGBoost, regressor/classifier) and return feature importances.
    
    Parameters:
        X (pd.DataFrame): Encoded feature matrix.
        y (pd.Series or np.array): Target values.
        model_type (str): Choose from:
                          - 'rf_regressor'
                          - 'rf_classifier'
                          - 'xgb_regressor'
                          - 'xgb_classifier'
        n_estimators (int): Number of trees. Default 100.
        random_state (int): Random seed. Default 33.
        top_n (int, optional): Return only top n features. Default None (all features).
        plot (bool): If True, plots a bar chart of feature importances.
    
    Returns:
        pd.Series: Feature importances sorted in descending order.
    """
    # Pick model based on choice
    if model_type == "rf_regressor":
        model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
    elif model_type == "rf_classifier":
        model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
    elif model_type == "xgb_regressor":
        model = XGBRegressor(n_estimators=n_estimators, random_state=random_state, verbosity=0)
    elif model_type == "xgb_classifier":
        model = XGBClassifier(n_estimators=n_estimators, random_state=random_state, use_label_encoder=False, eval_metric="logloss", verbosity=0)
    else:
        raise ValueError("Invalid model_type. Choose from 'rf_regressor', 'rf_classifier', 'xgb_regressor', 'xgb_classifier'.")

    # Fit the model
    model.fit(X, y)

    # Extract feature importances
    importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)

    if top_n:
        importances = importances.head(top_n)

    if plot:
        plt.figure(figsize=(10, 6))
        importances.plot(kind="bar")
        plt.title(f"Feature Importances ({model_type})")
        plt.ylabel("Importance")
        plt.show()

    return importances

from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor
import pandas as pd

def run_rfe(X, y, model_type="rf_classifier", n_features_to_select=10, n_estimators=100, random_state=33):
    """
    Perform Recursive Feature Elimination (RFE) with RandomForest or XGBoost (classifier or regressor).
    
    Parameters:
        X (pd.DataFrame): Encoded feature matrix.
        y (pd.Series or np.array): Target values.
        model_type (str): Choose from:
                          - 'rf_classifier'
                          - 'rf_regressor'
                          - 'xgb_classifier'
                          - 'xgb_regressor'
        n_features_to_select (int): Number of features to select.
        n_estimators (int): Number of trees for RF/XGB models. Default 100.
        random_state (int): Random seed. Default 33.
    
    Returns:
        list: Selected feature names.
        RFE: Fitted RFE object (contains ranking, support, etc.).
    """
    # Choose model
    if model_type == "rf_classifier":
        model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
    elif model_type == "rf_regressor":
        model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
    elif model_type == "xgb_classifier":
        model = XGBClassifier(n_estimators=n_estimators, random_state=random_state, 
                              use_label_encoder=False, eval_metric="logloss", verbosity=0)
    elif model_type == "xgb_regressor":
        model = XGBRegressor(n_estimators=n_estimators, random_state=random_state, verbosity=0)
    else:
        raise ValueError("Invalid model_type. Choose from 'rf_classifier', 'rf_regressor', 'xgb_classifier', 'xgb_regressor'.")
    
    # Run RFE
    rfe = RFE(estimator=model, n_features_to_select=n_features_to_select)
    rfe.fit(X, y)

    selected_features = X.columns[rfe.support_].tolist()
    
    print(f"[INFO] Model: {model_type} | Selected {len(selected_features)} features")
    print("Selected features:", selected_features)
    
    return selected_features, rfe

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

def cramers_v(x, y):
    """
    Calculate Cramér's V statistic for categorical-categorical association.

    Parameters:
    ----------
    x : array-like, pd.Series
        First categorical variable.
    y : array-like, pd.Series
        Second categorical variable.

    Returns:
    -------
    float
        Cramér's V value between 0 and 1, where:
        - 0 = no association
        - 1 = perfect association

    Notes:
    ------
    - Requires at least 2 unique values in each variable.
    """
    # Create contingency table
    confusion_matrix = pd.crosstab(x, y)
    
    if confusion_matrix.shape[0] < 2 or confusion_matrix.shape[1] < 2:
        raise ValueError("Both variables must have at least 2 unique categories.")
    
    # Chi-squared statistic
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape

    # Bias correction
    phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    rcorr = r - ((r - 1) ** 2) / (n - 1)
    kcorr = k - ((k - 1) ** 2) / (n - 1)

    return np.sqrt(phi2corr / min((kcorr - 1), (rcorr - 1)))
