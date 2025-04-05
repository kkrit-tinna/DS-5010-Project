import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score

class MMRPredictor:
    """
    Predicts the Manheim Market Report (MMR) value for vehicles based on their attributes.
    """
    
    def __init__(self, data, model_type='gradient_boosting'): # default to gradient boosting
        """
        Initialize the MMR predictor.
        
        Parameters:
        -----------
        data : pandas DataFrame
            DataFrame containing vehicle attributes and MMR values
        X : pandas DataFrame
            Feature matrix
        y : pandas Series
            Target variable (MMR values)
        model_type : str
            Type of model to use for prediction. Options: 'random_forest', 'gradient_boosting'
        model : object
            Model object (RandomForestRegressor or XGBRegressor)
        """
        self.df = data
        self.numerical_cols = ['condition', 'car_age', 'mileage']
        self.categorical_cols = ['brand', 'market_model', 'body_type', 'transmission', 'state', 'interior', 'color']
        self.mmr = 'mmr'
        self.rest = ['sellingprice', 'value_retention', 'price_status']
        self.encoder = None
        self.scaler = None
        self.model_type = model_type
        self.model = None
        
        # Initialize model based on type
        if model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42
            )
        elif model_type == 'gradient_boosting':
            self.model = XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}. Choose 'random_forest' or 'gradient_boosting'.")
    
    def select_features(self):
        """
        Select relevant features for modeling.
        """
        # Select relevant features for modeling
        self.df = self.df[self.numerical_cols + self.categorical_cols + [self.mmr]]

    def encode_categorical_features(self):
        """
        Encode categorical features using one-hot encoding and modify self.df in place.
        """
        self.encoder = LabelEncoder()
        # Fit the encoder on the categorical columns
        for col in self.categorical_cols:
            self.df[col] = self.encoder.fit_transform(self.df[col])
            if col not in self.df.columns:
                raise ValueError(f"Column {col} not found in DataFrame.")

    def normalize_features(self):
        """
        Normalize numerical features using StandardScaler.
        Ensure that categorical features are already encoded before normalization.
        """

        # Ensure categorical features are encoded
        if self.encoder is None:
            raise ValueError("Categorical features must be encoded before normalization. Call encode_categorical_features() first.")
        
        self.scaler = StandardScaler()
    
        # Fit and transform the numerical columns
        self.df[self.numerical_cols] = self.scaler.fit_transform(self.df[self.numerical_cols])
        self.df[self.categorical_cols] = self.scaler.fit_transform(self.df[self.categorical_cols])

    def generate_feature_correlation_matrix(self):
        """
        Generate a correlation matrix for the features and save it to a CSV file.
        
        Parameters:
        -----------
        df : pandas DataFrame
            Preprocessed vehicle data
            
        Returns:
        --------
        pandas DataFrame
            Correlation matrix of the features
        """
        if not os.path.exists('dataviz'):
            os.makedirs('dataviz')
        # Generate heatmap of correlation matrix
        corr_matrix = self.df.corr()
        plt.figure(figsize=(10, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
        plt.title("Correlation Matrix")
        plt.savefig('dataviz/correlation_matrix.png')
        plt.close()

    def preprocess_data(self):
        """
        Preprocess the data by selecting features, encoding categorical variables, and normalizing numerical features.
        
        Returns:
        --------
        pandas DataFrame
            Preprocessed DataFrame
        """
        self.select_features()
        self.encode_categorical_features()
        self.normalize_features()
        self.generate_feature_correlation_matrix()
        
        return self.df
    
    def split_data(self):
        """
        Split the data into training and testing sets.
        
        Parameters:
        -----------
        
        test_size : float
            Proportion of the data to be used for testing
        random_state : int
            Random seed for reproducibility
        """
        X = self.df.drop(columns='mmr')
        y = data['mmr']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test

    def train(self, X, y):
        """
        Train the MMR prediction model.
    
        Returns:
        --------
        self
        """
        self.model.fit(X, y)
        return self
    
    def predict(self, X):
        """
        Predict MMR values for new vehicles.
        
        Parameters:
        -----------
        X : pandas DataFrame
            Feature matrix for new vehicles
            
        Returns:
        --------
        numpy array
            Predicted MMR values
        """
        return self.model.predict(X)
    
    def evaluate(self, X, y):
        """
        Evaluate the performance of the MMR prediction model.
        
        Parameters:
        -----------
        X : pandas DataFrame
            Feature matrix
        y : pandas Series
            True MMR values
            
        Returns:
        --------
        dict
            Performance metrics (RMSE, R^2)
        """
        y_pred = self.model.predict(X)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        r2 = r2_score(y, y_pred)
        
        return {
            'rmse': rmse,
            'r2': r2
        }
    
    def optimize_hyperparameters(self, X, y, cv=5):
        """
        Optimize hyperparameters using grid search.
        
        Parameters:
        -----------
        X : pandas DataFrame
            Feature matrix
        y : pandas Series
            Target variable (MMR values)
        cv : int
            Number of cross-validation folds
            
        Returns:
        --------
        self
        """
        # Define hyperparameter grid based on model type
        if self.model_type == 'random_forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        elif self.model_type == 'gradient_boosting':
            param_grid = {
            'learning_rate': [0.01, 0.1, 0.3],
            'max_depth': [3,5,7],
            'n_estimators': [50, 100, 200],
            'subsample': [0.7, 1.0]
            }
        
        # Perform grid search
        grid_search = GridSearchCV(
            estimator=self.model,
            param_grid=param_grid,
            cv=cv,
            scoring='neg_root_mean_squared_error',
            n_jobs=-1
        )
        
        grid_search.fit(X, y)
        
        # Update model with best parameters
        self.model = grid_search.best_estimator_
        
    def train_evaluate_optimize(self):
        """
        Combines training, evaluation, hyperparameter optimization, and re-evaluation into one function.
        Outputs evaluation metrics and predicted MMR values.
        """
        # Split the data
        X_train, X_test, y_train, y_test = self.split_data()

        # Train the model
        self.train(X_train, y_train)

        # Evaluate the model
        initial_metrics = self.evaluate(X_test, y_test)
        print("Initial Evaluation Metrics:", initial_metrics)

        # Optimize hyperparameters
        self.optimize_hyperparameters(X_train, y_train)

        # Train the model again with optimized hyperparameters
        self.train(X_train, y_train)

        # Evaluate the model again
        optimized_metrics = self.evaluate(X_test, y_test)
        print("Optimized Evaluation Metrics:", optimized_metrics)

        # # Predict MMR values
        # y_pred = self.model.predict(X_test)
        # print("Predicted MMR values:", y_pred)

        # Generate feature importance plot
        self.generate_feature_importance(X_train)


    def generate_feature_importance(self, X):
        """
        Generate barplots for feature importance and save them to a folder.
        """
        # Check if model is trained
        if self.model is None:
            raise ValueError("Model is not trained. Please train the model before generating feature importance.")
        # Create directory for saving plots
        if not os.path.exists('dataviz'):
            os.makedirs('dataviz')

        # Get feature importance
        feature_importances = self.model.feature_importances_

        # Create a DataFrame for feature importance with feature names
        feature_importance_df = pd.DataFrame({
            'Feature': X.columns,
            'Importance': feature_importances
        })
        
        # Sort by importance
        feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
        
        # Feature importance represents the contribution of each feature 
        plt.figure(figsize=(10, 6))
        bars = plt.barh(feature_importance_df['Feature'][:15], feature_importance_df['Importance'][:15])
        plt.xlabel('Feature Importance')
        plt.ylabel('Feature')
        plt.title('Top 15 Feature Importances')
        plt.gca().invert_yaxis()

        # Annotate each bar with the percentage
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.005, bar.get_y() + bar.get_height() / 2, f'{width:.2%}', va='center')
        
        # Save the plot
        plt.savefig(f'dataviz/feature_importance_{self.model_type}.png')
        plt.close()



# Example usage
if __name__ == "__main__":
    # read data from CSV
    data = pd.read_csv('preprocessed_data.csv')

    # Initialize and train the model
    predictor = MMRPredictor(data, model_type='gradient_boosting')

    # Preprocess the data
    predictor.preprocess_data()

    # Call the combined function
    predictor.train_evaluate_optimize()

    print(predictor.model)



