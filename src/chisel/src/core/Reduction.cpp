#include "Reduction.h"

#include <algorithm>
#include <spdlog/spdlog.h>
#include <cmath>
#include <map>
#include <set>
#include <iostream>
#include <iterator>

#include "clang/Basic/SourceManager.h"
#include "llvm/Support/Program.h"

#include "OptionManager.h"
#include "Profiler.h"
#include "Report.h"
#include "FileManager.h"

#include <random>
#include <string>
#include <filesystem>
#include <unordered_set>
#include <cmath>

std::string generate_random_string(size_t length) {
    static const std::string characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    std::random_device random_device;
    std::mt19937 generator(random_device());
    std::uniform_int_distribution<> distribution(0, characters.size() - 1);

    std::string random_string;
    random_string.reserve(length);

    for (size_t i = 0; i < length; ++i) {
        random_string.push_back(characters[distribution(generator)]);
    }

    return random_string + ".txt";
}

static const std::string random_file_name = generate_random_string(10);

std::vector<int> divide_by_two(int num) {
    std::vector<int> results;
    while (num > 0) {
        results.push_back(num);
        num = num / 2;
    }
    return results;
}

bool file_exists(const std::string& file_name) {
    std::ifstream file(file_name.c_str());
    if (file.is_open()) {
        file.close();
        return true;
    }
    return false;
}

int compute_recommended_size() {
    if (!file_exists(random_file_name)) {
        return 0;
    }

    std::unordered_map<int, int> size_success_counts;
    std::unordered_map<int, int> size_total_counts;

    std::ifstream file(random_file_name);
    int line_count = 0;
    if (file.is_open()) {
        std::string line;
        while (std::getline(file, line)) {
            line_count++;
            std::istringstream iss(line);
            int size;
            std::string state;
            char delimiter;

            iss >> size >> delimiter >> state;
            size_total_counts[size]++;
            if (state == "success") {
                size_success_counts[size]++;
            }
        }
        file.close();
    } else {
        std::cerr << "Unable to open file: " << random_file_name << std::endl;
        return 0;
    }

    if (line_count < 100) {
        return 0;
    }

    int total_success_count = 0;
    for (const auto& pair : size_success_counts) {
        total_success_count += pair.first * pair.second;
    }

    std::vector<std::pair<int, double>> normalized_success_counts;
    for (const auto& pair : size_success_counts) {
        int size = pair.first;
	int num = pair.second;
        double normalized_success_count = static_cast<double>(size * num) / total_success_count;
        normalized_success_counts.emplace_back(size, normalized_success_count);
    }

    std::sort(normalized_success_counts.begin(), normalized_success_counts.end());

    double accumulated_success_ratio = 0.0;
    int max_size = 0;
    for (const auto& pair : normalized_success_counts) {
        int size = pair.first;
        double success_ratio = pair.second;
        accumulated_success_ratio += success_ratio;
        if (accumulated_success_ratio >= 0.95) {
            max_size = size;
            break;
        }
    }

    return max_size;
}


void update_file(int size, const std::string& state) {
    std::ofstream file(random_file_name, std::ios::app);
    if (file.is_open()) {
        file << size << ":" << state << std::endl;
        file.close();
    } else {
        std::cerr << "Unable to open file: " << random_file_name << std::endl;
    }
}

void Reduction::Initialize(clang::ASTContext &C) {
  Transformation::Initialize(C);
}

bool Reduction::callOracle() {
  testTimes=testTimes+1;
  // printf("\n\ncurrent test times:%d\n\n",testTimes);
  Profiler::GetInstance()->beginOracle();
  int Status = llvm::sys::ExecuteAndWait(OptionManager::OracleFile,
                                         {OptionManager::OracleFile});
  Profiler::GetInstance()->endOracle();
  return (Status == 0);
}

DDElementSet Reduction::toSet(DDElementVector &Vec) {
  DDElementSet S(Vec.begin(), Vec.end());
  return S;
}

