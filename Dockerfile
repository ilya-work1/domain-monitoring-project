FROM python
RUN mkdir /selenium_test
RUN chmod 777 /selenium_test
COPY . /selenium_test
WORKDIR /selenium_test
RUN pip install -r requirements.txt
CMD ["python", "test_run.py"]
