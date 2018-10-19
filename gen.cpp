#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <cstring>
#include <assert.h>
#include <algorithm>
#include <fstream>

using namespace std;

const int OUTCOUNT = 100;

struct VCF {
	VCF (int p, char r, char a, char a2, int g) : pos(p), alt(a), ref(r), gt(g), a2(a2) {};
	int pos;
	char ref;
	char alt;
	char a2;
	int gt;
};

inline int base2int(char x) {
	switch (x) {
		case 'A': return 0;
		case 'C': return 1;
		case 'G': return 2;
		case 'T': return 3;
		case '-': return 4;
		default:
			assert(0);
	}
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

void readbed (vector<pair<int, int>> & bed, char* fn) {
	ifstream fin(fn);
	string foo;
	int st, ed;
	while (fin >> foo >> st >> ed)
		bed.emplace_back(st+1, ed+1);
}

void readvcf (map<int, VCF> & vcf, char * fn) {
	ifstream fin(fn);
	string row;
	while (getline(fin, row)) {
		if (row[0]=='#') continue;
		auto tokens = split(row, 10);
		int pos = stoi(tokens[1]);
		auto & ref = tokens[3];
		auto & alt = tokens[4];
		int gt = tokens[9][0] + tokens[9][2] - '0' - '0';
		if (gt==3) {
			//fprintf(stderr, "%s\n",row.c_str());
			continue; // XXX
		}
		if (alt.size()>1) continue; // XXX no insertion

		if (ref.size() == 1) {
			// snp
			VCF t(pos, ref[0], alt[0], '/', gt);
			vcf.insert(make_pair(pos,t));
		} else {
			for (int i=1;i<ref.size();++i) {
				VCF t(pos, ref[i], '-', '/', gt);
				vcf.insert(make_pair(pos+i, t));
			}
		}

	}
}

void readref (string & ref, char* fn) {
	ifstream fin(fn);
	string row;
	getline(fin, row);
	ref = "-";
	while (getline(fin, row)) {
		ref += row;
	}
}

void parse(string seq, vector<int> & ret) {
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
					// DEL pattern is redundant
					// INS pattern is not used yet
					num_mode = 0;
					--fetched_num;
				}
			} else if (fetched_num) {
				--fetched_num;
			} else {
				switch (x) {
					case 'a':
					case 'A':
						ret[0] ++; break;
					case 'c':
					case 'C':
						ret[1] ++; break;
					case 'g':
					case 'G':
						ret[2] ++; break;
					case 't':
					case 'T':
						ret[3] ++; break;
					case '*':
					case 'N': // why pileup sequence contains N ... ?
						ret[4]++; break;
					case '^':
						prev_is_hat = 1; // discard the following mapping quality
						break;
					case '$':
						; break;
					default:
						puts(seq.c_str()); assert(0 && "unknown char in pileup");
				}
			}
		}
}

int main(int argc, char** argv) {
	assert(argc > 4);
	auto pileupFN = argv[1];
	auto bedFN = argv[2];
	auto vcfFN = argv[3];
	auto refFN = argv[4];

	//assume same chromosome !!

	vector<pair<int, int>> bed;
	map<int, VCF> vcf;
	string ref;

	readbed(bed, bedFN);
	readvcf(vcf, vcfFN);
	readref(ref, refFN);

	
	for (auto x: vcf) {
		auto pos = x.first;
		auto & vcf = x.second;
		//printf ("ref %c%c%c pos %d vcf %d %c %c %d\n",ref[pos-1],ref[pos],ref[pos+1], pos, vcf.pos, vcf.ref, vcf.alt, vcf.gt);
		assert(ref[pos]==vcf.ref);
	}

	vector<int> bufferX;
	vector<int> bufferY;

	ifstream fin(pileupFN);
	string row;
	vector<pair<int,pair<vector<int>, vector<int>>>> buffer;

	auto nowbed = bed.begin();
	while (getline(fin, row)) { // can use PIPE as input
		auto && tokens = split(row, 5);
		int pos = stoi(tokens[1]);

		while (pos >= nowbed->second) {
			++nowbed;
			if (nowbed == bed.end()) break;
		}
		if (pos < nowbed->first) continue;

		int depth = stoi(tokens[3]);
		auto & seq = tokens[4];

		vector<int> X(5,0);
		parse(seq,X);
		auto x = vcf.find(pos);

		vector<int> Y(5,0);
		if (x != vcf.end()) {
			int gt = x->second.gt;
			switch (gt) {
				case 1:
					Y[base2int(x->second.alt)] = 1;
					Y[base2int(x->second.ref)] = 1;
					break;
				case 2:
					Y[base2int(x->second.alt)] = 2;
					break;
				case 3:
					Y[base2int(x->second.alt)] = 1;
					Y[base2int(x->second.a2)] = 1;
					break;
				default:
					assert(0);
			}

		} else {
			Y[base2int(ref[pos])] = 2;
		}
		

		if (buffer.size()==0) {
			buffer.emplace_back(pos,make_pair(X,Y));
		} else {
			if (buffer.back().first != pos-1) {
				buffer.clear();
			}
			buffer.emplace_back(pos,make_pair(X,Y));
			if (buffer.size() == OUTCOUNT) {
				for (auto x : buffer) for (auto xx : x.second.first) printf("%d,", xx);
				for (auto x : buffer) for (auto xx : x.second.second) printf("%d,", xx);
				printf("%d\n", buffer[0].first);
				buffer.clear();
			}
		}
	}
}
		