DDElementSet Reduction::setDifference(DDElementSet &A, DDElementSet &B) {
  DDElementSet Result;
  std::set_difference(A.begin(), A.end(), B.begin(), B.end(),
                      std::inserter(Result, Result.begin()));
  return Result;
}

DDElementVector Reduction::toVector(DDElementSet &Set) {
  DDElementVector Vec(Set.begin(), Set.end());
  return Vec;
}

std::vector<DDElementVector> Reduction::getCandidates(DDElementVector &Decls,
                                                      int ChunkSize) {
  if (Decls.size() == 1)
    return {Decls};
  std::vector<DDElementVector> Result;
  int Partitions = Decls.size() / ChunkSize;
  for (int Idx = 0; Idx < Partitions; Idx++) {
    DDElementVector Target;
    Target.insert(Target.end(), Decls.begin() + Idx * ChunkSize,
                  Decls.begin() + (Idx + 1) * ChunkSize);
    if (Target.size() > 0)
      Result.emplace_back(Target);
  }
  for (int Idx = 0; Idx < Partitions; Idx++) {
    DDElementVector Complement;
    Complement.insert(Complement.end(), Decls.begin(),
                      Decls.begin() + Idx * ChunkSize);
    Complement.insert(Complement.end(), Decls.begin() + (Idx + 1) * ChunkSize,
                      Decls.end());
    if (Complement.size() > 0)
      Result.emplace_back(Complement);
  }

  if (OptionManager::SkipLearning)
    return Result;
  else {
    arma::uvec ChunkOrder = TheModel.sortCandidates(Decls, Result);
    std::vector<DDElementVector> SortedResult;
    for (int I = 0; I < Result.size(); I++)
      if (ChunkOrder[I] != -1)
        SortedResult.emplace_back(Result[ChunkOrder[I]]);
    return SortedResult;
  }
}


// some helper functions

std::string indices2string(const std::vector<int>& indices) {
  bool first = true;
  std::string indicesString = "[";
  for (int i: indices) {
    if (!first) {
      indicesString += ", ";
    }
    indicesString += std::to_string(i);
    first = false;
  }
  indicesString += "]";
  return indicesString;
}

float f(float x) {
  return std::fmin(x,1);
}

bool intersect(std::vector<int>& A,std::vector<int>& B){
  int sz=A.size();
  for(int i=0;i<sz;++i){
    if(find(B.begin(),B.end(),A[i])!=B.end())
      return true;
  }
  return false;
}

std::vector<int> sort_index(std::vector<float>& p) {
  std::vector<int> idx(p.size());
  iota(idx.begin(),idx.end(),0);
  stable_sort(idx.begin(),idx.end(),[&p](int i1, int i2) {return p[i1] < p[i2];});
  return idx;
}

std::vector<int> sort_index_counter(std::vector<int>& counters) {
  std::vector<int> idx(counters.size());
  iota(idx.begin(),idx.end(),0);
  stable_sort(idx.begin(),idx.end(),[&counters](int i1, int i2) {return counters[i1] < counters[i2];});
  return idx;
}

std::vector<int> sample(std::vector<float>& p) {
  std::vector<int> res;
  std::vector<int> idx = sort_index(p);
  double tmp = 1;
  double last = 0;
  int k = 0;
  int i;
  for (i = 0 ; i < idx.size(); i++){
    if (p[idx[i]] < 0){ 
      k++;
      continue;
    }   
    if (p[idx[i]] > 1)  
      break;
    for ( int j = k ; j < i ; j ++ )
      tmp *= (1-p[idx[i]]);
    tmp *= (i - k + 1); 
    if (tmp < last)
      break;
    last = tmp;
    tmp = 1;
  }

  while(i > k) {
    i--;
    res.push_back(idx[i]);
  }

  std::stable_sort(res.begin(), res.end());
  return res;
}

