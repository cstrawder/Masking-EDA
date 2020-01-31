# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 12:10:51 2019

@author: chelsea.strawder
"""

from sklearn import datasets, neighbors, linear_model

digits = datasets.load_digits()
X_digits = digits.data / digits.data.max()
y_digits = digits.target

n = len(X_digits)

X_train = X_digits[:int(.9 * n)]
y_train = y_digits[:int(.9 * n)]
X_test = X_digits[int(.9 * n):]
y_test = y_digits[int(.9 * n):]

knn = neighbors.KNeighborsClassifier()
logistic = linear_model.LogisticRegression(solver='lbfgs', max_iter=1000,
                                           multi_class='multinomial')

print('KNN score: %f' % knn.fit(X_train, y_train).score(X_test, y_test))
print('LogisticRegression score: %f'
      % logistic.fit(X_train, y_train).score(X_test, y_test))