#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>

/* --- Structure C pour l'objet Graph (private) --- */
typedef struct {
    PyObject_HEAD
    long *data;         /* tableau plat rows * cols */
    Py_ssize_t rows;
    Py_ssize_t cols;
} Graph;

/* --- dealloc : libère la mémoire C si allouée --- */
static void
Graph_dealloc(Graph *self)
{
    if (self->data) {
        free(self->data);
        self->data = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject *) self);
}

/* --- new : allocation mémoire pour l'objet Python --- */
static PyObject *
Graph_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Graph *self = (Graph *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->data = NULL;
        self->rows = 0;
        self->cols = 0;
    }
    return (PyObject *) self;
}

/* --- init : __init__(self, matrix) — matrix = iterable of iterables --- */
static int
Graph_init(Graph *self, PyObject *args, PyObject *kwds)
{
    PyObject *matrix = NULL;
    if (!PyArg_ParseTuple(args, "O", &matrix)) {
        return -1;
    }

    /* Vérifier que c'est une séquence */
    if (!PySequence_Check(matrix)) {
        PyErr_SetString(PyExc_TypeError, "matrix must be a sequence (list of lists)");
        return -1;
    }

    Py_ssize_t nrows = PySequence_Length(matrix);
    if (nrows < 0) return -1;

    if (nrows == 0) {
        /* empty matrix -> rows=cols=0, data=NULL */
        self->rows = 0;
        self->cols = 0;
        self->data = NULL;
        return 0;
    }

    /* Première passe : déterminer cols et vérifier rectangulaire */
    PyObject *first_row = PySequence_GetItem(matrix, 0); /* new ref */
    if (first_row == NULL) return -1;
    if (!PySequence_Check(first_row)) {
        Py_DECREF(first_row);
        PyErr_SetString(PyExc_TypeError, "matrix must be a sequence of sequences");
        return -1;
    }
    Py_ssize_t ncols = PySequence_Length(first_row);
    if (ncols < 0) { Py_DECREF(first_row); return -1; }
    Py_DECREF(first_row);

    for (Py_ssize_t i = 0; i < nrows; ++i) {
        PyObject *row = PySequence_GetItem(matrix, i); /* new ref */
        if (row == NULL) return -1;
        if (!PySequence_Check(row)) {
            Py_DECREF(row);
            PyErr_SetString(PyExc_TypeError, "each row must be a sequence");
            return -1;
        }
        Py_ssize_t len = PySequence_Length(row);
        Py_DECREF(row);
        if (len != ncols) {
            PyErr_SetString(PyExc_ValueError, "matrix rows must have the same length");
            return -1;
        }
    }

    /* Allouer le buffer C (rows * cols) */
    long *buf = (long *) malloc(sizeof(long) * (size_t)(nrows * ncols));
    if (buf == NULL) {
        PyErr_NoMemory();
        return -1;
    }

    /* Deuxième passe : copier les valeurs (on exige des entiers) */
    for (Py_ssize_t i = 0; i < nrows; ++i) {
        PyObject *row = PySequence_GetItem(matrix, i); /* new ref */
        if (row == NULL) { free(buf); return -1; }
        for (Py_ssize_t j = 0; j < ncols; ++j) {
            PyObject *item = PySequence_GetItem(row, j); /* new ref */
            if (item == NULL) {
                Py_DECREF(row);
                free(buf);
                return -1;
            }
            long v = PyLong_AsLong(item);
            Py_DECREF(item);
            if (PyErr_Occurred()) { Py_DECREF(row); free(buf); return -1; }
            buf[i * ncols + j] = v;
        }
        Py_DECREF(row);
    }

    /* Si l'objet avait déjà des données (ré-init), on les libère */
    if (self->data) free(self->data);

    self->data = buf;
    self->rows = nrows;
    self->cols = ncols;
    return 0;
}

/* --- Méthode display(self) : renvoie une chaîne contenant la matrice --- */
static PyObject *
Graph_display(Graph *self, PyObject *Py_UNUSED(ignored))
{
    if (self->rows == 0 || self->cols == 0 || self->data == NULL) {
        PySys_WriteStdout("[]\n");
        Py_RETURN_NONE;
    }

    for (Py_ssize_t i = 0; i < self->rows; ++i) {
        PySys_WriteStdout("[");
        for (Py_ssize_t j = 0; j < self->cols; ++j) {
            long v = self->data[i * self->cols + j];
            if (j + 1 < self->cols) {
                /* element + comma+space */
                PySys_WriteStdout("%ld, ", v);
            } else {
                /* last element */
                PySys_WriteStdout("%ld", v);
            }
        }
        PySys_WriteStdout("]\n");
    }

    Py_RETURN_NONE;
}

/* --- __repr__ pour l'objet Graph --- */
static PyObject *
Graph_repr(Graph *self)
{
    return PyUnicode_FromFormat("Graph(rows=%zd, cols=%zd)", self->rows, self->cols);
}

/* --- Méthodes exposées --- */
static PyMethodDef Graph_methods[] = {
    {"display", (PyCFunction) Graph_display, METH_NOARGS,
     "Return a string representation of the adjacency matrix."},
    {NULL}  /* sentinel */
};

/* --- Définition du type Graph --- */
static PyTypeObject GraphType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_fastgraphFPMS.Graph",
    .tp_basicsize = sizeof(Graph),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "Graph object storing adjacency matrix in C (private)",
    .tp_methods = Graph_methods,
    .tp_new = Graph_new,
    .tp_init = (initproc) Graph_init,
    .tp_dealloc = (destructor) Graph_dealloc,
    .tp_repr = (reprfunc) Graph_repr,
};

/* --- Module --- */
static PyMethodDef module_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fastgraph_module = {
    PyModuleDef_HEAD_INIT,
    "_fastgraphFPMS",
    "Minimal module providing Graph type implemented in C.",
    -1,
    module_methods
};

PyMODINIT_FUNC
PyInit__fastgraphFPMS(void)
{
    PyObject *m;
    if (PyType_Ready(&GraphType) < 0)
        return NULL;

    m = PyModule_Create(&fastgraph_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&GraphType);
    if (PyModule_AddObject(m, "Graph", (PyObject *) &GraphType) < 0) {
        Py_DECREF(&GraphType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
