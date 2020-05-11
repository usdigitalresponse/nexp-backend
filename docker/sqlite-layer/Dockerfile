# docker/sqlite-layer/Dockerfile

FROM lambci/lambda:build-python3.8

ENV PYTHON_VERSION=3.8.2

RUN yum update -y \
      && yum upgrade -y \
      && yum install -y tar xz yum-utils make automake gcc gcc-c++

RUN curl -O https://sqlite.org/2020/sqlite-amalgamation-3310100.zip \
      && unzip ./sqlite-amalgamation-3310100.zip \
      && cd ./sqlite-amalgamation-3310100        \
      && cd -

RUN pip install virtualenv   \
      && virtualenv sqlite   \
      && cd sqlite           \
      && source bin/activate \
      && cd -                \
      && git clone https://github.com/coleifer/pysqlite3 \
      && cd pysqlite3 \
      && cp ../sqlite-amalgamation-3310100/sqlite3.[ch] .  \
      && python setup.py build_static \
      && python setup.py install

RUN mkdir -p /var/task/python/ \
      && cp -r ./sqlite/lib/python3.8/site-packages/pysqlite3-0.4.2-py3.8-linux-x86_64.egg/pysqlite3/* /var/task/python

WORKDIR /var/task

CMD ["bash"]