int count_available_element(std::vector<int>& counters) {
    int num_available_element = 0;
    for (int counter : counters) {
        if (counter != -1) {
            num_available_element = num_available_element + 1;
        }
    }
    return num_available_element;
}

int increase_all_counters(std::vector<int>& counters) {
    for (auto it = counters.begin(); it != counters.end(); ++it) {
        if (*it != -1) {
            *it = *it + 1;
        }
    }
    return counters.size();
}

int find_min_counter(std::vector<int>& counters) {
  int current_min = 10000;
  for (int counter : counters) {
    if (counter < current_min && counter != -1) {
      current_min = counter;
    }
  }
  return current_min;
}

int compute_size_by_counter(int counter, float init_probability) {
    int size = round(-1.0 / log(1 - init_probability));
    int i = 0;
    while (i < counter) {
        size = floor(size * (1 - exp(-1)));
        i = i + 1;
    }
    size = std::max(size, 1);
    return size;
}

std::vector<int> sample_by_counter(std::vector<int>& counters, float init_probability) {
  std::vector<int> res;
  std::vector<int> idx = sort_index_counter(counters);
  int counter_min = find_min_counter(counters);
  int size_current = compute_size_by_counter(counter_min, init_probability);
  int num_available_element = count_available_element(counters);

  while (size_current >= num_available_element) {
    increase_all_counters(counters);
    counter_min = find_min_counter(counters);
    size_current = compute_size_by_counter(counter_min, init_probability);
    if (size_current == 1) {
      break;
    }
  }

  int k = 0;
  
  for (size_t i = 0; i < counters.size(); i++) {
    if (counters[idx[i]] != -1) {
      res.push_back(idx[i]);
      k++;
    }
    if (k >= size_current) {
      break;
    }
  }
  
  std::stable_sort(res.begin(), res.end());
  return res;
}

std::vector<int> pickProgram(std::vector<float>& p,bool restrictionToOne,float threshold) {
  float probability;
  int len=p.size();
  std::vector<int> res;

  int choose=-1;
  if(restrictionToOne){
    for(int i=len-1;i>=0;--i){
     if(fabs(p[i]+(1<<20))<5)
      continue;
      if(choose==-1){
        choose=i;
        continue;
      }
      if(p[i]>p[choose])
        choose=i;
     }
    res.push_back(choose);
  }
  else{
    for(int i=0;i<len;++i){
     if(fabs(p[i]+(1<<20))<5) 
      continue;
     if(f(p[i])>threshold)
      continue;
     probability = rand() % (RAND_MAX) / (float)(RAND_MAX);
     if (probability>f(p[i])){
        res.push_back(i);
     }
    }
  }
  return res;
}


bool checkStop(std::vector<float>& p,float threshold) {
  int len=p.size();
  for(int i=0;i<len;++i){
    if((fabs(p[i]+(1<<20))>5)&&(f(p[i])<threshold))
      return false;
  }
  spdlog::get("Logger")->info("Iteration needs to terminate");
  return true;
}

bool checkStopCounter(std::vector<int>& counters) {
  int len=counters.size();
  for(int i=0;i<len;++i){
    if(counters[i] != -1)
      return false;
  }
  spdlog::get("Logger")->info("Iteration needs to terminate");
  return true;
}

std::vector<int> minus(std::vector<int>& A,std::vector<int>& B){//return A-B
  int len=A.size();
  std::vector<int> ret;
  for(int i=0;i<len;++i){
    if(find(B.begin(),B.end(),A[i])==B.end())
      ret.push_back(A[i]);
  }
  return ret;
}

