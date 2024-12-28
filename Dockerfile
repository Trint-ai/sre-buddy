FROM python:3.12.7


ADD src/requirements.txt src/requirements.txt
RUN pip install -r src/requirements.txt


ADD src/ src/
WORKDIR src/app
CMD ["python","-u","main.py"]
