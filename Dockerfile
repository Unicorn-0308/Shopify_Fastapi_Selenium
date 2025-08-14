FROM python:3.11

# Creating base folder used by the application
# And installing dependencies for google-chrome-stable
RUN mkdir /app \
    && apt-get update \
    && apt-get install -y \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgbm1 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libx11-xcb1 \
        libxcb-dri3-0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        xdg-utils \
        libgdk-pixbuf2.0-0

WORKDIR /app

EXPOSE 8000

COPY requirements.txt /app/
COPY applications/google_chrome_86_0_4240_75.deb /app/applications/
COPY applications/chromedriver /app/applications/

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --upgrade \
    && dpkg -i applications/google_chrome_86_0_4240_75.deb \
    && chmod a+x applications/chromedriver

COPY api/ /app/api/

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]