void Reduction::refine(bool status,std::vector<int>& index,std::vector<float>& p,float delta){
  std::vector<int> waitList;
  if(status==true){
    std::vector<std::vector<int>> cache;
    for(auto history=mp1.begin(); history!=mp1.end();){
      std::vector<int> tmp=history->first;
      if(intersect(index,tmp)){
        std::vector<int> cha=minus(tmp,index);
        int sz=cha.size();
        if(sz==1){ //can't delete
          waitList.push_back(cha[0]);
          p[cha[0]]=-(1<<20);//can't delete
        }
        else{
          cache.push_back(cha);
        }
        mp1.erase(history++);
      }
      else
        history++;
    }
    int sz=cache.size();
    for(int i=0;i<sz;++i){
      mp1[cache[i]]=false;
    }
  }
  else{
    waitList.push_back(index[0]);
  }
}

void Reduction::refine_counter(bool status,std::vector<int>& index,std::vector<int>& counters){
  std::vector<int> waitList;
  if(status==true){
    std::vector<std::vector<int>> cache;
    for(auto history=mp1.begin(); history!=mp1.end();){
      std::vector<int> tmp=history->first;
      if(intersect(index,tmp)){
        std::vector<int> cha=minus(tmp,index);
        int sz=cha.size();
        if(sz==1){ //can't delete
          waitList.push_back(cha[0]);
          counters[cha[0]] = -1;//can't delete
        }
        else{
          cache.push_back(cha);
        }
        mp1.erase(history++);
      }
      else
        history++;
    }
    int sz=cache.size();
    for(int i=0;i<sz;++i){
      mp1[cache[i]]=false;
    }
  }
  else{
    waitList.push_back(index[0]);
  }
}

double computeRatio(std::vector<int> removed, std::vector<float> prob) {
  if (removed.size() == 0) return 1;
  double res = 0;
  double tmplog = 1;
  for (int i = 0 ; i < removed.size() ; i ++ ){
    if (prob[removed[i]] > 0 and prob[removed[i]] < 1)
      tmplog *= (1-prob[removed[i]]);
  }
  res = 1 / (1 - tmplog);
  return res;
}

void printSet(std::set<int> toprint) {
  if (toprint.size()==0) {
    std::cout << "empty set" << std::endl;
    return;
  }
  copy(toprint.begin(),toprint.end(),std::ostream_iterator<int>(std::cout,","));
  std::cout << std::endl;
}

// algorithm of ProbDD
DDElementSet Reduction::doProbDD(DDElementVector &Decls) {
  spdlog::get("Logger")->info("Running ProbDD - Size: {}", Decls.size());
  mp1.clear();
  DDElementSet Removed;
  std::map< std::vector<int>, std::map< int, double > > recordDelta; 
  int len=Decls.size();
  float delta=0.1;
  float initialP=OptionManager::InitProbability;
  float threshold=0.8;
  bool restrictionToOne=false;
  
  std::vector<float> p(len,initialP);
  std::vector<int> index;
  DDElementVector program;
  int configSize = len;

  while (true) {
    spdlog::get("Logger")->info("Config size: {}", configSize);
    // select a subsequence for testing
    index=sample(p);
    program.clear();
    spdlog::get("Logger")->info("Selected deletion size: {}", index.size());

    // print out indices to be deleted
    std::string indicesToBeRemoved = indices2string(index);
    spdlog::get("Logger")->info("Try deleting: {}", indicesToBeRemoved);

    for (int i: index) {
      program.push_back(Decls[i]);
    }

    bool status;
    if(mp1.find(index)!=mp1.end()){
        status=mp1[index];
    }
    else{
      if(isInvalidChunk(program)){
          status=false;
      }
      else{
          status = test(program);
      }
    }

    if (status) { // safely delete and update the model
      spdlog::get("Logger")->info("Deleted: {}", indicesToBeRemoved);
      FileManager::GetInstance()->saveTempSuccess();
      configSize -= index.size();
      auto TargetSet = toSet(program);
      Removed.insert(TargetSet.begin(), TargetSet.end());
      for(int i: index) {
          p[i]= -(1<<20);
      }
      refine(status,index,p,delta);
    }
    else { //can't delete and update the model
      double incRatio = computeRatio(index, p);
      std::map< int, double > incdelta;
      for (int i : index) {
        double delta = (incRatio - 1) * p[i];
        incdelta[i] = delta;
        p[i] += delta;
      }

      if(index.size()==1){
        p[index[0]]=-(1<<20);
      } 
      if(!OptionManager::NoCache) {
        mp1[index]=status;
      }
    }

    if (checkStop(p,threshold))
      break;
  }
  return Removed;
}

