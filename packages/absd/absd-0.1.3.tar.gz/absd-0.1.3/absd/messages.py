def a1():
    code = '''import tensorflow as tf
x=tf.constant([1,2,3,4,5,6],shape=[2,3])
print(x)
y=tf.constant([7,8,9,10,11,12],shape=[3,2])
print(y)
z=tf.matmul(x,y)
print("Product:",z)
e_matrix_A=tf.random.uniform([2,2],minval=3,maxval=10,dtype=tf.float32,name="matrixA")
print("Matrix A:\n{}\n\n".format(e_matrix_A))
eigen_values_A,eigen_vectors_A=tf.linalg.eigh(e_matrix_A)
print("Eigen Vectors:\n{}\n\nEigen Values:\n{}\n\n".format(eigen_vectors_A,eigen_values_A))'''
    print(code)

def a2():
    code = '''import numpy as np
from keras.layers import Dense
from keras.models import Sequential
model = Sequential()
model.add(Dense(units=2, activation='tanh', input_dim=2))
model.add(Dense(units=1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())
print(model.get_weights())
X=np.array([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
Y=np.array([0.,1.,1.,0.])
model.fit(X, Y, epochs=100,batch_size=4)
print(model.get_weights())
print(model.predict(X,batch_size=4))'''
    print(code)

def a3():
    code = '''from keras.models import Sequential
from keras.layers import Dense
from sklearn.datasets import make_blobs
from sklearn.preprocessing import MinMaxScaler
import numpy as np

X,Y=make_blobs(n_samples=100,centers=2,n_features=2,random_state=1)
scalar=MinMaxScaler()
scalar.fit(X)
X=scalar.transform(X)
model=Sequential()
model.add(Dense(4,input_dim=2,activation='relu'))
model.add(Dense(4,activation='relu'))
model.add(Dense(1,activation='sigmoid'))
model.compile(loss='binary_crossentropy',optimizer='adam')
model.fit(X,Y,epochs=500)
Xnew,Yreal=make_blobs(n_samples=3,centers=2,n_features=2,random_state=1)
Xnew=scalar.transform(Xnew)
Ynew_probs = model.predict(Xnew)
Ynew = (Ynew_probs > 0.5).astype(int)
for i in range(len(Xnew)):
 print("X=%s,Predicted=%s,Desired=%s"%(Xnew[i],Ynew[i],Yreal[i]))
print(model.summary())'''
    print(code)

def a4():
    code = '''from keras.models import Sequential
from keras.layers import Dense
from sklearn.datasets import make_regression
from sklearn.preprocessing import MinMaxScaler

X,Y=make_regression(n_samples=100,n_features=2,noise=0.1,random_state=1)
scalarX, scalarY=MinMaxScaler(),MinMaxScaler()
scalarX.fit(X)
scalarY.fit(Y.reshape(100,1))
X=scalarX.transform(X)
Y=scalarY.transform(Y.reshape(100,1))
model=Sequential()
model.add(Dense(4,input_dim=2,activation='relu'))
model.add(Dense(4,activation='relu'))
model.add(Dense(1,activation='sigmoid'))
model.compile(loss='mse',optimizer='adam')
model.fit(X,Y,epochs=1000,verbose=0)
Xnew,a=make_regression(n_samples=3,n_features=2,noise=0.1,random_state=1)
Xnew=scalarX.transform(Xnew)
Ynew = model.predict(Xnew)
for i in range(len(Xnew)):
  print("X=%s,Predicted=%s,Desired=%s"%(Xnew[i],Ynew[i],a[i]))
  #print("X=%s,Predicted=%s"%(Xnew[i],Ynew[i]))'''
    print(code)

