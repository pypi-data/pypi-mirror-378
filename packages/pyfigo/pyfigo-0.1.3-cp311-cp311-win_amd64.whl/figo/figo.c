#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <string.h>

#define BLOCK_SIZE 80
#define BUFFER_SIZE 1024

static PyObject* get(PyObject* self, PyObject* args) {
    const char* filename;
    if (!PyArg_ParseTuple(args, "s", &filename))
        return NULL;

    FILE* f = fopen(filename, "rb");
    if (!f) {
        PyErr_SetFromErrnoWithFilename(PyExc_OSError, filename);
        return NULL;
    }

    char buffer[BUFFER_SIZE];
    const char target[] = "OBJECT";

    while (1) {
        size_t n = fread(buffer, 1, BUFFER_SIZE, f);
        if (n == 0) {
            fclose(f);
            Py_RETURN_NONE;
        }

        for (size_t i = 0; i + BLOCK_SIZE <= n; i += BLOCK_SIZE)
        {
            if (memcmp(buffer + i, target, 6) == 0)
            {
                char *first = buffer + i + 10;
                char *second = memchr(first + 1, '\'', (buffer + i + BLOCK_SIZE) - (first + 1));
                if (!second)
                    continue;
                size_t length = second - (first + 1);
                fclose(f);
                return PyUnicode_FromStringAndSize(first + 1, length);
            }
        }

        if (n < BUFFER_SIZE) break; // EOF
    }

    fclose(f);
    Py_RETURN_NONE;
}

static PyMethodDef Methods[] = {
    {
        "get", get, METH_VARARGS, 
        "Get the OBJECT keyword from a fits file\n\n"\
        "Args:\n"\
        "    filename (str): Name of FITS file\n\n"\
        "Returns:\n"\
        "    str: Value of the OBJECT keyword in the fits file\n"
    },
    {NULL, NULL, 0, NULL}
};

/* Module definition */
static struct PyModuleDef figomodule = {
    PyModuleDef_HEAD_INIT, 
    "cfigo", 
    "Get the OBJECT keyword from a fits file",
    -1,
    Methods
};

/* Initialization function */
PyMODINIT_FUNC PyInit_cfigo(void) {
    return PyModule_Create(&figomodule);
}
