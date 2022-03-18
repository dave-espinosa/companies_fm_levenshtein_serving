#! /bin/bash

read -p "Enter e-mail liked with GCP : " my_account
gcloud auth login "$my_account"
local_pwd="$PWD"
mkdir -p data/processed
cd "data/processed" || exit
gsutil -m cp -r  gs://job_data_results/MachineLearning/company_names_cleaned_v1.0.csv "$PWD"
printf "Data downloaded sucessfully!"

# Logout GCP
gcloud auth revoke
