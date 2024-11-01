FROM python:3.12.7

WORKDIR /code

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the rest of the application code to the container
COPY ./fast_api /code/fast_api
COPY ./features /code/features
COPY ./navigation /code/navigation
COPY ./streamlit_app.py /code/streamlit_app.py

CMD ["/bin/bash", "-c", "uvicorn fast_api.fast_api_setup:app --host 0.0.0.0 --port 8000 --reload & streamlit run streamlit_app.py --server.port 8501"]
