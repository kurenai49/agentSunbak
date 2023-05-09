FROM python:3.10

WORKDIR /home/

RUN git clone https://github.com/kurenai49/joonggoboat.git

WORKDIR /home/joonggoboat/

RUN pip install -r requirements.txt

RUN echo "SECRET_KEY=django-insecure-8=0reqa5hmq)h7r7+67=nsy6sde42)l3-jc%-ibbag*s362nf#" > .env

RUN python manage.py migrate

EXPOSE 8000

CMD ["python","manage.py","runserver","0.0.0.0:8000"]