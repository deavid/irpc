GDC=/usr/bin/gdc
DMD=./dmd/bin/dmd

SOURCES=irpcchatter.d messagequeue.d test.d irpcsocket.d
OBJS=irpcchatter.o messagequeue.o test.o irpcsocket.o
EXE=test

all: $(EXE)

$(EXE): $(SOURCES)
	$(GDC) $(SOURCES) -o $(EXE)
# $(DMD) $(SOURCES) -of$(EXE)
    
run: $(EXE)
	./$(EXE)


clean:
	unlink $(EXE) || true
	rm $(OBJS) || true