// algorithm of CDD
DDElementSet Reduction::doCDD(DDElementVector &Decls) {
  spdlog::get("Logger")->info("Running CDD - Size: {}", Decls.size());
  mp1.clear();
  DDElementSet Removed;
  std::map< std::vector<int>, std::map< int, double > > recordDelta; 
  int len=Decls.size();
  float delta=0.1;
  float initialP=OptionManager::InitProbability;
  
  std::vector<int> counters(len, 0);

  std::vector<int> index;
  DDElementVector program;
  int configSize = len;

  while (true) {
    spdlog::get("Logger")->info("Config size: {}", configSize);
    // select a subsequence for testing
    index=sample_by_counter(counters, initialP);
    program.clear();
    spdlog::get("Logger")->info("Selected deletion size: {}", index.size());

    // print out indices to be deleted
    std::string indicesToBeRemoved = indices2string(index);
    spdlog::get("Logger")->info("Try deleting: {}", indicesToBeRemoved);

    for (int i: index) {
      program.push_back(Decls[i]);
    }

    bool status;
    if(mp1.find(index)!=mp1.end()){
        status=mp1[index];
    }
    else{
      if(isInvalidChunk(program)){
          status=false;
      }
      else{
          status = test(program);
      }
    }

    if (status) { // safely delete and update the model
      spdlog::get("Logger")->info("Deleted: {}", indicesToBeRemoved);
      FileManager::GetInstance()->saveTempSuccess();
      configSize -= index.size();
      auto TargetSet = toSet(program);
      Removed.insert(TargetSet.begin(), TargetSet.end());
      for(int i: index) {
          counters[i]= -1;
      }
      refine_counter(status,index,counters);
    }
    else { //can't delete and update the model
      for (int i : index) {
        counters[i] += 1;
      }

      if(index.size()==1){
        counters[index[0]] = -1;
      }
      if(!OptionManager::NoCache) {
        mp1[index]=status;
      }
    }

    if (checkStopCounter(counters))
      break;
  }
  return Removed;
}

// algorithm of ChiselDD
DDElementSet Reduction::doChiselDD(DDElementVector &Decls) {
  DDElementSet Removed;
  DDElementVector DeclsCopy = Decls;

  TheModel.initialize(Decls);

  int ChunkSize = (DeclsCopy.size() + 1) / 2;
  int Iteration = 0;
  spdlog::get("Logger")->info("Running ChiselDD - Size: {}",
                              DeclsCopy.size());

  while (DeclsCopy.size() > 0) {
    bool Success = false;
    TheModel.train(Iteration);
    auto Targets = getCandidates(DeclsCopy, ChunkSize);
    for (auto Target : Targets) {
      Iteration++;
      if (isInvalidChunk(Target))
        continue;

      spdlog::get("Logger")->info("Config size: {}", DeclsCopy.size());
      spdlog::get("Logger")->info("Selected deletion size: {}", Target.size());
      bool Status = test(Target);
      TheModel.addForTraining(Decls, Target, Status);
      if (Status) {
        auto TargetSet = toSet(Target);
        Removed.insert(TargetSet.begin(), TargetSet.end());
        for (auto T : Target)
          DeclsCopy.erase(std::remove(DeclsCopy.begin(), DeclsCopy.end(), T),
                          DeclsCopy.end());
        Success = true;
        break;
      }
    }
    if (Success) {
      ChunkSize = (DeclsCopy.size() + 1) / 2;
    } else {
      if (ChunkSize == 1)
        break;
      ChunkSize = (ChunkSize + 1) / 2;
    }
  }
  return Removed;
}


