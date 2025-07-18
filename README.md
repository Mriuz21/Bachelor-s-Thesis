# AI-Powered Fake News Detection App

This is a full-stack web application for detecting fake news using a fine-tuned versions of BERT and RoBERTA. The system includes a React frontend and a Flask backend with a MySQL database.

## Running the backend

First you need to have installed **MySQL**,**Python** and **pip** .  
I used **Python 3.12.3**.

1. Rename `.env.example` to `.env` and complete it with **your MySQL credentials**.

2. I recommend creating a virtual environment for installing dependencies. Install them using:

    pip install -r requirements.txt

3. Run the `init.py` script. By running it successfully, you should see:

    [INFO] Database and tables initialized.

4. If you are unable to clone the models, you can find them on Kaggle via:  
   - https://www.kaggle.com/models/mariusdudui47/fine_tuned_bert_welfake  
     Create a directory inside `backend/` named `fine_tuned_bert_welfake` and put the files there  
   - https://www.kaggle.com/models/mariusdudui47/my_roberta  
     Create a directory inside `backend/` named `My_Roberta` and put the files there

5. Next step is to run the `app.py` script.

## Running the frontend

1. Go to the `frontend` directory and run:

    npm install

2. Then run:

    npm start

And that should be it.
