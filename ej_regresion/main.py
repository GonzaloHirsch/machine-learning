import argparse
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from constants import Headers, x_headers_list
import matplotlib.gridspec as gridspec
from sklearn.model_selection import train_test_split

def print_entire_df (df):
    pd.set_option('display.max_rows', df.shape[0]+1)
    print(df)

def read_data(file):
    df = pd.read_csv(file, sep=' ')
    return df

def split_train_test_dataset(X, y, seed):
    # 70% train, 30% test, 100 -> seed for shuffling
    return train_test_split(X, y, test_size = 0.3, random_state = seed)

def split_df_all_attributes(df, seed):
    x = df[x_headers_list]
    y = df[Headers.WEIGHT.value]
    x_train, x_test, y_train, y_test = split_train_test_dataset(x, y, seed)
    return x_train, x_test, y_train, y_test

def split_df_filtered_attributes(df, attributes, seed):
    x = df[attributes]
    y = df[Headers.WEIGHT.value]
    x_train, x_test, y_train, y_test = split_train_test_dataset(x, y, seed)
    return x_train, x_test, y_train, y_test

def run_regression(x_train, y_train):
    # Convert X and Y to matrix and array
    matrix = []
    for n in range(len(x_train)):
        matrix.append([1])
        for p in range(len(x_train.columns)):
            matrix[-1].append(x_train.iloc[n][p])
    X = np.matrix(np.array(matrix))
    Y = []
    for i in range(len(y_train)):
        Y.append([y_train.iloc[i]])
    Y = np.array(Y)

    # Calculate betas
    Xt = X.T
    try:
        B = (Xt * X).I * Xt * Y
    except:
        return None, None
    return B, X

def predict(input, B):
    Yi = B[0,0]
    for j in range(len(input)):
        Yi += B[j+1, 0] * input[j]
    return Yi

def test(x_test, y_test, B):
    n = len(x_test)
    p = len(x_test.iloc[0])
    q = len(B)

    meanY = 0
    for i in range(n):
        meanY += y_test.iloc[i]
    meanY = meanY / n

    RSS = 0
    TSS = 0
    for i in range(n):
        actual = predict(x_test.iloc[i], B)
        expected = y_test.iloc[i]
        diff = abs(actual-expected)
        RSS += diff**2
        TSS += (actual-meanY)**2
    sigma2 = RSS/(n-p-1)

    R2 = 1 - RSS/TSS
    R2adj = 1 - (1-R2)*(n-1)/(n-q)

    F = ((TSS - RSS)/p) / (RSS/(n-p-1))
    return RSS, TSS, sigma2, R2, R2adj, F

# Diapo 22
def get_standard_error(inputs, B, sigma2):
    n = len(inputs)
    SE2 = [0]
    for j in range(len(B)-1):
        meanX = 0
        for i in range(n):
            meanX += inputs.iloc[i,j]
        meanX = meanX / n
        square_sum = 0
        for i in range(n):
            square_sum += (inputs.iloc[i,j]-meanX)**2
        SE2.append(sigma2/square_sum)
    return SE2

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Machine Learning Regression Exercise")
    # Add arguments
    parser.add_argument('-f', dest='file', required=True)
    args = parser.parse_args()
    df = read_data(args.file)
    seed = random.randint(1, 9999)

    # EJERCICIO 2
    print("== EJERCICIO 2 -- MATRICES ==")
    x_train, x_test, y_train, y_test = split_df_all_attributes(df, seed)
    B, X = run_regression(x_train, y_train)
    RSS, TSS, sigma2, R2, R2adj, F = test(x_test, y_test, B)
    varB = sigma2 * (X.T*X).I
    print("RSS =", RSS)
    print("sigma2 =", sigma2)
    print("R2 =", R2)
    print("R2 adj =", R2adj)
    print("F =", F)
    get_standard_error(x_train, B, sigma2)

    # EJERCICIO 3 (Forward Selection, usa solo RSS)
    print("\n== EJERCICIO 3 -- FORWARD SELECTION ==")
    p = len(x_headers_list)
    list_of_attributes = []
    best_attributes = []
    best_attributes_global = []
    min_RSS_global = 99999999
    for amount_of_attributes in range(p):
        min_RSS = 99999999
        for attr in x_headers_list:
            current_attributes = list_of_attributes.copy()
            current_attributes.append(attr)
            x_train, x_test, y_train, y_test = split_df_filtered_attributes(df, current_attributes, seed)
            B, X = run_regression(x_train, y_train)
            if B is not None:
                RSS, TSS, sigma2, R2, R2adj, F = test(x_test, y_test, B)
                if RSS < min_RSS:
                    min_RSS = RSS
                    best_attributes = current_attributes.copy()
        list_of_attributes = best_attributes.copy()
        print(amount_of_attributes+1, "attributes -> RSS =", min_RSS)
        if min_RSS < min_RSS_global:
            best_attributes_global = best_attributes.copy()
            min_RSS_global = min_RSS
    print("\nRSS = ", min_RSS_global, " using", len(best_attributes_global),"attributes:")
    print(best_attributes_global)



if __name__ == '__main__':
    main()
