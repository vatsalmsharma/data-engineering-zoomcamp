FROM python:3.11
# FROM tell the base image we want to use 

RUN pip install pandas

WORKDIR /app
COPY pipeline.py pipeline.py

# ENTRYPOINT [ "bash" ]
ENTRYPOINT [ "python", "pipeline.py" ]

# Docker to SQL
