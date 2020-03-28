#include <cstdio>
#include <Python.h>
#include <numpy/arrayobject.h>

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <cstring>
#include <assert.h>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <ctime>
#include <assert.h>

using namespace std;
const int WINDOW_SIZE = 100;
const int READ_BEGIN = 123;
const int READ_END = 99;

const int INS_CAP = 100;
const int INS_FLAG = 200;

const int FEAT_DIM[2] = {250,550};

inline int base2int(char x) {
    switch (x) {
        case 'A': return 0;
        case 'C': return 1;
        case 'G': return 2;
        case 'T': return 3;
        case 'N': return 4;
        case 'a': return 5;
        case 'c': return 6;
        case 'g': return 7;
        case 't': return 8;
        case '*': return 9;
        default: return -1;
    }
}
inline int get_strand(int x) {
    if (x==4 || x==9) return 2;
    return x<4;
    // del => 2
    // ACGT => 1
    // acgt => 0
}

inline int get_last_ins (int x, int y) {
    int xx = get_strand(x);
    int yy = get_strand(y);
    int cntdel = (xx==2) + (yy==2);
    int cnt1 = (xx==1) + (yy==1);
    int cnt0 = (xx==0) + (yy==0);
    assert(cnt0 * cnt1 == 0);
    int strand = cnt0 > 0;

    return 5 * (x%5) + (y%5) + (strand * 25) + 250;
}

inline int get_kmer(int x, int y, int z) {
    int xx = get_strand(x);
    int yy = get_strand(y);
    int zz = get_strand(z);
    int cntdel = (xx==2) + (yy==2) + (zz==2);
    int cnt1 = (xx==1) + (yy==1) + (zz==1);
    int cnt0 = (xx==0) + (yy==0) + (zz==0);
    assert(cnt0 * cnt1 == 0);
    int strand = cnt0 > 0;

    return 25 * (x%5) + 5 * (y%5) + (z%5) + (strand * 125);
}


vector<string> split(const string & str, int n) {
	auto s = strdup(str.c_str());
	char * pch = strtok(s,"\t");
	vector<string> ret;
	while (n--) {
		ret.push_back(string(pch));
		pch = strtok(NULL, "\t");
	}
	free(s);
	return ret;
}

vector<int> parse1(string seq) {
		vector<int> ret;
		bool num_mode = 0;
		bool prev_is_hat = 0;
		int fetched_num = 0;

		for (auto x : seq) {
			if (prev_is_hat) {
				prev_is_hat = 0;
			} else if (x == '+' || x == '-') {
				num_mode = 1; fetched_num = 0;
			} else if (num_mode) {
				if (isdigit(x)) fetched_num = fetched_num * 10 + x - '0';
				else {
					// DEL pattern is redundant // INS pattern is not used yet
					num_mode = 0;
					--fetched_num;
				}
			} else if (fetched_num) {
				--fetched_num;
			} else {
                int t = base2int(x);
                if (t != -1) {
                    ret.push_back(t);
                } else if (x=='^') {
                    prev_is_hat = 1; // discard the following mapping quality
                    ret.push_back(READ_BEGIN);
                } else if (x=='$') {
                    {
                    int x = ret.back();
                    ret.pop_back();
                    ret.push_back(READ_END);
                    ret.push_back(x);
                    }
                } else {
                    puts(seq.c_str()); assert(0 && "unknown char in pileup");
                }
			}
		}
	return ret;
}

void output1(vector<vector<int> > & buffer, int* ret) {
	auto now = buffer.begin()+2;
	while (now != buffer.end()) {
		auto left = now - 2;
		auto mid = now - 1;
		auto right = now;
		auto l = left->begin();
		auto m = mid->begin();
		auto r = right->begin();
		while (l!=left->end()) {
			if (*l==READ_END) {++l;++l; continue;}
			if (*m==READ_END) {++m;++m;++l; continue;}
			if (*r==READ_END) {++r;}
			if (*l == READ_BEGIN) ++l;
            int kmer = get_kmer(*l,*m,*r);
			ret[kmer]++;
			++l;++m;++r;
		}
		++now;
		ret += FEAT_DIM[0];
	}
}


vector<int> parse2(string seq) {
        vector<int> ret;
        int indel_mode = 0; // 1 => indel, 0 => off
        bool is_ins = 0; 
        bool prev_is_hat = 0;
        int fetched_num = 0;
        string indel_pattern = "";

        for (auto x : seq) {
            if (prev_is_hat) {
                prev_is_hat = 0;
            } else if (x == '+' || x == '-') {
                indel_mode = 1; fetched_num = 0; is_ins = x=='+';
            } else if (indel_mode) {
                if (isdigit(x)) fetched_num = fetched_num * 10 + x - '0';
                else {
                    indel_mode = 0;
                    indel_pattern += x;
                    --fetched_num;
                        if (fetched_num == 0 && is_ins && indel_pattern.size() < INS_CAP) {
                            ret.push_back(INS_FLAG);
                            for (auto & ch : indel_pattern) ret.push_back(base2int(ch));
                            ret.push_back(INS_FLAG);
                        }
                    if (fetched_num == 0) indel_pattern.clear();

                }
            } else if (fetched_num) {
                indel_pattern += x;
                --fetched_num;
                if (fetched_num == 0 && is_ins && indel_pattern.size() < INS_CAP) {
                    ret.push_back(INS_FLAG);
                    for (auto & ch : indel_pattern) ret.push_back(base2int(ch));
                    ret.push_back(INS_FLAG);
                }
                if (fetched_num == 0) indel_pattern.clear();
                    
            } else {
                int t = base2int(x);
                if (t != -1) {
                    ret.push_back(t);
                } else if (x=='^') {
                    prev_is_hat = 1; // discard the following mapping quality
                    ret.push_back(READ_BEGIN);
                } else if (x=='$') {
                    {
                    int x = ret.back();
                    if (x==INS_FLAG) {
						// XXX simply remove this ins
						ret.pop_back();
						while (ret.back() != INS_FLAG) ret.pop_back();
						ret.pop_back();
						x = ret.back();
					}
                    ret.pop_back();
                    ret.push_back(READ_END);
                    ret.push_back(x);
                    }
                } else {
                    puts(seq.c_str()); assert(0 && "unknown char in pileup");
                }
            }
        }
    return ret;
}

