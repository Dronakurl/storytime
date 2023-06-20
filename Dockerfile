FROM python:3.11-slim as base
COPY pyproject.toml ./pyproject.toml
COPY . ./
RUN pip install .[extras]
# RUN pip install --no-cache-dir .[extras]
CMD streamlit run storytime_ai/webapp.py 
