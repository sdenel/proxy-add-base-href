A small Python script, that aims to be used as a proxy between the client and a service that does not provide a <base href="..."> tag.

# Usage wih Docker
```bash
docker pull sdenel:proxy-add-base-href:latest
docker run -p8765:8765 \
    -e BASE_HREF="http://something.com/registry" \
    -e TARGET_URL="http://registry:8080/" \
    proxy-add-base-href:latest
```
