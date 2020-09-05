.PHONY: all clean

all:
	./build

clean:
	$(RM) -r dist/
	find lib/ -type d -name __pycache__ | xargs $(RM) -r
