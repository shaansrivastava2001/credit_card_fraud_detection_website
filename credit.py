import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn
import scipy
import seaborn as sns
from sklearn.metrics import classification_report,accuracy_score
from sklearn.ensemble import IsolationForest
from pylab import rcParams
import pickle
rcParams['figure.figsize']=14,8

df=pd.read_csv('creditcard.csv')

count_by_clss=df['Class'].value_counts().sort_values(ascending=False)
LABELS=['Normal','Fraud']
plt.bar(LABELS,count_by_clss)
plt.title("NORMAL VS FRAUD CASES")
plt.xlabel('Class NORMAL(0) AND Fraud(1)')
plt.ylabel('No of obesrvaion')
plt.show()
total_cases=count_by_clss[0]+count_by_clss[1]
print("Normal cases Percentage:{}".format(count_by_clss[0]/total_cases*100))
print("Fraud cases Percentage:{}".format(count_by_clss[1]/total_cases*100))

normal=df[df['Class']==0]
fraud=df[df['Class']==1]


bins=50
plt.subplot(2,1,1)
plt.hist(normal.Amount,bins=bins)
plt.xlabel('normal transaction amount')
plt.ylabel('no. of observations')
plt.xlim((0, 10000))
plt.subplot(2,1,2)
plt.hist(fraud.Amount,bins=bins)
plt.xlabel('fraud transaction amount')
plt.ylabel('No. Of Observations')
plt.xlim((0,3000))
plt.show()

data=df.sample(frac=0.5,random_state=1)

Fraud=data[data['Class']==1]
Valid=data[data['Class']==0]
print('Fraud Cases:{}'.format(len(Fraud)))
print('Valid Cases:{}'.format(len(Valid)))

corr_mat = data.corr()
corr_features = corr_mat.index
plt.figure(figsize=(20,20))
g=sns.heatmap(df[corr_features].corr(),annot=True,cmap="RdYlGn")

X=data.drop(columns=['Class'])
Y=data['Class']

outlier_fraction = len(Fraud)/float(len(Valid))
Classifier=IsolationForest(n_estimators=100, max_samples=len(X),contamination=outlier_fraction,random_state=np.random.RandomState(42), verbose=0)
Classifier.fit(X)
score_pred = Classifier.decision_function(X)
y_hat = Classifier.predict(X)
y_hat[y_hat==1]=0
y_hat[y_hat==-1]=1
errors=(y_hat!=Y).sum()
print("ISOLATION FOREST ERRORS:{}".format(errors))
print(classification_report(Y,y_hat))

with open('credicard_model','wb') as f:
  pickle.dump(Classifier,f)