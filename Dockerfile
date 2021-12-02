FROM python:3.10.0-slim-buster

###########################################
# --- Install Chrome and Chromedriver --- #
###########################################

# # We need wget to set up the PPA and xvfb to have a virtual screen and unzip to install the Chromedriver
# RUN apt-get update -y
# RUN apt-get install -y wget xvfb unzip gnupg2

# # Set up the Chrome PPA
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# # Update the package list and install chrome
# RUN apt-get update -y
# RUN apt-get install -y google-chrome-stable

# # Set up Chromedriver Environment variables
# ENV CHROMEDRIVER_VERSION 2.19
# ENV CHROMEDRIVER_DIR /chromedriver
# RUN mkdir $CHROMEDRIVER_DIR

# # Download and install Chromedriver
# RUN wget -q --continue -P $CHROMEDRIVER_DIR "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
# RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# # Put Chromedriver into the PATH
# ENV PATH $CHROMEDRIVER_DIR:$PATH

# these install commands come from: https://github.com/dimmg/dockselpy/blob/master/Dockerfile

# install build dependencies
RUN echo "===> Installing system dependencies..." && \
    BUILD_DEPS="curl unzip bzip2" && \
    apt-get update && apt-get install --no-install-recommends -y wget \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 libgbm1 \
    $BUILD_DEPS \
    xvfb

# install geckodriver
RUN echo "===> Installing geckodriver" && \
    GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

# install firefox
RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

# install chrome
RUN CHROME_SETUP=google-chrome.deb && \
    wget -O $CHROME_SETUP "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" && \
    dpkg -i $CHROME_SETUP && \
    apt-get install -y -f && \
    rm $CHROME_SETUP


###########################
# --- Install Firefox --- #
###########################

# RUN echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" >> /etc/apt/sources.list.d/sources.list
# # RUN echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" >> /etc/apt/sources.list.d/debian.list
# RUN dpkg --add-architecture i386
# RUN apt-get update -y
# # RUN apt-get install -y --no-install-recommends firefox
# RUN apt-get install -y libcrypt1:i386
# RUN apt-get install -y -t unstable firefox


#######################
# --- Install App --- #
#######################

WORKDIR /app

# copy *just enough* files to install the linkedin_bot package
COPY ./requirements.txt ./requirements.txt
COPY src/ ./src/
COPY make.sh ./make.sh
RUN /bin/bash make.sh install

# copy the rest of the source code
COPY . .