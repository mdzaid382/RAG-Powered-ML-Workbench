from sklearn.linear_model import (
    LogisticRegression,
    LinearRegression,
    Ridge,
    Lasso
)

from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor

from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor
)

from sklearn.svm import (
    SVC,
    SVR
)

from sklearn.neighbors import (
    KNeighborsClassifier,
    KNeighborsRegressor
)

from sklearn.naive_bayes import GaussianNB

from xgboost import (
    XGBClassifier,
    XGBRegressor
)




class ModelFactory:

    @staticmethod
    def classification_models():

        return {

            "Logistic Regression": LogisticRegression(
                max_iter=1000,
                random_state=42
            ),

            "Decision Tree": DecisionTreeClassifier(
                random_state=42
            ),

            "Random Forest": RandomForestClassifier(
                random_state=42
            ),

            "KNN": KNeighborsClassifier(),

            "SVM": SVC(),

            "Naive Bayes": GaussianNB(),

            "XGBoost": XGBClassifier(
                eval_metric="logloss",
                random_state=42
            )

        }

    @staticmethod
    def regression_models():

        return {

            "Linear Regression": LinearRegression(),

            "Ridge": Ridge(),

            "Lasso": Lasso(),

            "Decision Tree": DecisionTreeRegressor(
                random_state=42
            ),

            "Random Forest": RandomForestRegressor(
                random_state=42
            ),

            "KNN": KNeighborsRegressor(),

            "SVR": SVR(),

            "XGBoost": XGBRegressor(
                random_state=42
            )

        }