def a5():
    code = '''import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import LSTM,Dense,Dropout
from sklearn.preprocessing import MinMaxScaler

#1)Generate synthetic stock price data using a sine wave
np.random.seed(0)
time_steps=300
x=np.linspace(0,50,time_steps)
data=np.sin(x)+np.random.normal(scale=0.2,size=time_steps)  #Sine_wave+noise
data=data.reshape(-1,1)

#2)Scale the data
scaler=MinMaxScaler(feature_range=(0,1))
scaled_data=scaler.fit_transform(data)

#3)Create sequences of 60 time steps
X=[]
y=[]
sequence_length=60
for i in range(sequence_length,len(scaled_data)):
    X.append(scaled_data[i-sequence_length:i,0])
    y.append(scaled_data[i,0])


X,y=np.array(X),np.array(y)

#Reshape input to be [samples,time steps,features]
X=np.reshape(X,(X.shape[0],X.shape[1],1))

#4)Build the LSTM model
model=Sequential()
model.add(LSTM(units=50,return_sequences=True,input_shape=(X.shape[1],1)))
model.add(Dropout(0.2))
model.add(LSTM(units=50,return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))
model.add(Dense(units=1))

#5)Compile and train the model
model.compile(optimizer='adam',loss='mean_squared_error')
model.fit(X,y,epochs=20,batch_size=32)

#6)Predict
predicted=model.predict(X)
predicted=scaler.inverse_transform(predicted.reshape(-1,1))
actual=scaler.inverse_transform(y.reshape(-1,1))

#7)Plot results
plt.figure(figsize=(12,6))
plt.plot(actual,color="red",label="Actual (Synthetic Stock Price)")
plt.plot(predicted,color="blue",label='Predicted Price')
plt.title('LSTM Stock Price Prediction (Synthetic Data)')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()'''
    print(code)

def a6():
    code = '''iimport numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

#1)Generate synthetic monthly umbrella sales data for 3 years(36 months)
np.random.seed()
months=pd.date_range(start="2020-01",periods=36,freq="M")

#Simulate sales with seasonality (rainy season in June,July,August)
seasonality=10+5*np.sin(2*np.pi*(months.month-1)/12)
noise=np.random.normal(0,1,len(months))
sales=seasonality+noise

#Create DataFrame
data=pd.DataFrame({"Date":months,"Umbrella_Sales":sales})
data.set_index("Date",inplace=True)

#2)Plot the sales data
plt.figure(figsize=(10,4))
plt.plot(data,label="Umbrella_Sales")
plt.title("Synthetic Monthly Umbrella Sales")
plt.xlabel("Date")
plt.ylabel("Sales")
plt.grid(True)
plt.legend()
plt.show()

#3)Fit ARIMA model (we'll use ARIMA(1,1,1) as a simple example)
model=ARIMA(data,order=(1,1,1))
model_fit=model.fit()

#4)Forecast the next 12 months
forecast_steps=12
forecast=model_fit.forecast(steps=forecast_steps)

#5)Plot the original and forecasted values
forecast_index=pd.date_range(start=data.index[-1]+pd.offsets.MonthEnd(1),periods=forecast_steps,freq="M")
forecast_series=pd.Series(forecast,index=forecast_index)

plt.figure(figsize=(12,6))
plt.plot(data,label="Historical Sales")
plt.plot(forecast_series,label="Forecasted Sales",color="orange")
plt.title(" Umbrella Sales Forecast (ARIMA Model)")
plt.xlabel("Date")
plt.ylabel("Sales")
plt.grid(True)
plt.legend()
plt.show()'''
    print(code)

def a7():
    code = '''import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Dense, Flatten
from tensorflow.keras.utils import to_categorical

(X_train, y_train), (X_test, y_test) = mnist.load_data()

X_train = X_train.reshape(-1, 28, 28, 1).astype('float32')/ 255.0
X_test = X_test.reshape(-1, 28, 28, 1).astype('float32')/ 255.0

y_train = to_categorical(y_train,10)
y_test = to_categorical(y_test,10)

model = Sequential([
    Conv2D(32, kernel_size=3 ,activation='relu', input_shape=(28,28,1)),
    Conv2D(64, kernel_size=3 ,activation='relu'),
    Flatten(),
    Dense(10, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=1,batch_size=128)

index = 0
sample_image = X_test[index]
sample_label = y_test[index]
prediction = model.predict(np.expand_dims(sample_image, axis=0))
predicted_class = np.argmax(prediction)
actual_class = np.argmax(y_test[index])

plt.figure(figsize=(3,3))
plt.imshow(sample_image.reshape(28,28), cmap='gray')
plt.title(f': {predicted_class}, Actual: {actual_class}')
plt.axis('off')
plt.show()'''
    print(code)

