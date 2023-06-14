# Getting Started

## First time setting up the enviroment
### 1. Install python3.8.9

This program is developed and tested under python3.8.9. Other versions of python might work but is not guaranteed.
### 2. Create virtual enviroment and activate

Under the project's root directory, run:

`python3 -m venv venv`


`source venv/bin/activate`

### 3. Install dependencies

`pip install -r requirements.txt`

### 4. (Optional) Reactivate the virtual enviroment

If you have installed other versions of otree on your computer before, you can reactivate the virtual enviroment to make sure you are using the otree in the venv:

`source venv/bin/activate`

## Running the program on your local machine
### 1. Activate the virtual enviroment

Go to the project's root directory and run:

`source venv/bin/activate`

### 2. Start Otree

`otree devserver`

## Running the program on Google Cloud

### 1. Logging in to the Google Cloud machine

### 2. Switch to the Super User
The password is `1234`
```console
YOUR_NAME@instance-2:/path$ su
```
You should see:
```console
root@instance-2:/path#
```


### 3. Git clone the repository

### 4. Setting up the enviroment

Check the ["First time setting up the enviroment"](#first-time-setting-up-the-enviroment) section above

### 5. Activate the virtual enviroment

Go to the project's root directory and run:

`source venv/bin/activate`

### (Optional) Set OTREE_PRODUCTION=1 to enter production mode

`export OTREE_PRODUCTION=1`

### 6. Start Otree

`otree prodserver 80`

## Debug
If the program doesn't work for some reasons, you can try two things:

1. Reactivate the virtuanl enviroment

`source venv/bin/activate`

2. Reset the otree database

`otree resetdb`
