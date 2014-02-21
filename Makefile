# Change these to match your source code.
TARGET	= glupy.so
OBJECTS	= glupy.o

# Change these to match your environment.
GLFS_SRC  = $(HOME)/glusterfs
GLFS_ROOT = /usr/lib64
GLFS_VERS = 3git
HOST_OS  = GF_LINUX_HOST_OS
PYTHON_GLUSTER_DIR = /usr/lib/python2.6/site-packages/gluster/

# You shouldn't need to change anything below here.
XLATOR_DIR = $(GLFS_ROOT)/glusterfs/$(GLFS_VERS)/xlator/features
GLUPY_DIR = $(XLATOR_DIR)/glupy/
PY_FILES = debug-trace.py helloworld.py negative.py
GLUPY_PY = glupy.py

CFLAGS	= -fPIC -Wall -O0 -g \
	  -DHAVE_CONFIG_H -D_FILE_OFFSET_BITS=64 -D_GNU_SOURCE -D$(HOST_OS) \
	  -DGLUSTER_PYTHON_PATH=\"$(GLUPY_DIR)\" \
	  -I$(GLFS_SRC) -I$(GLFS_SRC)/libglusterfs/src \
	  -I$(GLFS_SRC)/contrib/uuid -I.
LDFLAGS	= -module -avoid-version -shared -nostartfiles -L$(GLFS_ROOT) \
	  -lglusterfs -lpthread -lpython2.6

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(OBJECTS) $(LDFLAGS) -o $(TARGET)

install: $(TARGET)
	cp -f $(TARGET) $(XLATOR_DIR)
	mkdir -p $(GLUPY_DIR)
	cp -f $(PY_FILES) $(GLUPY_DIR)
	cp -f $(GLUPY_PY) $(PYTHON_GLUSTER_DIR)

uninstall: $(TARGET)
	rm -f $(XLATOR_DIR)/$(TARGET)
	rm -f $(PYTHON_GLUSTER_DIR)/glupy.py
	rm -f $(GLUPY_DIR)/debug-trace.py
	rm -f $(GLUPY_DIR)/helloworld.py
	rm -f $(GLUPY_DIR)/negative.py
	rmdir --ignore-fail-on-non-empty $(GLUPY_DIR)

clean:
	rm -f $(TARGET) $(OBJECTS)
