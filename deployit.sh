echo "Should I run the app? (y/N)"
read run_app
if [ "$run_app" = "y" ]; then
    poetry run streamlit run app.py
fi
echo "Should I run pre-commit? (y/N)"
read run_precommit
if [ "$run_precommit" = "y" ]; then
    poetry run pre-commit run 
fi
echo "Should I update poetry? (y/N)"
read update_poetry
if [ "$update_poetry" = "y" ]; then
    poetry install --all-extras
    poetry update
    poetry lock
    poetry export -f requirements.txt --output requirements.txt --without-hashes --extras webapp
fi
echo "Should I test the docker image locally? (y/N)"
read test_docker
if [ "$test_docker" = "y" ]; then
    docker build -t storytime .
    docker run -p 8080:8080 storytime
fi
echo "Should I deploy to GCP? (y/N)"
read deploy_gcp
if [ "$deploy_gcp" = "y" ]; then
    gcloud app deploy
fi
