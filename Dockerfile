FROM python:3.11
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    make \
    cmake \
    zlib1g-dev \
    git 
RUN lsb_release -a
RUN wget https://apache.jfrog.io/artifactory/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb
RUN apt install ./apache-arrow-apt-source-latest-focal.deb

RUN apt update

RUN apt install libarrow-dev libarrow-python-dev
RUN ARROW_HOME=/usr PYARROW_CMAKE_OPTIONS="-DARROW_ARMV8_ARCH=armv8-a" pip install pyarrow
COPY requirements.txt /requirements.txt
RUN pip3 install --prefer-binary -r requirements.txt
WORKDIR /app
COPY . /app
RUN pip install --prefer-binary .[webapp]
ENTRYPOINT ["streamlit", "run", "storytime_ai/webapp.py", "--server.port=8080", "--server.address=0.0.s0.0"]
