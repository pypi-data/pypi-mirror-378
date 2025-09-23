import pandas as pd
import numpy as np
from scipy.stats import t
import os
from statsmodels.stats.contingency_tables import mcnemar
#from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple, Dict, Iterator

import joblib

from sklearn.model_selection import GridSearchCV,StratifiedKFold,KFold,RepeatedStratifiedKFold
import sys
from sklearn import tree, svm
import scipy as ss
import h2o
import statistics
from sklearn.metrics import balanced_accuracy_score
from h2o.estimators.kmeans import H2OKMeansEstimator
import optuna
import optuna.exceptions
import statistics
from sklearn.cluster import KMeans
from sklearn.model_selection import KFold,LeaveOneOut
from multiprocessing import Pool, cpu_count




class behaviourConstructor:
    def __init__(self,par,effect_var,parent_cause_vars,lags,simulator_types,
                 output_file,default_missing_value,dt_runs,eval_method,eval_method_model_selection,
                 svm_model,dt_model,num_processes,category=None,min_cluster=None,max_cluster=None,
                 discretize_step=None,corrected_min_value=None,folds=None,k=None,r=None):
        self.hyperparameter_tuned = False
        self.par=par
        self.parent_cause_vars=parent_cause_vars
        self.effect_var=effect_var
        self.features=self.parent_cause_vars+[self.effect_var]
        self.min_cluster=min_cluster
        self.default_missing_value=default_missing_value
        self.max_cluster=max_cluster
        self.lags=lags
        self.max_lag=max(self.lags)
        self.simulator_types=simulator_types
        self.discretize_step=discretize_step
        self.corrected_min_value=corrected_min_value
        self.folds=folds
        self.output_file=output_file
        self.binned_vars=None
        self.discretized_df=None
        self.category=category
        self.dt_runs=dt_runs
        self.evaluation_method=eval_method
        self.ml_svm_model =svm_model
        self.ml_dt_model=dt_model
        self.eval_method_model_selection=eval_method_model_selection
        self.eval_method=eval_method
        self.num_processes=num_processes
        self.data_par_no_summary=None
        self.data_par_summary=None
        self.simulators=pd.DataFrame()
        self.k=k
        self.r=r

        """NP=0
        OP=1
        UP=2
        UPB=3
        UPC=4"""
        for simulator in simulator_types:
            if simulator==0:
                for ml_model_var in [0, 1]:
                    self.simulators = pd.concat([self.simulators, pd.DataFrame({'simulator_type': simulator,
                                                                                'ml_model': ml_model_var,
                                                                                'lag': 0}, index=[0])],
                                                ignore_index=True)
            else:
             for lag in lags:
               for ml_model_var in [0,1]:
                    self.simulators = pd.concat([self.simulators, pd.DataFrame({'simulator_type': simulator,
                                                                                'ml_model':ml_model_var,
                                                          'lag': lag}, index=[0])], ignore_index=True)


    def process_numeric_features(self):
        binned_vars = {}
        discretized_df = {}
        for var in self.cause_vars:
            if self.features_type[self.features_type['feature'] == var]['type'].item() == 'numeric':

                if 3 in self.simulator_types:
                    # bin the numeric cause var
                    binned_df = pd.DataFrame()
                    binned_df[var] = self.df[var] / self.discretize_step
                    binned_df[var] = binned_df[var].astype(int)
                    # normalize the value of var from corrected_min_value to one and assign zero to missing values
                    corrected_min = binned_df[var].min() - self.corrected_min_value
                    binned_df[var] = (binned_df[var] - corrected_min) / (binned_df[var].max() - corrected_min)
                    binned_df[self.effect_var] = self.df[self.effect_var]
                    corrected_min = binned_df[self.effect_var].min() - self.corrected_min_value
                    binned_df[self.effect_var] = (binned_df[self.effect_var] - corrected_min) / (
                            binned_df[self.effect_var].max() - corrected_min)

                    self.binned_vars[var] = binned_df[[var, self.effect_var]]
                if 4 in self.simulator_types:
                    ##### discretize the numeric cause var
                    disc_df = self.discretize_real_valued_by_clustering(var)
                    disc_df.reset_index(inplace=True, drop=True)
                    self.discretized_df[var] = disc_df[[var, self.effect_var]]
                    self.create_summary_col_names()

        # normalize the effect var
        if self.features_type[self.features_type['feature'] == self.effect_var]['type'] == 'numeric':
            corrected_min = self.df[self.effect_var].min() - self.corrected_min_value
            self.df[self.effect_var] = (self.df[self.effect_var] - corrected_min) / (
                    self.df[self.effect_var].max() - corrected_min)

        # normalize the cause vars for the OP model
        for var in self.cause_vars:
            if self.features_type[self.features_type['feature'] == var]['type'].item() == 'numeric':
                corrected_min = self.df[var].min() - self.corrected_min_value
                self.df[var] = (self.df[var] - corrected_min) / (self.df[var].max() - corrected_min)


    def extract_category_rows(self,temp_var,cat_var):
            temp_df = temp_var.copy()
            for index,feature_cat in cat_var.iterrows():
                    temp_df = temp_df[temp_df[feature_cat['feature']]== feature_cat['value']]
                    #print('feature_cat',feature_cat,index)
                    #print(temp_df.columns.to_list())
                    temp_df.drop(feature_cat['feature'],axis=1,inplace=True)
            return temp_df

    def build_data_with_no_summary(self,summary_lag):
        df_temp_new = self.data_window_no_summary_max_lag.copy()
        for order in range(summary_lag + 1, self.max_lag + 1):
            for feature in self.cause_vars+[self.effect_var]:
                df_temp_new.drop([feature + "_lag" + str(order)], axis=1, inplace=True)
        df_temp_new.reset_index(inplace=True, drop=True)
        return df_temp_new

    def create_summary_general(self, summary_lag, binned_df_var=None, discretized_df_var=None):
        summary_var = []

        effect_var_vals = sorted(self.feature_values[self.feature_values['var'] == self.effect_var]['values'].tolist())
        temp_df = pd.DataFrame()
        for cause_var in self.cause_vars:
            if (self.features_type[self.features_type['var'] == cause_var]['type'].values[0] == 'categorical'):
                cause_var_vals = sorted(self.feature_type[self.feature_type['var'] == cause_var]['values'].tolist())
                for cause_var_val in cause_var_vals:
                    if (self.effect_type == 'categorical'):
                        for effect_var_val in effect_var_vals:
                            temp_df['condition'] = np.where(((self.df[cause_var] == cause_var_val) & (
                                    self.df[self.effect_var] == effect_var_val)), 1, np.nan)
                            summary_list = temp_df['condition'].rolling(summary_lag, min_periods=1).sum().to_list()
                            summary_var.append(summary_list[(summary_lag):])
                    else:
                        if (self.effect_type == 'numeric'):
                            temp_df['condition'] = np.where(self.df[cause_var] == cause_var_val, self.df[self.effect_var], np.nan)
                            summary_list = temp_df['condition'].rolling(summary_lag, min_periods=1).mean().to_list()
                            summary_var.append(summary_list[(summary_lag):])
            else:
                if (self.effect_type == 'categorical'):
                    effect_var_vals = sorted(self.feature_type[self.feature_type['var'] == self.effect_var]['values'].tolist())
                    for effect_var_val in effect_var_vals:
                        temp_df['condition'] = np.where(self.df[self.effect_var] == effect_var_val, self.df[self.cause_var], np.nan)
                        summary_list = temp_df['condition'].rolling(summary_lag, min_periods=1).mean().to_list()
                        summary_var.append(summary_list[(summary_lag):])
                else:
                    if binned_df_var != None:
                        temp_data = binned_df_var[cause_var]
                        cause_var_vals = sorted(
                            self.feature_values[self.feature_values['var'] == cause_var]['values'].tolist())
                        for cause_var_val in cause_var_vals:
                            temp_df['condition'] = np.where(temp_data[cause_var] == cause_var_val,
                                                            temp_data[self.effect_var],
                                                            np.nan)
                            summary_list = temp_df['condition'].rolling(summary_lag, min_periods=1).mean().to_list()
                            summary_var.append(summary_list[(summary_lag):])
                    else:
                        if discretized_df_var != None:

                            temp_data = discretized_df_var[cause_var]
                            cause_var_vals = sorted(discretized_df_var[cause_var][cause_var].unique().tolist())
                            for cause_var_val in cause_var_vals:
                                temp_df['condition'] = np.where(temp_data[cause_var] == cause_var_val,
                                                                temp_data[self.effect_var], np.nan)
                                summary_list = temp_df['condition'].rolling(summary_lag, min_periods=1).mean().to_list()
                                summary_var.append(summary_list[(summary_lag):])

        summary_var = pd.DataFrame(np.vstack(summary_var))
        summary_var = summary_var.fillna(self.default_missing_var)
        summary_var = summary_var.transpose()
        return summary_var

    def objective(self,trial,x_train_var, y_train_var, folds, kernel_var,svm_model,effect_type):
        # C = trial.suggest_float('C', 1e-1, 1e3)
        # epsilon = trial.suggest_float('epsilon', 0, 1e-4)

        # gamma = trial.suggest_float('gamma', 1e-3, 1e1)
        C = trial.suggest_categorical('C', [0.1, 1, 10, 100])
        # epsilon = trial.suggest_categorical('epsilon', [0, 0.1, 0.01, 0.001, 0.0001])
        gamma = trial.suggest_categorical('gamma', [1, 0.1, 0.01, 0.001, 0.0001])
        # kernel = trial.suggest_categorical('kernel', ['poly', 'rbf'])

        # For 'poly' kernel, add degree as a tunable parameter
        if kernel_var == 'poly':
            degree = trial.suggest_int('degree', 2, 5)
        else:
            degree = 3  # Default value for other kernels

        # K-Fold Cross-Validation
        kf = self.eval_method_model_selection#KFold(n_splits=folds)
        fold_eval = []
        pred_list=[]
        true_label_list=[]
        for fold, (train_idx, valid_idx) in enumerate(kf.split(x_train_var, y_train_var)):
            # Split data into train and validation sets
            X_train, X_valid = x_train_var.iloc[train_idx].values, x_train_var.iloc[valid_idx].values
            y_train, y_valid = y_train_var.iloc[train_idx].values, y_train_var.iloc[valid_idx].values

            # Train model
            model = svm_model(C=C, kernel=kernel_var, gamma=gamma)
            model.fit(X_train, y_train)

            # Validate model
            preds = model.predict(X_valid)
            pred_list.append(preds[0])
            true_label_list.append(y_valid[0])
        true_label_list = [item for sub in true_label_list for item in sub]
        pred_list = [item for sub in pred_list for item in sub]
        if self.effect_type == 'numeric':
            eval_score = -np.abs(np.subtract(true_label_list, pred_list)).mean()
        else:
            eval_score = balanced_accuracy_score(true_label_list, pred_list)


        # Report intermediate result to Optuna
        #trial.report(sum(fold_eval) / len(fold_eval), fold + 1)
        #trial.report(eval_score)

        """# Check if trial should be pruned
        if trial.should_prune():
            raise optuna.exceptions.TrialPruned()"""

        # Return the average accuracy across all folds
        #return sum(fold_eval) / len(fold_eval)
        return eval_score

    def select_model_parallelized(self,params_var:pd.DataFrame()):

        summary_type_var = params_var[0]
        ml_model_type = params_var[1]
        lag_var = params_var[2]

        evaluation_lag = pd.DataFrame()
        features = []
        eval_score_list=[]
        best_params = []

        if summary_type_var == '0':
            # NP
            x_train_var = self.df.iloc[self.max_lag:][self.cause_vars]
            y_train_var = self.df.iloc[self.max_lag:][self.effect_var]
            features = self.cause_vars
        elif summary_type_var == 1:  # OP
            self.data_par_no_summary = self.build_data_with_no_summary(summary_lag=lag_var)
            features = self.data_par_no_summary.columns.tolist()
            features.remove(self.effect_var)
            x_train_var = self.data_par_no_summary[features]
            y_train_var = self.data_par_no_summary[self.effect_var]
        elif summary_type_var == 3:  # UPB

            summary = self.create_summary_general( lag_var,binned_df_var=self.binned_vars,discretized_df_var=None)
            summary.reset_index(inplace=True, drop=True)
            summary.columns = self.summ_cols_var
            data_par_summary = self.df.iloc[self.max_lag:]
            data_par_summary.reset_index(inplace=True, drop=True)
            summary = summary.iloc[(self.max_lag - lag_var):]
            summary.reset_index(drop=True, inplace=True)
            data_par_cols = self.df.columns.tolist()
            data_par_summary = pd.concat([data_par_summary, summary], ignore_index=True, axis=1)
            data_par_summary.columns = data_par_cols + self.summ_cols_var
            data_par_summary.reset_index(inplace=True, drop=True)
            features = self.cause_vars + self.summ_cols_var
            x_train_var = data_par_summary[features]
            y_train_var = data_par_summary[self.effect_var]
        elif summary_type_var == 4:  # UPC

            summary = self.create_summary_general(lag_var, binned_df_var=None,
                                             discretized_df_var=self.discretized_df)
            summary.reset_index(inplace=True, drop=True)
            summary.columns = self.summ_disc_cols_var
            data_par_summary = self.df.iloc[self.max_lag:]
            data_par_summary.reset_index(inplace=True, drop=True)
            summary = summary.iloc[(self.max_lag - lag_var):]
            summary.reset_index(drop=True, inplace=True)
            data_par_cols = self.df.columns.tolist()
            data_par_summary = pd.concat([data_par_summary, summary], ignore_index=True, axis=1)
            data_par_summary.columns = data_par_cols + self.summ_disc_cols_var
            data_par_summary.reset_index(inplace=True, drop=True)
            features = self.cause_vars + self.summ_disc_cols_var
            x_train_var = data_par_summary[features]
            y_train_var = data_par_summary[self.effect_var]
        else:
            summary = self.create_summary_general(lag_var, binned_df_var=None,
                                                  discretized_df_var=None)
            summary.reset_index(inplace=True, drop=True)
            summary.columns = self.summ_cols_var
            data_par_summary = self.df.iloc[self.max_lag:]
            data_par_summary.reset_index(inplace=True, drop=True)
            summary = summary.iloc[(self.max_lag - lag_var):]
            summary.reset_index(drop=True, inplace=True)
            data_par_cols = self.df.columns.tolist()
            data_par_summary = pd.concat([data_par_summary, summary], ignore_index=True, axis=1)
            data_par_summary.columns = data_par_cols + self.summ_cols_var
            data_par_summary.reset_index(inplace=True, drop=True)
            features = self.cause_vars + self.summ_cols_var
            x_train_var = data_par_summary[features]
            y_train_var = data_par_summary[self.effect_var]


        if not (self.category is None):
                category_row=self.extract_category_rows(pd.concat([x_train_var,y_train_var],axis=1),self.category)
                features=list(set(features)-set(self.category['feature'].unique()))
                x_train_var=category_row[features]
                y_train_var=category_row[self.effect_var]


        if ml_model_type == 1:  # svm
            best_params_df = pd.DataFrame()
            runs=1
            for kernel in ['rbf']:
                # Run the optimization
                pruner = optuna.pruners.MedianPruner()
                sampler = optuna.samplers.TPESampler()
                study = optuna.create_study(sampler=sampler, direction='maximize', pruner=pruner)
                study.optimize(lambda trial: self.objective(trial, x_train_var, y_train_var,
                                                            self.folds, kernel,self.ml_svm_model,self.effect_type), n_trials=10,
                               n_jobs=self.num_processes)
                best_params = study.best_trial.params

                best_params_df = pd.concat([best_params_df, pd.DataFrame({'kerenl': kernel,
                                                                          'score': study.best_trial.value
                                                                             , 'best_params': [best_params]},
                                                                         index=[0])], ignore_index=True)
                # print(best_params_df)
            best_params = best_params_df.iloc[best_params_df['score'].argmax()]['best_params']


            ml_model_var = self.ml_svm_model(
                C=best_params['C'],
                # epsilon=best_params['epsilon'],
                kernel=kernel,
                gamma=best_params['gamma']
            )
            ml_model_var.fit(x_train_var, y_train_var)
            y_pred = ml_model_var.predict(x_train_var)
            if self.effect_type == 'numeric':
                eval_score = -np.abs(np.subtract(y_train_var, y_pred)).mean()
            else:
                eval_score = balanced_accuracy_score(y_train_var, y_pred)

        elif ml_model_type == 0:
            runs = self.dt_runs
            # print(summary_type_var,lag_var,len(features))
            #model_local = tree.DecisionTreeRegressor(max_depth=len(features), min_samples_leaf=20)
            ml_model_var= self.ml_dt_model(max_depth=len(features), min_samples_leaf=20)
            best_params = {'max_depth':len(features),'min_samples_leaf':20}
            kf = self.eval_method_model_selection  # KFold(n_splits=folds)
            X=pd.concat([x_train_var,y_train_var],axis=1)
            X.reset_index(inplace=True,drop=True)
            eval_score = 0
            counter=0
            pred_list=[]
            true_label_list=[]
            for i, (train_index, test_index) in enumerate(kf.split(x_train_var,y_train_var)):
                training_data_x = X.iloc[train_index][features].copy()
                training_data_y = X.iloc[train_index][self.effect_var].copy()
                for run in range(runs):
                    counter+=1
                    ml_model_var = ml_model_var.fit(training_data_x.values, training_data_y.values)
                    # Predict the response for test dataset
                    y_pred = ml_model_var.predict(X.iloc[test_index][features].values)
                    pred_list.append(y_pred)
                    true_label_list.append(X.iloc[test_index][self.effect_var].values)
            if self.effect_type == 'numeric':
                eval_score = -np.abs(np.subtract(true_label_list, pred_list)).mean()
            else:
                eval_score = balanced_accuracy_score(true_label_list, pred_list)


        evaluation_lag = pd.concat([evaluation_lag, pd.DataFrame(
            {'lag': lag_var, 'score': eval_score, 'simulator_type': summary_type_var,'model':ml_model_type, 'ml_model': ml_model_var, 'params': [best_params]
             ,'runs':runs}, index=[0])],
                            ignore_index=True, axis=0)
        return evaluation_lag


    def select_model_parallelized_grid_search(self,params_var:pd.DataFrame()):

        summary_type_var = params_var[0]
        ml_model_type = params_var[1]
        lag_var = params_var[2]
        #print(summary_type_var,ml_model_type,lag_var)

        evaluation_lag = pd.DataFrame()
        features = []
        eval_score_list=[]
        best_params = []

        if summary_type_var == 0:
            # NP
            x_train_var = self.df.iloc[self.max_lag:][self.cause_vars]
            y_train_var = self.df.iloc[self.max_lag:][self.effect_var]
            features = self.cause_vars
        elif summary_type_var == 1:  # OP
            self.data_par_no_summary = self.build_data_with_no_summary(summary_lag=lag_var)
            features = self.data_par_no_summary.columns.tolist()
            features.remove(self.effect_var)
            x_train_var = self.data_par_no_summary[features]
            y_train_var = self.data_par_no_summary[self.effect_var]
        elif summary_type_var == 3:  # UPB

            summary = self.create_summary_general( lag_var,binned_df_var=self.binned_vars,discretized_df_var=None)
            summary.reset_index(inplace=True, drop=True)
            summary.columns = self.summ_cols_var
            data_par_summary = self.df.iloc[self.max_lag:]
            data_par_summary.reset_index(inplace=True, drop=True)
            summary = summary.iloc[(self.max_lag - lag_var):]
            summary.reset_index(drop=True, inplace=True)
            data_par_cols = self.df.columns.tolist()
            data_par_summary = pd.concat([data_par_summary, summary], ignore_index=True, axis=1)
            data_par_summary.columns = data_par_cols + self.summ_cols_var
            data_par_summary.reset_index(inplace=True, drop=True)
            features = self.cause_vars + self.summ_cols_var
            x_train_var = data_par_summary[features]
            y_train_var = data_par_summary[self.effect_var]
        elif summary_type_var == 4:  # UPC

            summary = self.create_summary_general(lag_var, binned_df_var=None,
                                             discretized_df_var=self.discretized_df)
            summary.reset_index(inplace=True, drop=True)
            summary.columns = self.summ_disc_cols_var
            data_par_summary = self.df.iloc[self.max_lag:]
            data_par_summary.reset_index(inplace=True, drop=True)
            summary = summary.iloc[(self.max_lag - lag_var):]
            summary.reset_index(drop=True, inplace=True)
            data_par_cols = self.df.columns.tolist()
            data_par_summary = pd.concat([data_par_summary, summary], ignore_index=True, axis=1)
            data_par_summary.columns = data_par_cols + self.summ_disc_cols_var
            data_par_summary.reset_index(inplace=True, drop=True)
            features = self.cause_vars + self.summ_disc_cols_var
            x_train_var = data_par_summary[features]
            y_train_var = data_par_summary[self.effect_var]
        else:
            summary = self.create_summary_general(lag_var, binned_df_var=None,
                                                  discretized_df_var=None)
            summary.reset_index(inplace=True, drop=True)
            summary.columns = self.summ_cols_var
            data_par_summary = self.df.iloc[self.max_lag:]
            data_par_summary.reset_index(inplace=True, drop=True)
            summary = summary.iloc[(self.max_lag - lag_var):]
            summary.reset_index(drop=True, inplace=True)
            data_par_cols = self.df.columns.tolist()
            data_par_summary = pd.concat([data_par_summary, summary], ignore_index=True, axis=1)
            data_par_summary.columns = data_par_cols + self.summ_cols_var
            data_par_summary.reset_index(inplace=True, drop=True)
            features = self.cause_vars + self.summ_cols_var
            x_train_var = data_par_summary[features]
            y_train_var = data_par_summary[self.effect_var]


        if not (self.category is None):
                category_row=self.extract_category_rows(pd.concat([x_train_var,y_train_var],axis=1),self.category)
                features=list(set(features)-set(self.category['feature'].unique()))

                x_train_var=category_row[features]
                y_train_var=category_row[self.effect_var]


        if ml_model_type == 1:  # svm
            best_params_df = pd.DataFrame()
            runs=1
            for kernel in ['rbf']:

                param_grid = {'C': [0.1, 1, 10, 100, 1000],
                              'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
                               'degree': [3],
                              'kernel': ['rbf']}

                grid = GridSearchCV(self.ml_svm_model(), param_grid, refit=True, verbose=0, scoring='balanced_accuracy',
                                    cv=self.eval_method_model_selection)
                #print('was here')
                # fitting the model for grid search
                grid.fit(x_train_var.to_numpy(), y_train_var.to_numpy())
                preds = grid.predict(x_train_var.to_numpy())
                best_params = grid.best_params_


            best_params = best_params

            ml_model_var = self.ml_svm_model(
                C=best_params['C'],
                # epsilon=best_params['epsilon'],
                kernel=kernel,
                gamma=best_params['gamma']
            )
            ml_model_var.fit(x_train_var, y_train_var)
            y_pred = ml_model_var.predict(x_train_var)
            if self.effect_type == 'numeric':
                eval_score = -np.abs(np.subtract(y_train_var, y_pred)).mean()
            else:
                eval_score = balanced_accuracy_score(y_train_var, y_pred)

        elif ml_model_type == 0:
            runs = self.dt_runs
            # print(summary_type_var,lag_var,len(features))
            #model_local = tree.DecisionTreeRegressor(max_depth=len(features), min_samples_leaf=20)
            ml_model_var= self.ml_dt_model(max_depth=len(features), min_samples_leaf=20)
            best_params = {'max_depth':len(features),'min_samples_leaf':20}
            kf = self.eval_method_model_selection  # KFold(n_splits=folds)
            X=pd.concat([x_train_var,y_train_var],axis=1)
            X.reset_index(inplace=True,drop=True)
            eval_score = 0
            counter=0
            pred_list=[]
            true_label_list=[]
            for i, (train_index, test_index) in enumerate(kf.split(x_train_var,y_train_var)):
                training_data_x = X.iloc[train_index][features].copy()
                training_data_y = X.iloc[train_index][self.effect_var].copy()
                for run in range(runs):
                    counter+=1
                    ml_model_var = ml_model_var.fit(training_data_x.values, training_data_y.values)
                    # Predict the response for test dataset
                    y_pred = ml_model_var.predict(X.iloc[test_index][features].values)
                    pred_list.append(y_pred)
                    true_label_list.append(X.iloc[test_index][self.effect_var].values)
            true_label_list=[item for sub in true_label_list for item in sub]
            pred_list=[item for sub in pred_list for item in sub]
            if self.effect_type == 'numeric':
                eval_score = -np.abs(np.subtract(true_label_list, pred_list)).mean()
            else:
                eval_score = balanced_accuracy_score(true_label_list, pred_list)


        evaluation_lag = pd.concat([evaluation_lag, pd.DataFrame(
            {'lag': lag_var, 'score': eval_score, 'simulator_type': summary_type_var,'model':ml_model_type, 'ml_model': ml_model_var, 'params': [best_params]
             ,'runs':runs}, index=[0])],
                            ignore_index=True, axis=0)
        return evaluation_lag



    def hyperparameter_tuning(self):
        evaluation_lag = pd.DataFrame()
        with Pool(processes=self.num_processes) as pool:
            evaluation_lag_process = pool.starmap_async(self.select_model_parallelized_grid_search,[
                ([params]) for params in self.simulators.to_numpy()])
            for list in evaluation_lag_process.get():
                evaluation_lag = pd.concat([evaluation_lag, list], ignore_index=True)

        evaluation_lag = evaluation_lag.sort_values(['lag'], ascending=False).sort_values(['simulator_type'], ascending=True).sort_values(by=['model'],
                                                                                      ascending=False).sort_values(['score'], ascending=True)
        evaluation_lag.reset_index(inplace=True, drop=True)

        evaluation_lag.to_excel(self.output_file+self.effect_var+"_par_" + str(
            self.par) + "_select_model_results.xlsx",
                       index=False)

        return evaluation_lag.iloc[-1] #evaluation_lag.iloc[evaluation_lag['score'].argmax()]

    def generate_behavioural_pattern(self,df):

        self.df = df
        self.split_temp=self.dump_rskf_splits()
        self.sort_features()
        #check if any of the cause variables is numeric
        if self.features_type[self.features_type['feature'].isin(self.parent_cause_vars)]['type'].isin(['numeric']).any():
            self.process_numeric_features()
        self.create_summary_col_names()
        if(1 in self.simulator_types):
          self.data_window_no_summary_max_lag = self.build_data_with_no_summary_complete()



        if not self.hyperparameter_tuned:
            self.hyperparameter_tuned=True
            self.best_ml_model = self.hyperparameter_tuning()

        eval_score_df = pd.DataFrame()
        eval_score_lag = pd.DataFrame()
        total_eval_score=0
        with Pool(processes=self.num_processes) as pool:
            eval_score_lag_item = pool.starmap(self.generate_simulator, [
                (self.eval_method,self.best_ml_model['runs'],self.folds,self.best_ml_model['ml_model'],
                 self.binned_vars,self.discretized_df, params) for
                params in
                self.simulators[['simulator_type','lag']].drop_duplicates().to_numpy()])
        for l in eval_score_lag_item:
            eval_score_lag = pd.concat([eval_score_lag, l], ignore_index=True)

        self.best_fit_simulator = eval_score_lag.iloc[eval_score_lag['eval_score'].argmax()]
        total_eval_score = total_eval_score + self.best_fit_simulator ['eval_score']
        gc_on_window = pd.DataFrame()

        with Pool(processes=self.num_processes) as pool:
            gc_on_window_item = pool.starmap(self.GC_on_window_parallized, [
                (self.eval_method,self.best_ml_model['ml_model'],cause_var) for cause_var in self.parent_cause_vars
            ])


        for l in gc_on_window_item:
            gc_on_window = pd.concat([gc_on_window, l], ignore_index=True)
        return gc_on_window,eval_score_lag,self.best_fit_simulator['eval_score'],self.best_ml_model

    def sort_features(self):
        features_type = pd.DataFrame()
        columns=self.df.columns.tolist()
        features = self.df.columns.tolist()
        bool_features = [feature for feature in self.df.columns
                        if pd.DataFrame(self.df[feature].unique()).isin([0, 1]).all().values]
        if len(bool_features) != 0:
            features_type = pd.concat([features_type, pd.DataFrame(
                {'feature': bool_features, 'type': ['categorical'] * len(bool_features)}
            )], axis=0, ignore_index=True)
        cat_features = self.df.select_dtypes(include=['object']).columns.tolist()
        numeric_features= list(set(features) - set(cat_features)- set(bool_features))
        features_type = pd.concat([features_type, pd.DataFrame(
            {'feature': numeric_features, 'type': ['numeric'] * len(numeric_features)}
        )], axis=0, ignore_index=True)
        cat_features = list(set(cat_features) - set(bool_features))
        if self.effect_var in cat_features:
            cat_features.remove(self.effect_var)
            features_type = pd.concat([features_type, pd.DataFrame(
                {'feature': self.effect_var, 'type': ['categorical']}
            )], axis=0, ignore_index=True)


        for cat_feature in cat_features:
            cause_cat_types = pd.DataFrame()
            data_par_dummies = pd.get_dummies(self.df[cat_feature], drop_first=True, prefix=cat_feature)
            data_par_dummies = data_par_dummies.replace({True: 1, False: 0})
            columns_dummies = data_par_dummies.columns.tolist()
            columns.remove(cat_feature)
            columns = columns + columns_dummies
            self.df.drop([cat_feature], axis=1, inplace=True)
            self.df = pd.concat([self.df, data_par_dummies], axis=1, ignore_index=True)
            cause_cat_types['feature'] = columns_dummies
            cause_cat_types['type'] = ['categorical'] * len(columns_dummies)
            features_type = pd.concat([features_type, cause_cat_types], axis=0, ignore_index=True)


        self.df.columns = columns
        self.features_type=features_type
        #if self.effect_var in cat_features:
        #    self.effect_type='categorical'
        #else:
        self.effect_type=self.features_type[self.features_type['feature']==self.effect_var]['type'].values[0]
        self.cause_vars=list(self.df.columns)
        self.cause_vars.remove(self.effect_var)

    def create_summary_col_names(self):
        summ_cols_var = []
        summ_disc_cols_var = []
        if self.features_type[self.features_type['feature']==self.effect_var]['type'].values[0] == 'categorical':
            effect_var_vals = sorted(self.df[self.effect_var].unique())
        else:
            effect_var_vals = ['avg']
        feature_values = pd.DataFrame({'var': self.effect_var, 'values': effect_var_vals})
        feature_disc_values = pd.DataFrame({'var': self.effect_var, 'values': effect_var_vals})

        for cause_var in self.cause_vars:
            if self.features_type[self.features_type['feature'] == cause_var]['type'].values[0] == 'categorical':
                cause_var_vals = sorted(self.df[cause_var].unique())
                feature_values = pd.concat([feature_values, pd.DataFrame({'var': cause_var, 'values': cause_var_vals})],
                                           axis=0, ignore_index=True)
                feature_disc_values = pd.concat([feature_disc_values, pd.DataFrame({'var': cause_var, 'values': cause_var_vals})],
                                           axis=0, ignore_index=True)
                for cause_var_val in cause_var_vals:
                    for effect_var_val in effect_var_vals:
                        summ_cols_var.append(
                            cause_var + "_" + str(cause_var_val) + "_" + self.effect_var + "_" + str(effect_var_val))
                        summ_disc_cols_var.append(
                            cause_var + "_" + str(cause_var_val) + "_" + self.effect_var + "_" + str(effect_var_val))
            else:
                binned_temp = self.binned_vars[cause_var]
                cause_var_vals = sorted(binned_temp[cause_var].unique())
                feature_values = pd.concat([feature_values, pd.DataFrame({'var': cause_var, 'values': cause_var_vals})],
                                           axis=0, ignore_index=True)
                for cause_var_val in cause_var_vals:
                    for effect_var_val in effect_var_vals:
                        summ_cols_var.append(
                            cause_var + "_" + str(cause_var_val) + "_" + self.effect_var + "_" + str(effect_var_val))

                discretized_temp = self.discretized_df[cause_var]
                cause_var_vals = sorted(binned_temp[cause_var].unique())
                feature_disc_values = pd.concat([feature_disc_values, pd.DataFrame({'var': cause_var, 'values': cause_var_vals})],
                                           axis=0, ignore_index=True)
                for cause_var_val in cause_var_vals:
                    for effect_var_val in effect_var_vals:
                        summ_disc_cols_var.append(
                            cause_var + "_" + str(cause_var_val) + "_" + self.effect_var + "_" + str(effect_var_val))

        self.summ_cols_var=summ_cols_var
        self.feature_values=feature_values
        self.summ_disc_cols_var=summ_disc_cols_var
        self.feature_disc_values_values=feature_disc_values

    def create_summary_general(self, summary_lag, binned_df_var=None, discretized_df_var=None):
        summary_var = []
        effect_var_vals = sorted(self.feature_values[self.feature_values['var'] == self.effect_var]['values'].tolist())
        summary_list = []
        temp_df = pd.DataFrame()
        for cause_var in self.cause_vars:
            if (self.features_type[self.features_type['feature'] == cause_var]['type'].values[0] == 'categorical'):
                cause_var_vals = sorted(self.feature_values[self.feature_values['var'] == cause_var]['values'].tolist())
                for cause_var_val in cause_var_vals:
                    if (self.effect_type == 'categorical'):
                        for effect_var_val in effect_var_vals:
                            temp_df['condition'] = np.where(((self.df[cause_var] == cause_var_val) & (
                                    self.df[self.effect_var] == effect_var_val)), 1, np.nan)
                            summary_list = temp_df['condition'].rolling(summary_lag, min_periods=1).sum().to_list()
                            summary_var.append(summary_list[(summary_lag-1):-1])
                    else:
                        if (self.effect_type == 'numeric'):
                            temp_df['condition'] = np.where(self.df[cause_var] == cause_var_val, self.df[self.effect_var], np.nan)
                            summary_list = temp_df['condition'].rolling(summary_lag, min_periods=1).mean().to_list()
                            summary_var.append(summary_list[(summary_lag-1):-1])
            else:
                if (self.effect_type== 'categorical'):
                    temp_df['condition'] = np.where(self.df[self.effect_var] == effect_var_val, self.df[cause_var], np.nan)
                    summary_list = temp_df['condition'].rolling(summary_lag, min_periods=1).mean().to_list()
                    summary_var.append(summary_list[(summary_lag-1):-1])
                else:
                    if binned_df_var != None:
                        temp_data = binned_df_var[cause_var]
                        cause_var_vals = sorted(
                            self.feature_values[self.feature_values['var'] == cause_var]['values'].tolist())
                        for cause_var_val in cause_var_vals:
                            temp_df['condition'] = np.where(temp_data[cause_var] == cause_var_val,
                                                            temp_data[self.effect_var],
                                                            np.nan)
                            summary_list = temp_df['condition'].rolling(summary_lag, min_periods=1).mean().to_list()
                            summary_var.append(summary_list[(summary_lag-1):-1])
                    else:
                        if discretized_df_var != None:

                            temp_data = discretized_df_var[cause_var]
                            cause_var_vals = sorted(discretized_df_var[cause_var][cause_var].unique().tolist())
                            for cause_var_val in cause_var_vals:
                                temp_df['condition'] = np.where(temp_data[cause_var] == cause_var_val,
                                                                temp_data[self.effect_var], np.nan)
                                summary_list = temp_df['condition'].rolling(summary_lag, min_periods=1).mean().to_list()
                                summary_var.append(summary_list[(summary_lag-1):-1])
        summary_var = pd.DataFrame(np.vstack(summary_var))
        summary_var = summary_var.fillna(self.default_missing_value)
        summary_var = summary_var.transpose()
        return summary_var

    def calculate_inertia(self,n_clusters, data):
        """Calculate inertia for a given number of clusters."""
        # print('caluculate interia')
        # kmeans = KMeans(n_clusters=n_clusters, n_init=10, max_iter=300,)

        # kmeans.fit(data)
        h2o.init()
        data_h2o = h2o.H2OFrame(data)
        kmeans = H2OKMeansEstimator(k=n_clusters, max_iterations=10)
        kmeans.train(training_frame=data_h2o)
        return n_clusters, kmeans.tot_withinss()

    def calculate_distance(self,point, p1, p2):
        """Calculate the perpendicular distance of a point from a line defined by p1 and p2."""
        # print('calculate distance')
        line_vector = p2 - p1
        line_vector_norm = line_vector / np.linalg.norm(line_vector)
        vector_to_line = point - p1
        projection = np.dot(vector_to_line, line_vector_norm) * line_vector_norm
        distance = np.linalg.norm(vector_to_line - projection)
        return distance

    def detect_elbow_point(self,inertia_dict, num_processes=None):
        """
        Detect the elbow point in the inertia curve using multiprocessing.

        Parameters:
            inertia_dict (dict): A dictionary with cluster numbers as keys and inertia values as values.
            num_processes (int, optional): Number of processes to use. Defaults to CPU count.

        Returns:
            int: The optimal number of clusters detected by the elbow method.
        """
        # print('detect elbow')
        cluster_numbers = np.array(list(inertia_dict.keys()))
        inertia_values = np.array(list(inertia_dict.values()))

        # Compute the line connecting the first and last points
        p1 = np.array([cluster_numbers[0], inertia_values[0]])
        p2 = np.array([cluster_numbers[-1], inertia_values[-1]])

        points = np.array([[cluster_numbers[i], inertia_values[i]] for i in range(len(cluster_numbers))])


        with Pool(processes=self.num_processes) as pool:
            distances = pool.starmap_async(self.calculate_distance, [(point, p1, p2) for point in points])

        # The elbow point is the cluster number with the maximum distance
        optimal_cluster_index = np.argmax(distances.get())
        return cluster_numbers[optimal_cluster_index]

    def find_optimal_clusters(self,data, cluster_range, num_processes=None):
        """
        Find the optimal number of clusters using the Elbow method with multiprocessing.

        Parameters:
            data (array-like): Input data for clustering.
            cluster_range (range): Range of cluster numbers to evaluate.
            num_processes (int, optional): Number of processes to use. Defaults to CPU count.

        Returns:
            dict: A dictionary with cluster numbers as keys and inertia values as values.
        """
        # print('find optimal ')
        with Pool(processes=self.num_processes) as pool:
            results = pool.starmap(self.calculate_inertia, [(k, data) for k in cluster_range])

        return dict(results)

    def discretize_real_valued_by_clustering(self,cause_var):
        # Range of clusters to evaluate
        cluster_range = range(self.min_cluster, self.max_cluster)
        # Determine optimal clusters
        inertia_dict = self.find_optimal_clusters(self.df[[cause_var, self.effect_var]], cluster_range)
        optimal_clusters = self.detect_elbow_point(inertia_dict)

        model = KMeans(n_clusters=optimal_clusters
                       , n_init=10)
        model.fit(self.df[[cause_var, self.effect_var]])
        ids_list = model.predict(self.df[[cause_var, self.effect_var]])
        prototypes = pd.DataFrame()
        prototypes['id'] = ids_list
        prototypes[cause_var] = self.df[cause_var]
        prototypes[self.effect_var] = self.df[self.effect_var]

        discretized_df = pd.DataFrame()
        for id, row in prototypes.iterrows():
            discretized_df = pd.concat([discretized_df, pd.DataFrame({'id': int(row['id'])
                                                                         ,
                                                                      cause_var: prototypes.groupby('id').mean().iloc[
                                                                          int(row['id'])][cause_var]
                                                                         ,
                                                                      self.effect_var: prototypes.groupby('id').mean().iloc[
                                                                          int(row['id'])][self.effect_var]}, index=[0])])

        return discretized_df

    def build_data_with_no_summary_complete(self):
        df_temp = self.df.copy()
        for order in range(1, self.max_lag + 1):
            for feature in self.df.columns:
                df_temp[feature + "_lag" + str(order)] = df_temp[feature].shift(order)
        df_temp = df_temp.iloc[self.max_lag:]
        df_temp.reset_index(inplace=True, drop=True)
        return df_temp

    def generate_simulator(self,evaluation_method_var,runs_var,folds_var,ml_model_var, binned_df_var,
                           discretized_df_var, simulator_var):

        simulator_type_var = simulator_var[0]
        lag_var = simulator_var[1]

        if simulator_type_var == 0:
            eval_score_lag_var = self.performance_no_memeory(ml_model_var,runs_var)
        elif simulator_type_var == 1:
            eval_score_lag_var = self.compare_no_summary_on_window(ml_model_var,runs_var,lag_var)
        elif simulator_type_var == 3:#'UPB'
            eval_score_lag_var = self.compare_summary_on_window(ml_model_var,runs_var,lag_var,binned_df_var, None)
        elif simulator_type_var == 4:#'UPC'
            eval_score_lag_var = self.compare_summary_on_window(ml_model_var,runs_var,lag_var,None, discretized_df_var)
        else:#'UP'
            eval_score_lag_var = self.compare_summary_on_window(ml_model_var,runs_var,lag_var,None,None)
        return eval_score_lag_var

    def compare_summary_on_window(self,ml_model_var,runs_var,lag_var, binned_df_var,
                                  discretized_df_var):
        eval_score_lag = pd.DataFrame()
        eval_score_list = []

        if self.effect_type=='numeric':
            if discretized_df_var!=None:
                summary_type = 4 #'UPC'
                summary = self.create_summary_general(lag_var, None,discretized_df_var)

            else:
                summary_type = 3
                summary = self.create_summary_general(lag_var,binned_df_var,None)

        else:
            summary_type = 2
            summary = self.create_summary_general(lag_var, None,None)

        summary.reset_index(inplace=True, drop=True)
        summary.columns = self.summ_cols_var
        data_par_summary = self.df.iloc[self.max_lag:]
        data_par_summary.reset_index(inplace=True, drop=True)
        summary = summary.iloc[(self.max_lag - lag_var):]
        summary.reset_index(drop=True, inplace=True)
        data_par_cols = self.df.columns.tolist()
        data_par_summary = pd.concat([data_par_summary, summary], ignore_index=True, axis=1)
        data_par_summary.columns = data_par_cols + self.summ_cols_var
        data_par_summary.reset_index(inplace=True, drop=True)

        X = data_par_summary
        if not (self.category is None):
            X = self.extract_category_rows(X, self.category)

        kf = self.eval_method#KFold(n_splits=folds)
        target = self.effect_var
        features = self.cause_vars + self.summ_cols_var
        if not (self.category is None):
         features=list(set(features)-set(self.category['feature'].unique()))
        eval_score = 0
        counter=0
        pred_list=[]
        true_label_list=[]
        #for i, (train_index, test_index) in enumerate(kf.split(X=X[features],y=X[target])):
        splits = self.load_rskf_splits("splits.pkl")
        eval_score_list=[]
        for train_index, test_index in ((s["train"], s["test"]) for s in splits):
            training_data_x = X.iloc[train_index][features].copy()
            training_data_y = X.iloc[train_index][target].copy()
            for run in range(runs_var):
                    counter += 1
                    #print('inside',X.iloc[train_index][target].nunique())
                    ml_model_var = ml_model_var.fit(training_data_x.values, training_data_y.values)
                    # Predict the response for test dataset
                    y_pred = ml_model_var.predict(X.iloc[test_index][features].values)
                    pred_list.append(y_pred)
                    true_label_list.append(X.iloc[test_index][self.effect_var].values)
                    if self.effect_type == 'numeric':
                        eval_score_list.append(-np.abs(np.subtract(X.iloc[test_index][self.effect_var].values, y_pred)).mean())
                    else:
                        eval_score_list.append(balanced_accuracy_score(X.iloc[test_index][self.effect_var].values, y_pred))

        true_label_list = [item for sub in true_label_list for item in sub]
        pred_list = [item for sub in pred_list for item in sub]
        if self.effect_type == 'numeric':
                eval_score = -np.abs(np.subtract(true_label_list, pred_list)).mean()
        else:
                eval_score = balanced_accuracy_score(true_label_list, pred_list)

        eval_score_lag = pd.concat([eval_score_lag,
                             pd.DataFrame({'lag': lag_var, 'eval_score': eval_score, 'simulator_type': summary_type, 'eval_score_list': [eval_score_list]},
                                          index=[0])], ignore_index=True, axis=0)
        # print('out of summary')
        return eval_score_lag

    def compare_no_summary_on_window(self,ml_model_var,runs_var,lag_var):
        eval_score_lag = pd.DataFrame()
        eval_score_list = []

        # prepare data
        data_par_no_summary = self.build_data_with_no_summary( summary_lag=lag_var)
        data_par_no_summary.reset_index(inplace=True, drop=True)
        X = data_par_no_summary
        if not (self.category is None):
            X = self.extract_category_rows(X, self.category)


        kf = self.eval_method#KFold(n_splits=folds)
        target = self.effect_var
        features = data_par_no_summary.columns.tolist()
        if not (self.category is None):
         features=list(set(features)-set(self.category['feature'].unique()))
        features.remove(self.effect_var)
        eval_score = 0
        counter=0
        pred_list=[]
        true_label_list=[]
        #for i, (train_index, test_index) in enumerate(kf.split(X=X[features],y=X[self.effect_var])):
        splits = self.load_rskf_splits("splits.pkl")
        for train_index, test_index in ((s["train"], s["test"]) for s in splits):
            training_data_x = X.iloc[train_index][features].copy()
            training_data_y = X.iloc[train_index][target].copy()
            for run in range(runs_var):
                    counter+=1
                    ml_model_var = ml_model_var.fit(training_data_x.values, training_data_y.values)
                    # Predict the response for test dataset
                    y_pred = ml_model_var.predict(X.iloc[test_index][features].values)
                    pred_list.append(y_pred)
                    true_label_list.append(X.iloc[test_index][self.effect_var].values)
                    if self.effect_type == 'numeric':
                        eval_score_list.append(-np.abs(np.subtract(X.iloc[test_index][self.effect_var].values, y_pred)).mean())
                    else:
                        eval_score_list.append(balanced_accuracy_score(X.iloc[test_index][self.effect_var].values, y_pred))

        true_label_list = [item for sub in true_label_list for item in sub]
        pred_list = [item for sub in pred_list for item in sub]
        if self.effect_type == 'numeric':
                eval_score = -np.abs(np.subtract(true_label_list, pred_list)).mean()
        else:
                #print(true_label_list)
                #print(pred_list)
                eval_score = balanced_accuracy_score(true_label_list, pred_list)

        eval_score_lag = pd.concat(
            [eval_score_lag, pd.DataFrame({'lag': lag_var, 'eval_score': eval_score, 'simulator_type': 1, 'eval_score_list': [eval_score_list]}, index=[0])],
            ignore_index=True, axis=0)
        return eval_score_lag

    def performance_no_memeory(self,ml_model_var,runs_var):
        X = self.df.iloc[self.max_lag:]
        X.reset_index(drop=True, inplace=True)
        if not (self.category is None):
            X = self.extract_category_rows(X, self.category)


        kf = self.eval_method#KFold(n_splits=folds)
        target = self.effect_var
        features = self.cause_vars
        if not (self.category is None):
         features=list(set(features)-set(self.category['feature'].unique()))
        eval_score = 0
        eval_score_list = []
        counter=0
        pred_list=[]
        true_label_list=[]
        #for i, (train_index, test_index) in enumerate(kf.split(X=X[features], y=X[target])):
        splits=self.load_rskf_splits("splits.pkl")
        for train_index, test_index in ((s["train"], s["test"]) for s in splits):
            training_data_x = X.iloc[train_index][features].copy()
            training_data_y = X.iloc[train_index][target].copy()
            for run in range(runs_var):
                    counter+=1
                    ml_model_var = ml_model_var.fit(training_data_x.values, training_data_y.values)
                    # Predict the response for test dataset
                    y_pred = ml_model_var.predict(X.iloc[test_index][features].values)
                    pred_list.append(y_pred)
                    true_label_list.append(X.iloc[test_index][self.effect_var].values)
                    if self.effect_type == 'numeric':
                        eval_score_list.append(-np.abs(np.subtract(X.iloc[test_index][self.effect_var].values, y_pred)).mean())
                    else:
                        eval_score_list.append(balanced_accuracy_score(X.iloc[test_index][self.effect_var].values, y_pred))

        true_label_list = [item for sub in true_label_list for item in sub]
        pred_list = [item for sub in pred_list for item in sub]
        if self.effect_type == 'numeric':
                eval_score = -np.abs(np.subtract(true_label_list, pred_list)).mean()
        else:
                eval_score = balanced_accuracy_score(true_label_list, pred_list)

        # print('out of no memory')
        return pd.DataFrame({'simulator_type': 0, 'lag': 0, 'eval_score': eval_score, 'eval_score_list': [eval_score_list]}, index=[0])


    def GC_on_window_parallized(self,evaluation_method_var,ml_model_var,cause_var):
        #print(cause_var)
        gc_lag_list = pd.DataFrame()
        summary_type = self.best_fit_simulator['simulator_type']
        best_fit_lag_var = self.best_fit_simulator['lag']
        unrestricted_measure = self.best_fit_simulator['eval_score']
        unrestricted_eval_score_list = self.best_fit_simulator['eval_score_list']
        eval_score_list = []
        if self.best_fit_simulator['simulator_type']==0:
            X = self.df.iloc[self.max_lag:]
            X.reset_index(drop=True, inplace=True)
            features = self.cause_vars

        elif self.best_fit_simulator['simulator_type']==1:
            # prepare data
            data_par_no_summary = self.build_data_with_no_summary(int(self.best_fit_simulator['lag']))
            data_par_no_summary.reset_index(inplace=True, drop=True)
            features = data_par_no_summary.columns.tolist()
            features.remove(self.effect_var)
            X = data_par_no_summary

        elif self.best_fit_simulator['simulator_type']==2:
            summary = self.create_summary_general(int(self.best_fit_simulator['lag']), None, None)
            # summary = pd.DataFrame(np.vstack(summary))
            summary.reset_index(inplace=True, drop=True)
            summary.columns = self.summ_cols_var
            data_par_summary = self.df.iloc[self.max_lag:]
            data_par_summary.reset_index(inplace=True, drop=True)
            summary = summary.iloc[(self.max_lag - int(self.best_fit_simulator['lag'])):]
            summary.reset_index(drop=True, inplace=True)
            data_par_cols = self.df.columns.tolist()
            data_par_summary = pd.concat([data_par_summary, summary], ignore_index=True, axis=1)
            data_par_summary.columns = data_par_cols + self.summ_cols_var
            data_par_summary.reset_index(inplace=True, drop=True)
            features = self.cause_vars + self.summ_cols_var
            X = data_par_summary

        elif self.best_fit_simulator['simulator_type']==4:
            summary = self.create_summary_general(int(self.best_fit_simulator['lag']),
                                             None, self.discretized_df)
            # summary = pd.DataFrame(np.vstack(summary))
            summary.reset_index(inplace=True, drop=True)
            summary.columns = self.summ_disc_cols_var
            data_par_summary = self.df.iloc[self.max_lag:]
            data_par_summary.reset_index(inplace=True, drop=True)
            summary = summary.iloc[(self.max_lag - best_fit_lag_var):]
            summary.reset_index(drop=True, inplace=True)
            data_par_cols = self.df.columns.tolist()
            data_par_summary = pd.concat([data_par_summary, summary], ignore_index=True, axis=1)
            data_par_summary.columns = data_par_cols + self.summ_disc_cols_var
            data_par_summary.reset_index(inplace=True, drop=True)
            features = self.cause_vars + self.summ_disc_cols_var
            X = data_par_summary

        elif summary_type==3:
            summary = self.create_summary_general(int(self.best_fit_simulator['lag']), self.binned_vars, None)
            # summary = pd.DataFrame(np.vstack(summary))
            summary.reset_index(inplace=True, drop=True)
            summary.columns = self.summ_cols_var
            data_par_summary = self.df.iloc[self.max_lag:]
            data_par_summary.reset_index(inplace=True, drop=True)
            summary = summary.iloc[(self.max_lag - int(self.best_fit_simulator['lag'])):]
            summary.reset_index(drop=True, inplace=True)
            data_par_cols = self.df.columns.tolist()
            data_par_summary = pd.concat([data_par_summary, summary], ignore_index=True, axis=1)
            data_par_summary.columns = data_par_cols + self.summ_cols_var
            data_par_summary.reset_index(inplace=True, drop=True)
            features = self.cause_vars + self.summ_cols_var
            X = data_par_summary

        eval_score_list = []
        kf =evaluation_method_var
        target = self.effect_var
        features = [x for x in features if cause_var not in x]  # remove the cause
        if not (self.category is None):
            X = self.extract_category_rows(X, self.category)
            features = list(set(features) - set(self.category['feature'].unique()))

        eval_score = 0
        counter=0
        pred_list=[]
        true_label_list=[]
        #for i, (train_index, test_index) in enumerate(kf.split(X=X[features],y=X[target])):
        splits = self.load_rskf_splits("splits.pkl")
        for train_index, test_index in ((s["train"], s["test"]) for s in splits):
            training_data_x = X.iloc[train_index][features].copy()
            training_data_y = X.iloc[train_index][target].copy()
            for run in range(self.best_ml_model['runs']):
                    counter+=1
                    # model = tree.DecisionTreeClassifier(max_depth=len(features))
                    ml_model_var = ml_model_var.fit(training_data_x.values, training_data_y.values)
                    # Predict the response for test dataset
                    y_pred = ml_model_var.predict(X.iloc[test_index][features].values)
                    pred_list.append(y_pred)
                    true_label_list.append(X.iloc[test_index][self.effect_var].values)
                    if self.effect_type == 'numeric':
                        eval_score_list.append(-np.abs(np.subtract(X.iloc[test_index][self.effect_var].values, y_pred)).mean())
                    else:
                        eval_score_list.append(balanced_accuracy_score(X.iloc[test_index][self.effect_var].values, y_pred))

        true_label_list = [item for sub in true_label_list for item in sub]
        pred_list = [item for sub in pred_list for item in sub]
        if self.effect_type == 'numeric':
                eval_score = -np.abs(np.subtract(true_label_list, pred_list)).mean()
        else:
                eval_score = balanced_accuracy_score(true_label_list, pred_list)


        gc = unrestricted_measure-eval_score
        if self.effect_type=='numeric':
            _, alpha = ss.stats.ttest_ind_from_stats(statistics.mean(unrestricted_eval_score_list),
                                                     statistics.stdev(unrestricted_eval_score_list),
                                                     len(unrestricted_eval_score_list),
                                                     statistics.mean(eval_score_list), statistics.stdev(eval_score_list),
                                                     len(eval_score_list), alternative='two-sided')
            if alpha >= 0.05:
                gc = 0
        else:
            #d = unrestricted_measure - eval_score_list
            d=np.array([a - b for a, b in zip(unrestricted_eval_score_list, eval_score_list)])
            kr = len(d)  # total CV evaluations
            n_test = len(test_index)  # size of *one* test fold
            n_train = len(train_index)  # size of *one* train fold
            df = kr - 1
            var_d = d.var(ddof=1)
            std_corr = np.sqrt(var_d * (1 / kr + n_test / n_train))
            #print('mran',d.mean())
            #print('corr',std_corr)
            if std_corr==0:
                if d.mean()==0:
                    gc=0
            else:
                t_corr = d.mean() / std_corr
                p_corr = t.sf(t_corr, df)
                if p_corr>=0.05:
                    gc=0

        gc_lag_list = pd.concat([gc_lag_list, pd.DataFrame(
            {'cause_var': cause_var, 'effect_var': self.effect_var, 'GC': gc
                }, index=[0])],
                                ignore_index=True, axis=0)

        return gc_lag_list

    def dump_rskf_splits(self):
        rskf = self.eval_method
        splits= []
        temp_df_split=self.df[self.max_lag:].copy()
        temp_df_split.reset_index(inplace=True,drop=True)
        for i, (train_idx, test_idx) in enumerate(rskf.split(temp_df_split[self.parent_cause_vars], temp_df_split[self.effect_var])):
            splits.append(
                {
                    "repeat": i // self.k,
                    "fold":   i %  self.k,
                    "train":  np.asarray(train_idx, dtype=np.int32),
                    "test":   np.asarray(test_idx,  dtype=np.int32),
                }
            )

        joblib.dump(splits, Path('splits.pkl'))          # one-liner persistence
        return splits

    def load_rskf_splits(self, path: str ):
        split_list= joblib.load(Path(path))
        return split_list