void output2(vector<vector<int>> & buffer, int* ret) {
    auto now = buffer.begin()+2;
    int prevl, prevm, prevr;
    auto this_row = ret;
    while (now != buffer.end()) {
        auto left = now - 2;
        auto mid = now - 1;
        auto right = now;
        auto l = left->begin();
        auto m = mid->begin();
        auto r = right->begin();
        while (l!=left->end()) {
            if (*l == INS_FLAG) { ++l; while (*l != INS_FLAG) ++l; ++l; continue; }
            if (*l==READ_END) {++l;++l; continue;}
            if (*l == READ_BEGIN) ++l;
            if (*m==READ_END) {++m;++m;++l; continue;}
            if (*m == INS_FLAG) {
                ++m;
                vector<int> pattern {prevl, prevm};
                while (*m != INS_FLAG) { pattern.push_back(*m); ++m; }
                ++m;
                pattern.push_back(prevr);

                for (int i=0;i<pattern.size()-2;++i) {
                    int kmer = get_kmer(pattern[i],pattern[i+1],pattern[i+2]);
                    this_row[250+kmer]++;
                }
                int last = get_last_ins(pattern[pattern.size()-2],pattern[pattern.size()-1]);
                this_row[250+last]++;
                continue;
            }

            if (*r == INS_FLAG) { ++r; while (*r != INS_FLAG) ++r; ++r; continue; }
            if (*r==READ_END) {++r;}

            int kmer = get_kmer(*l,*m,*r);
            prevl = *l; prevm = *m; prevr = *r;
            this_row[kmer]++;
            ++l;++m;++r;
        }

        if (m != mid->end() && *m == INS_FLAG) {
            ++m;
            vector<int> pattern {prevl, prevm};
            while (*m != INS_FLAG) { pattern.push_back(*m); ++m; }
            ++m;
            pattern.push_back(prevr);
    
            for (int i=0;i<pattern.size()-2;++i) {
                int kmer = get_kmer(pattern[i],pattern[i+1],pattern[i+2]);
                this_row[250+kmer]++;
            }
            int last = get_last_ins(pattern[pattern.size()-2],pattern[pattern.size()-1]);
            this_row[250+last]++;
        }

        ++now;
        this_row += FEAT_DIM[1];
    }
}

void my_main(FILE* pipe, int* ret, int phase) {
    vector<vector<int> > buffer;
    //int nr = 0;
    const int LEN = 65536;
    char row[LEN];

    while (fgets(row, LEN, pipe) != nullptr) {
        if (strlen(row) == LEN - 1) throw "row in pileup is too long";
        auto && tokens = split(row,5);
        vector<int> X;
        if (stoi(tokens[3]) != 0) X = phase ? parse2(tokens[4]) : parse1(tokens[4]); 
        {
            buffer.emplace_back(X);
            if (buffer.size() == WINDOW_SIZE+2) {
                phase ? output2(buffer, ret) : output1(buffer,ret);
                ret += FEAT_DIM[phase] * WINDOW_SIZE;
                buffer.erase(buffer.begin(),buffer.begin()+WINDOW_SIZE);
            }
        }
        //if (++nr % 1000000 == 0) fprintf(stderr,"%d base parsed.\n", nr);
    }
}

PyObject* gen_phase_pipe(PyObject* args, int phase) {
    PyObject *out_array;
    char *fn;
    char *ctg;
    int start, end;
    char cmd[256];
    if (!PyArg_ParseTuple(args, "siis", &ctg, &start, &end, &fn)) return NULL;
    sprintf(cmd, "samtools mpileup -r %s:%d-%d -B -q0 -Q0 -aa %s", ctg, start, end, fn);
    auto pipe = popen(cmd, "r");
    int nr = end - start + 1;
	nr = (nr-2) / WINDOW_SIZE;
	npy_intp dim = FEAT_DIM[phase] * WINDOW_SIZE * nr;
    auto ret = new int[dim];
    my_main(pipe, ret, phase);
    pclose(pipe);
	out_array = PyArray_SimpleNewFromData(1, &dim, NPY_INT32, ret);
	return out_array;
}

static PyObject* gen_phase1(PyObject* self, PyObject* args) {
    return gen_phase_pipe(args, 0);
}

static PyObject* gen_phase2(PyObject* self, PyObject* args) {
    return gen_phase_pipe(args, 1);
}

static PyMethodDef Methods[] =
{
     {"gen_phase1", gen_phase1, METH_VARARGS, "gen tensor for phase 1"},
     {"gen_phase2", gen_phase2, METH_VARARGS, "gen tensor for phase 2"},
     //{"gen_phase_pipe", gen_phase_pipe, METH_VARARGS, "gen tensor using pipe for phase 1"},
     {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initparse_pileup(void) {
    PyObject *module;
    module = Py_InitModule("parse_pileup", Methods);
    if(module==NULL) return;
    /* IMPORTANT: this must be called */
    import_array();
    return;
}

