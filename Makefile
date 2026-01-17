# Makefile
.PHONY: all build docker clean

all: build

build:
	mkdir -p build
	python3 src/make_binary.py build/hello.bin
	chmod +x build/hello.bin
	file build/hello.bin

docker:
	docker build -t pure-hello-world .
	docker run --rm pure-hello-world

test:
	@echo "Testing local binary..."
	./build/hello.bin

clean:
	rm -rf build
	docker rmi pure-hello-world 2>/dev/null || true