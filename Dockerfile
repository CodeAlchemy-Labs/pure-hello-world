FROM alpine:latest AS builder

# Install Python and 'file' utility for verification
RUN apk add --no-cache python3 file

WORKDIR /app
COPY src/make_binary.py .

# Generate and verify the binary
RUN python3 make_binary.py /app/hello.bin && \
    file /app/hello.bin && \
    echo "Build successful."

# Final minimal image
FROM alpine:latest
COPY --from=builder /app/hello.bin /usr/local/bin/hello
ENTRYPOINT ["/usr/local/bin/hello"]