// algorithm of FastDD
DDElementSet Reduction::doFastDD(DDElementVector &Decls) {
  DDElementSet removed;
  DDElementVector declsCopy = Decls;
  DDElementVector toBeRemoved;

  spdlog::get("Logger")->info("Running FastDD - Size: {}",
                              declsCopy.size());
  int recommended_size = compute_recommended_size();
  std::vector<int> chunkSizeSet;
  if (recommended_size == 0) {
      chunkSizeSet = divide_by_two(declsCopy.size() / 2);
  }
  else {
      chunkSizeSet = divide_by_two(recommended_size);
  }
  for (int chunkSize: chunkSizeSet) {
    if (chunkSize > declsCopy.size()) {
      continue;
    }
    int idx = 0;
    while (idx < declsCopy.size()) {
      toBeRemoved.clear();
      spdlog::get("Logger")->info("Config size: {}", declsCopy.size());
      spdlog::get("Logger")->info("Selected deletion size: {}", chunkSize);
      std::vector<int> indices;

      int current_size = declsCopy.size();
      int end_idx = std::min(idx + chunkSize, current_size);
      for (int i = idx; i < end_idx; i++) {
        toBeRemoved.push_back(declsCopy[i]);
        indices.push_back(i);
      }
      std::string indicesToBeRemoved = indices2string(indices);
      spdlog::get("Logger")->info("Try deleting: {}", indicesToBeRemoved);

      bool status;
      if(isInvalidChunk(toBeRemoved)){
        status = false;
	update_file(toBeRemoved.size(), "fail");
      }
      status = test(toBeRemoved);
      if (status) {
        auto toBeRemovedSet = toSet(toBeRemoved);
        removed.insert(toBeRemovedSet.begin(), toBeRemovedSet.end());
        declsCopy.erase(declsCopy.begin()+idx, declsCopy.begin()+end_idx);
        spdlog::get("Logger")->info("Deleted: {}", indicesToBeRemoved);
        FileManager::GetInstance()->saveTempSuccess();
	update_file(toBeRemoved.size(), "success");
      }
      else {
        idx += chunkSize;
	update_file(toBeRemoved.size(), "fail");
      }
    }
  }

  return removed;
}

// algorithm of SimplifiedProbDD
DDElementSet Reduction::doSimplifiedProbDD(DDElementVector &Decls) {
  DDElementSet removed;
  DDElementVector declsCopy = Decls;
  DDElementVector toBeRemoved;

  spdlog::get("Logger")->info("Running SimplifiedProbDD - Size: {}", declsCopy.size());
  std::vector<int> chunkSizeSet {5, 3, 1};
  for (int chunkSize: chunkSizeSet) {
    if (chunkSize > declsCopy.size()) {
      continue;
    }
    int idx = 0;
    while (idx < declsCopy.size()) {
      toBeRemoved.clear();
      spdlog::get("Logger")->info("Config size: {}", declsCopy.size());
      spdlog::get("Logger")->info("Selected deletion size: {}", chunkSize);
      std::vector<int> indices;

      int current_size = declsCopy.size();
      int end_idx = std::min(idx + chunkSize, current_size);
      for (int i = idx; i < end_idx; i++) {
        toBeRemoved.push_back(declsCopy[i]);
        indices.push_back(i);
      }
      std::string indicesToBeRemoved = indices2string(indices);
      spdlog::get("Logger")->info("Try deleting: {}", indicesToBeRemoved);

      bool status;
      if(isInvalidChunk(toBeRemoved)){
        status = false;
      }
      status = test(toBeRemoved);
      if (status) {
        auto toBeRemovedSet = toSet(toBeRemoved);
        removed.insert(toBeRemovedSet.begin(), toBeRemovedSet.end());
        declsCopy.erase(declsCopy.begin()+idx, declsCopy.begin()+end_idx);
        spdlog::get("Logger")->info("Deleted: {}", indicesToBeRemoved);
        FileManager::GetInstance()->saveTempSuccess();
      }
      else {
        idx += chunkSize;
      }
    }
  }

  return removed;
}

