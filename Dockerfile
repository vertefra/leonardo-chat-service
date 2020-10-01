FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /usr/app

# copy first the requirements to avoid that a change in the source code
# will trigger a coomplete reinstall 


COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./ ./

EXPOSE 80

CMD ["python3", "app/main.py"]






