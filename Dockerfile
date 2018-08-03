FROM gcr.io/distroless/python3:latest
ADD ./env/lib/python3.6/* /app
ADD proxy.py /app
WORKDIR /app
CMD ["proxy.py"]