def a8():
    code = '''import keras
from keras.datasets import mnist
from keras import layers
import numpy as np
import matplotlib.pyplot as plt

(X_train, _), (X_test, _) = mnist.load_data()
X_train = X_train.astype('float32') / 255.
X_test = X_test.astype('float32') / 255.
X_train = X_train[..., np.newaxis]
X_test = X_test[..., np.newaxis]

noise_factor = 0.5
X_train_noisy = np.clip(X_train + noise_factor * np.random.normal(size=X_train.shape), 0., 1.)
X_test_noisy = np.clip(X_test + noise_factor * np.random.normal(size=X_test.shape), 0., 1.)

input_imp = keras.Input(shape=(28,28,1))
x = layers.Conv2D(32,3,activation='relu',padding='same')(input_imp)
x = layers.MaxPooling2D(2, padding='same')(x)
x = layers.Conv2D(32,3,activation='relu',padding='same')(x)
encoded = layers.MaxPooling2D(2, padding='same')(x)

x = layers.Conv2D(32,3,activation='relu',padding='same')(encoded)
x = layers.UpSampling2D(2)(x)
x = layers.Conv2D(32,3,activation='relu',padding='same')(x)
x = layers.UpSampling2D(2)(x)
decoded = layers.Conv2D(1,3,activation='sigmoid',padding='same')(x)

autoencoder = keras.Model(input_imp,decoded)
autoencoder.compile(optimizer='adam',loss='binary_crossentropy', metrics=['accuracy'])
autoencoder.fit(X_train_noisy,X_train,epochs=1,batch_size=128,shuffle=True,validation_data=(X_test_noisy,X_test))

plt.figure(figsize=(20, 2))
for i in range(10):
  ax = plt.subplot(1,10,i+1)
  plt.imshow(X_test_noisy[i].squeeze(),cmap='gray')
  ax.axis('off')
plt.show()

predictions = autoencoder.predict(X_test_noisy)
plt.figure(figsize=(20, 2))
for i in range(10):
  ax = plt.subplot(1,10,i+1)
  plt.imshow(predictions[i].squeeze(),cmap='gray')
  ax.axis('off')
plt.show()'''
    print(code)

def b1():
    code = '''import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
df=pd.read_csv("")
df.head()
sns.scatterplot(x="cgpa",y="ML",data=df)
kmeans=KMeans(n_clusters=4,random_state=0,n_init=10)
kmeans.fit(df)
centroid=kmeans.cluster_centers_
label=kmeans.labels_
sns.scatterplot(x="cgpa",y="ML",data=df,hue=label)
sns.scatterplot(x="cgpa",y="ML",data=df,hue=label,palette='coolwarm',s=50)'''
    print(code)

def b2():
    code = '''from scipy.cluster import hierarchy as SCH 
from sklearn.cluster import AgglomerativeClustering 
import matplotlib.pyplot as plt 
import pandas as pd
df = pd.read_csv(r"")
df.columns = ['CustomerID', 'Gender', 'Age', 'annual_income', 'spending_score']
df = df[['annual_income', 'spending_score']]
plt.figure(figsize =(6, 6))
plt.title('Visualising the data') 
Dendrogram = SCH.dendrogram((SCH.linkage (df, method ='ward')))
ac2 = AgglomerativeClustering(n_clusters = 5) # Visualizing the clustering 
plt.figure(figsize =(6, 6)) 
plt.scatter(df['annual_income'], df['spending_score'], c = ac2.fit_predict(df)) 
plt.show()'''
    print(code)

def b3():
    code = '''print([i for i in range(10) if i % 2 == 0])'''
    print(code)

def b4():
    code = '''import numpy as np 
import matplotlib.pyplot as plt 
from sklearn.mixture import GaussianMixture 
from sklearn.datasets import make_blobs 
 
# Generate synthetic data 
X, y = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0) 
 
# Fit Gaussian Mixture Model 
gmm = GaussianMixture(n_components=4, random_state=42) 
gmm.fit(X) 
labels = gmm.predict(X) 
# Plot the results 
plt.figure(figsize=(10, 6))

# Plot the data points 
plt.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap='viridis', alpha=0.6) 

# Plot the Gaussian ellipses 
for i in range(gmm.n_components): 
    # Get eigenvalues and eigenvectors 
    covariances = gmm.covariances_[i][:2, :2] 
    v, w = np.linalg.eigh(covariances) 
    v = 2.0 * np.sqrt(2.0) * np.sqrt(v) 
     
    # Calculate ellipse angle 
    angle = np.arctan2(w[0][1], w[0][0]) 
    angle = 180.0 * angle / np.pi  # Convert to degrees 
     
    # Create ellipse 
    mean = gmm.means_[i, :2] 
    ell = plt.matplotlib.patches.Ellipse(mean, v[0], v[1], 180.0 + angle,color='red', alpha=0.3) 
    plt.gca().add_artist(ell) 
 
plt.title('Gaussian Mixture Model Clustering') 
plt.xlabel('Feature 1') 
plt.ylabel('Feature 2') 
plt.grid(True) 
plt.show() 
 
# Print model parameters 
print("Means:", gmm.means_) 
print("Covariances:", gmm.covariances_) 
print("Weights:", gmm.weights_)
'''
    print(code)

