FROM python:3.11-slim
EXPOSE 8080
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./
RUN pip install .[webapp]
# CMD streamlit run storytime_ai/webapp.py --server.port 8080 --server.address=0.0.0.0
ENTRYPOINT ["streamlit", "run", "storytime_ai/webapp.py", "--server.port=8080", "--server.address=0.0.0.0"]