// algorithm of ddmin
std::string partition2IndicesString(const DDElementVector& partition, const DDElementVector& declsCopy) {
  std::vector<int> indices;
  for (const auto& elem : partition) {
    auto it = std::find(declsCopy.begin(), declsCopy.end(), elem);
    if (it != declsCopy.end()) {
      indices.push_back(std::distance(declsCopy.begin(), it));
    }
  }
  std::sort(indices.begin(), indices.end());
  std::stringstream ss;
  ss << "[";
  for (size_t i = 0; i < indices.size(); i++) {
    if (i > 0) {
      ss << ",";
    }
    ss << indices[i];
  }
  ss << "]";
  return ss.str();
}

std::vector<int> getComplement(const std::vector<int> &indices, const std::vector<int> &indexPartition) {
  std::vector<int> indexComplement;
  std::set_difference(indices.begin(), indices.end(), indexPartition.begin(), indexPartition.end(), std::back_inserter(indexComplement));
  return indexComplement;
}

std::vector<std::vector<int>> getPartitions(const std::vector<int> &indices, int n) {
  std::vector<std::vector<int>> indexPartitions;
  int partitionSize = std::ceil(static_cast<float>(indices.size()) / n);

  for (int i = 0; i < indices.size(); i += partitionSize) {
    std::vector<int> partition(indices.begin() + i, std::min(indices.begin() + i + partitionSize, indices.end()));
    indexPartitions.push_back(partition);
  }

  return indexPartitions;
}

DDElementVector getElementsByIndices(const DDElementVector &Decls, const std::vector<int> &indices) {
  DDElementVector elements;
  for (const auto &index : indices) {
    elements.push_back(Decls[index]);
  }
  return elements;
}

std::string intVectorToString(const std::vector<int>& vec) {
  std::stringstream ss;
  for (size_t i = 0; i < vec.size(); ++i) {
    if (i > 0) {
      ss << ",";
    }
    ss << vec[i];
  }
  return ss.str();
}