def b5():
    code = '''import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
movies={
    'title':["The Dark Knight","Inception","Toy Story","Finding Nemo"," The Shawshank Redemption","Pulp Fiction"],
    'genre':["Action,Crime,Drama","Action,Adventure,Sci-Fi","Animation,Adventure,Comedy","Animation,Adventure,Comedy",
             "Drama","Crime,Drama"]
}
movies_df=pd.DataFrame(movies)
user_likes=["The Dark Knight"]
tfidf=TfidfVectorizer(stop_words="english")
tfidf_matrix=tfidf.fit_transform(movies_df["genre"])
cosine_sim=cosine_similarity(tfidf_matrix,tfidf_matrix)

def get_recommendations(title,cosine_sim=cosine_sim):
    idx=movies_df[movies_df["title"]==title].index[0]
    sim_scores=list(enumerate(cosine_sim[idx]))
    sim_scores=sorted(sim_scores,key=lambda x: x[1],reverse=True)
    sim_scores=sim_scores[1:4]
    movie_indices=[i[0] for i in sim_scores]
    return movies_df["title"].iloc[movie_indices]

print("Recommendations based on your likes:")
for liked_movie in user_likes:
    recommendations=get_recommendations(liked_movie)
    print(f"Because you liked'{liked_movie}':")
    print(recommendations.to_string(index=False))
'''
    print(code)

def b6():
    code = '''import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
ratings = {
    'User': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'The Dark Knight': [5, 4, 0, 0, 1],
    'Inception': [4, 5, 2, 0, 0],
    'Toy Story': [1, 2, 5, 4, 0],
    'Finding Nemo': [0, 0, 4, 5, 3],
    'The Shawshank Redemption': [5, 0, 1, 0, 4]
}
 
import pandas as pd
ratings_df = pd.DataFrame(ratings).set_index('User')

def recommend_movies(user_name, ratings_df, n_recommendations=3):
    user_similarity = cosine_similarity(ratings_df.fillna(0))
    user_sim_df = pd.DataFrame(
        user_similarity,
        index=ratings_df.index,
        columns=ratings_df.index
    )
    user_sim_scores = user_sim_df[user_name]
    user_sim_scores = user_sim_scores.drop(user_name)
    similar_users = user_sim_scores.sort_values(ascending=False)
    target_user_ratings = ratings_df.loc[user_name]
    unseen_movies = target_user_ratings[target_user_ratings == 0].index
    
    recommendations = {}
    for movie in unseen_movies:
        weighted_ratings = 0
        similarity_sum = 0
        
        for other_user in similar_users.index:
            if ratings_df.loc[other_user, movie] > 0:
                weighted_ratings += similar_users[other_user] * ratings_df.loc[other_user, movie]
                similarity_sum += similar_users[other_user]
        if similarity_sum > 0:
            recommendations[movie] = weighted_ratings / similarity_sum
    recommended_movies = sorted(recommendations.items(), key=lambda x: x[1],reverse=True)
    return recommended_movies[:n_recommendations]


user = 'Alice'
recommendations = recommend_movies(user, ratings_df)
print(f"Recommendations for {user}:")
for movie, predicted_rating in recommendations:
    print(f"{movie} (predicted rating: {predicted_rating:.2f})")
'''
    print(code)

