FROM python:3.9

WORKDIR /app

COPY cert.pem /app/cert.pem
COPY key.pem /app/key.pem

COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        texlive \
        texlive-latex-extra \
        texlive-fonts-recommended \
        texlive-lang-english \
        texlive-lang-european \
        texlive-xetex \
        texlive-luatex && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY Tahoma.ttf /usr/share/fonts/truetype/Tahoma.ttf

EXPOSE 5050

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5050

CMD ["flask", "run", "--cert=cert.pem", "--key=key.pem", "--debugger", "--reload"]