DDElementSet Reduction::doDdmin(DDElementVector &Decls) {
  DDElementSet removed;
  DDElementVector declsCopy = Decls;
  DDElementVector toBeRemoved;
  spdlog::get("Logger")->info("Running ddmin - Size: {}", declsCopy.size());

  if (declsCopy.size() == 1) {
    spdlog::get("Logger")->info("Config size: {}", declsCopy.size());
    spdlog::get("Logger")->info("Selected partition size: {}", declsCopy.size());
    DDElementVector toBeRemoved = declsCopy;
    if (test(toBeRemoved)) {
      auto toBeRemovedSet = toSet(toBeRemoved);
      removed.insert(toBeRemovedSet.begin(), toBeRemovedSet.end());
      spdlog::get("Logger")->info("Try deleting: [0]");
      spdlog::get("Logger")->info("Deleted");
      FileManager::GetInstance()->saveTempSuccess();
      return removed;
    }
  }

  int n = 2;
  std::vector<int> indices(declsCopy.size());
  std::iota(indices.begin(), indices.end(), 0);
  std::unordered_set<std::string> onePassCache;

  while (true) {
    outerLoop:
    if (indices.size() <= 1) {
      break;
    }
    toBeRemoved.clear();
    std::vector<std::vector<int>> indexPartitions = getPartitions(indices, n);
    // start from N optimization
    if (OptionManager::StartFromN > 0) {
      // Check if the size of every partition is not greater than OptionManager::StartFromN
      bool allPartitionsWithinThreshold = true;
      for (const auto& partition : indexPartitions) {
        if (partition.size() > OptionManager::StartFromN) {
          allPartitionsWithinThreshold = false;
          break;
        }
      }
  
      if (!allPartitionsWithinThreshold) {
	int current_size = indices.size();
        n = std::min(2 * n, current_size);
        continue;
      }
    }

    // complement only optimization
    if (!OptionManager::ComplementOnly) {
      for (const auto &indexPartition : indexPartitions) {
        std::vector<int> indexComplement = getComplement(indices, indexPartition);
        toBeRemoved = getElementsByIndices(declsCopy, indexComplement);
        spdlog::get("Logger")->info("Config size: {}", indices.size());
        spdlog::get("Logger")->info("Selected partition size: {}", indexPartition.size());
        std::string indicesToBeRemoved = indices2string(indexPartition);
        spdlog::get("Logger")->info("Try deleting(complement of): {}", indicesToBeRemoved);
        bool status;
        if(isInvalidChunk(toBeRemoved)){
          status = false;
        }
        status = test(toBeRemoved);
        if (status) {
          auto toBeRemovedSet = toSet(toBeRemoved);
          removed.insert(toBeRemovedSet.begin(), toBeRemovedSet.end());
          spdlog::get("Logger")->info("Deleted(complement of): {}", indicesToBeRemoved);
          FileManager::GetInstance()->saveTempSuccess();
          indices = indexPartition;
          n = 2;
          goto outerLoop;
        }
      }
    }

    for (const auto &indexPartition : indexPartitions) {
      
      // onepass optimization
      if (OptionManager::Onepass) {
	std::string indexPartitionStr = intVectorToString(indexPartition);
        if (onePassCache.find(indexPartitionStr) != onePassCache.end()) {
          continue;
        } else {
          onePassCache.insert(indexPartitionStr);
        }
      }

      toBeRemoved = getElementsByIndices(declsCopy, indexPartition);
      spdlog::get("Logger")->info("Config size: {}", indices.size());
      spdlog::get("Logger")->info("Selected partition size: {}", indexPartition.size());
      std::vector<int> indexComplement = getComplement(indices, indexPartition);
      std::string indicesToBeRemoved = indices2string(indexPartition);
      spdlog::get("Logger")->info("Try deleting: {}", indicesToBeRemoved);

      bool status;
      if(isInvalidChunk(toBeRemoved)){
        status = false;
      }
      status = test(toBeRemoved);
      if (status) {
        auto toBeRemovedSet = toSet(toBeRemoved);
        removed.insert(toBeRemovedSet.begin(), toBeRemovedSet.end());
        spdlog::get("Logger")->info("Deleted: {}", indicesToBeRemoved);
        FileManager::GetInstance()->saveTempSuccess();
        indices = indexComplement;
        n--;
        goto outerLoop;
      }
    }

    if (n == indices.size()) {
      break;
    }
    else {
      int current_size = indices.size();
      n = std::min(2 * n, current_size);
    }
  }

  return removed;
}

DDElementSet Reduction::doDeltaDebugging(DDElementVector &Decls) {
  DDElementSet removed;
  if (OptionManager::Algorithm.compare("probdd") == 0) {
    removed = doProbDD(Decls);
  }  
  else if (OptionManager::Algorithm.compare("cdd") == 0) {
    removed = doCDD(Decls);
  }
  else if (OptionManager::Algorithm.compare("chiseldd") == 0) {
    removed = doChiselDD(Decls);
  }
  else if (OptionManager::Algorithm.compare("fastdd") == 0) {
    removed = doFastDD(Decls);
  }
  else if (OptionManager::Algorithm.compare("simplifiedprobdd") == 0) {
    removed = doSimplifiedProbDD(Decls);
  }
  else if (OptionManager::Algorithm.compare("ddmin") == 0) {
    removed = doDdmin(Decls);
  }
  else {
    spdlog::get("Logger")->info("Unknown algorithm");
    exit(1);
  }
  return removed;
}