def b7():
    code = '''import numpy as np
import random

# Step 1: Define the slot machines (arms) with reward probabilities
true_probs = [0.3, 0.5, 0.7]   # A, B, C

# Step 2: Parameters
epsilon = 0.2   # 20% explore
n_rounds = 50   # total plays
n_arms = len(true_probs)

# Step 3: Tracking variables
counts = np.zeros(n_arms)      
# how many times each arm is pulled
rewards = np.zeros(n_arms)    
 # total rewards for each arm

# Step 4: Run simulation
history = []

for t in range(1, n_rounds+1):
    # ε-greedy: explore or exploit
    if random.random() < epsilon:
        choice = random.randint(0, n_arms-1)   # explore
    else:
        choice = np.argmax(rewards / (counts + 1e-6))  # exploit best so far
    
    # Generate reward (1 or 0) based on true probability
    reward = 1 if random.random() < true_probs[choice] else 0
    
    # Update stats
    counts[choice] += 1
    rewards[choice] += reward
    
    # Save history
    avg_rewards = rewards / (counts + 1e-6)
    history.append((t, choice, reward, avg_rewards.copy()))

# Step 5: Print results
print("Final average rewards per arm:", rewards / counts)
print("Total rewards collected:", sum(rewards))
print("Arm chosen most often:", np.argmax(counts))

# Show detailed round history (first 10 rounds)
for h in history[:10]:
    print(f"Round {h[0]} | Chose Arm {h[1]} | Reward={h[2]} | Estimates={h[3]}")
'''
    print(code)

def b8():
    code = '''import gymnasium as gym
import numpy as np
import random

# Create environment
env = gym.make("FrozenLake-v1", is_slippery=False)

# Initialize Q-table
Q = np.zeros((env.observation_space.n, env.action_space.n))

# Monte Carlo parameters
episodes = 5000
epsilon, gamma = 0.3, 1.0

returns_sum, returns_count = {}, {}

for _ in range(episodes):
    state = env.reset()[0]
    episode = []
    done = False
    
    while not done:
        # ε-greedy policy
        action = random.choice(range(env.action_space.n)) if random.random() < epsilon else np.argmax(Q[state])
        next_state, reward, done, _, _ = env.step(action)
        episode.append((state, action, reward))
        state = next_state

    # Update Q-values
    G, visited = 0, set()
    for s, a, r in reversed(episode):
        G = gamma * G + r
        if (s, a) not in visited:
            returns_sum[(s,a)] = returns_sum.get((s,a),0) + G
            returns_count[(s,a)] = returns_count.get((s,a),0) + 1
            Q[s,a] = returns_sum[(s,a)] / returns_count[(s,a)]
            visited.add((s,a))

# ------------------------------
# Derive Policy and Value Function
# ------------------------------
policy = np.argmax(Q, axis=1).reshape(4,4)
V = np.max(Q, axis=1).reshape(4,4)   # Value Function

print("Learned Policy (0=Left,1=Down,2=Right,3=Up):\n", policy)
print("\nLearned Value Function (V):\n",V)'''
    print(code)


def c1():
    code = '''text = "This is my test text. We're keeping this text short to keep things manageable."

# Convert the text to lowercase to ensure uniform word counting
# (e.g., "This" and "this" will be treated as the same word)
text = text.lower()

# Define a function to count words in a given text
def count_words(text):
    # Characters to remove from the text (punctuation marks)
    skips = [".", ",", ":", ";", "'", '"']
    
    # Remove punctuation from the text
    for ch in skips:
        text = text.replace(ch, "")
    
    # Initialize an empty dictionary to store word counts
    word_counts = {}
    
    # Split the text into words by spaces and count occurrences
    for word in text.split(" "):
        # If the word is already in dictionary, increment its count
        if word in word_counts:
            word_counts[word] += 1
        # If word is new, add it to dictionary with count = 1
        else:
            word_counts[word] = 1
    
    # Return the final dictionary of word counts
    return word_counts

# Call the function on our text
num = count_words(text)

# Print the dictionary showing each word and its frequency
print(num)
'''
    print(code)

def c2():
    code = '''# Define the input text
text = "This is my test text. We're keeping this text short to keep things manageable."

# Import Counter from collections (Counter is used for counting hashable objects like words) 
from collections import Counter

# Function to count words quickly using Counter
def count_words_fast(text):
    # Convert text to lowercase (so 'This' and 'this' are treated the same)
    text = text.lower()
    
    # Define punctuation marks to remove
    skips = [".", ",", ":", ";", "'", '"']
        # Remove punctuation from the text
    for ch in skips:
        text = text.replace(ch, "")
    
    # Use Counter to count occurrences of each word
    # text.split(" ") → splits the text into a list of words
    word_counts = Counter(text.split(" "))    
    return word_counts

# Call the function with our text
num = count_words_fast(text)

# Print the dictionary-like Counter object showing word frequencies
print(num)
'''
    print(code)

