FROM python
RUN mkdir /monitoring_app
RUN chmod 777 /monitoring_app
COPY . /monitoring_app
WORKDIR /monitoring_app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
