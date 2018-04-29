FROM ubuntu:16.04

MAINTAINER Anton Dnitriev

# Update packages
RUN apt-get -y update

# Install postgresql
ENV PGVER 9.6

RUN apt-get install -y wget
RUN apt-get install -y curl
RUN apt-get install -y python3
RUN apt-get install libpq-dev -y
RUN apt-get install build-essential -y
RUN apt-get install -y python3-pip

RUN echo deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main > /etc/apt/sources.list.d/pgdg.list

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
         apt-key add -

RUN apt-get -y update

RUN apt-get install -y postgresql-$PGVER

# Run the rest of the commands as the ``postgres`` user created by the ``postgres-$PGVER`` package when it was ``apt-get installed``
USER postgres

# Create a PostgreSQL role named ``docker`` with ``12345`` as the password and
# then create a database `docker` owned by the ``docker`` role.
RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER anton WITH SUPERUSER PASSWORD '12345';" &&\
    createdb -O anton anton &&\
    /etc/init.d/postgresql stop

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/$PGVER/main/pg_hba.conf

# And add ``listen_addresses`` to ``/etc/postgresql/$PGVER/main/postgresql.conf``
RUN echo "listen_addresses='*'" >> /etc/postgresql/$PGVER/main/postgresql.conf
RUN echo "synchronous_commit = off" >> /etc/postgresql/$PGVER/main/postgresql.conf
RUN echo "shared_buffers = 256MB" >> /etc/postgresql/$PGVER/main/postgresql.conf
RUN echo "autovacuum = off" >> /etc/postgresql/$PGVER/main/postgresql.conf
# Expose the PostgreSQL port
EXPOSE 5432

EXPOSE 5000

# Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# Back to the root user
USER root

RUN pip3 install psycopg2
RUN pip3 install tornado
RUN pip3 install pytz
RUN pip3 install tzlocal

RUN echo "Europe/Moscow" > /etc/timezone

ENV PGPASSWORD 12345
ENV PYTHONIOENCODING UTF-8
ENV TZ Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD . /forum
WORKDIR /forum

RUN chmod +x ./index.sh
ENTRYPOINT ["./index.sh"]