def c3():
    code = '''# Import the Natural Language Toolkit (NLTK) library
import nltk

# Download the VADER (Valence Aware Dictionary and sEntiment Reasoner) lexicon
# This lexicon contains a list of words and their associated sentiment intensities
nltk.download("vader_lexicon")

# Import the SentimentIntensityAnalyzer from NLTK's sentiment module
from nltk.sentiment import SentimentIntensityAnalyzer

# Create an object of SentimentIntensityAnalyzer
# This object can analyze text and return sentiment scores
s = SentimentIntensityAnalyzer()

# Define the input text to analyze
text = "I hate this product very much"

# Get the sentiment scores for the text
# The result is a dictionary with 4 keys: 
# 'neg' (negative), 'neu' (neutral), 'pos' (positive), and 'compound' (overall score)
score = s.polarity_scores(text)

# Print the sentiment scores
print(score)

# Define a function to interpret the sentiment score based on the 'compound' value
def interpret_sentiment(score):
    # Extract the compound score (overall sentiment between -1 and +1)
    compound = score["compound"]
    
    # If compound score >= 0.05, sentiment is positive
    if compound >= 0.05:
        return "Positive"
    # If compound score <= -0.05, sentiment is negative
    elif compound <= -0.05:
        return "Negative"
    # Otherwise, sentiment is neutral
    else:
        return "Neutral"

# Print the interpreted sentiment for the given text
print(interpret_sentiment(score))
'''
    print(code)

def c4():
    code = '''# A simple Python list of numbers
numbers_list = [1,2,3,4,5,6,7,8,9,10]

# Convert the list into an RDD (Resilient Distributed Dataset) using SparkContext
rdd = sc.parallelize(numbers_list)

# Each element of the RDD is mapped into a tuple (x,)
# so that it can be properly converted into a DataFrame
df_numbers = rdd.map(lambda x: (x,)).toDF(["numbers"])

# Display the DataFrame with column name 'numbers'
df_numbers.show()
'''
    print(code)

def c5():
    code = '''# A list of tuples, each tuple has (name, age)
data = [("Alice",25), ("Bob",35), ("Charlie",40), ("David",28), ("Eva",32)]

# Create a DataFrame from the list, with column names 'name' and 'age'
df_people = spark.createDataFrame(data, ["name","age"])	

# Filter the DataFrame to keep only rows where age > 30
df_people.filter(col("age") > 30).show()
'''
    print(code)

def c6():
    code = '''lines = ["hello world", "hello Spark", "hello PySpark world"]

# Convert list into an RDD
rdd_lines = sc.parallelize(lines)

# Split lines into words, map each word to (word,1), then reduceByKey to count occurrences
word_counts = (rdd_lines
               .flatMap(lambda line: line.split())
               .map(lambda w: (w.lower(), 1))
               .reduceByKey(lambda a,b: a+b)) 

# Collect and print results as a list of (word, count)
print(word_counts.collect())
'''
    print(code)

def c7():
    code = '''data = [("HR",50000), ("IT",70000), ("HR",55000), ("IT",80000), ("Sales",45000)]

# Create DataFrame
df_dept = spark.createDataFrame(data, ["department","salary"])

# Group by department and calculate average salary
df_dept.groupBy("department").avg("salary") \
      .withColumnRenamed("avg(salary)","avg_salary") \
      .show()
'''
    print(code)

def c8():
    code = '''# Sample employee data
left = [(1,"Alice"), (2,"Bob"), (3,"Charlie")]

# Sample department data
right = [(1,"HR"), (2,"IT"), (4,"Finance")]

# Create DataFrames
df_emp = spark.createDataFrame(left, ["employee_id","employee_name"])
df_dept = spark.createDataFrame(right, ["employee_id","department_name"])

# Perform inner join on employee_id
joined = df_emp.join(df_dept, on="employee_id", how="inner")

# Show results
joined.show()
'''
    print(code)