import json
import os
import time

class RetrievalTracker:

    def __init__(self, tracker_path):
        self.tracker_path = tracker_path
        if os.path.exists(tracker_path):
            self.tracker = json.load(open(tracker_path, "r"))
        else:
            self.tracker = []

    def update_tracker(self, question, s1_query_result, s2_retrieval_result, s2_agreement_result, s3_RAG_result, id=None, save=True):
        if id is None:
            id = time.strftime("%Y-%m%d-%H:%M:%S", time.localtime())

        success_round = 0
        if s1_query_result:
            success_round = 1
        elif s2_agreement_result:
            success_round = 2
        elif s3_RAG_result:
            success_round = 3
        else:
            assert False, "The PolyRAG retrieval pipeline is not completed"

        context = ""
        if success_round == 1:
            context = f"{question} {s1_query_result}"
        elif success_round == 2:
            context = ('\n').join(s2_retrieval_result)
        elif success_round == 3:
            context = ('\n').join(s3_RAG_result)
    
        _t = {
            "id": id,
            "question": question,
            "success_round": success_round,
            "context": context,
            "s1_query_result": s1_query_result,
            "s1_query_success": True if s1_query_result else False,
            "s1_stage_context": s1_query_result,
            "s2_retrieval_result": s2_retrieval_result,
            "s2_agreement_result": s2_agreement_result,
            "s2_retrieval_success": True if s2_agreement_result else False,
            "s2_stage_context": ('\n').join(s2_retrieval_result),
            "s3_RAG_result": s3_RAG_result,
            "s3_stage_context": ('\n').join(s3_RAG_result)
        }
        self.tracker.append(_t)
        if save:
            self.save_tracker()

    def save_tracker(self):
        if os.path.exists(self.tracker_path):
            os.remove(self.tracker_path)
        with open(self.tracker_path, "w") as f:
            json.dump(self.tracker, f, indent=4)
        print(f"Tracker saved to {self.tracker_path}")

    def _s1_stat(self, print=False):
        s1_query_success = sum([t["s1_query_success"] for t in self.tracker])
        s1_query_fail = len(self.tracker) - s1_query_success
        if print:
            print(f"[S1 Ontology Query Results] Success: {s1_query_success}, Fail: {s1_query_fail}")
        return s1_query_success, s1_query_fail

    def _s2_stat(self, print=False):
        s2_retrieval_success = sum([t["s2_retrieval_success"] for t in self.tracker])
        s2_retrieval_fail = len(self.tracker) - s2_retrieval_success
        if print:
            print(f"[S2 Retrieval Agreement Results] Success: {s2_retrieval_success}, Fail: {s2_retrieval_fail}")
        return s2_retrieval_success, s2_retrieval_fail
    
    def _s3_stat(self, print=False):
        s3_RAG_success = sum([t["success_round"]==3 for t in self.tracker])
        s3_RAG_fail = len(self.tracker) - s3_RAG_success
        if print:
            print(f"[PolyRAG Results] Success: {s3_RAG_success}, Fail: {s3_RAG_fail}")
        return s3_RAG_success, s3_RAG_fail

    def print_statistics(self):
        self._s1_stat(print=True)
        self._s2_stat(print=True)
        self._s3_stat(print=True)

    def get_contexts(self, question=None, id=None):
        if question:
            return [t["context"] for t in self.tracker if t["question"]==question]
        elif id:
            return [t["context"] for t in self.tracker if t["id"]==id]
        else:
            assert False, "At least one of question and id should be provided"


class RetrievalTrackerTest:

    def __init__(self, tracker_path, benchmark_path, stage_wise=False):
        self.tracker_path = tracker_path
        self.benchmark_path = benchmark_path
        self.benchmark = json.load(open(benchmark_path, "r"))
        self.ids = [bench['id'] for bench in self.benchmark]
        self.questions = [bench['question'] for bench in self.benchmark]
        self.stage_wise = stage_wise
        if self.stage_wise:
            self.s2_retrieval_ids = self.ids
            self.s2_retrieval_questions = self.questions
            self.s3_RAG_ids = self.ids
            self.s3_RAG_questions = self.questions

        self.tracker = []
        for i in range(len(self.ids)):
            self.tracker.append({"id": self.ids[i], 
                                 "question": self.questions[i],
                                 "success_round": 0,
                                 "context": "",
                                 "s1_query_result": None,
                                 "s1_query_success": False,
                                 "s1_stage_context": "",
                                 "s2_retrieval_result": None,
                                 "s2_agreement_result": None,
                                 "s2_retrieval_success": False,
                                 "s2_stage_context": "",
                                 "s3_RAG_result": None,
                                 "s3_stage_context": ""})
            
    def save_tracker(self):
        if os.path.exists(self.tracker_path):
            os.remove(self.tracker_path)
        with open(self.tracker_path, "w") as f:
            json.dump(self.tracker, f, indent=4)
        print(f"Tracker saved to {self.tracker_path.split('/')[-1]}")

    def load_tracker(self, tracker_path):
        self.tracker_path = tracker_path
        self.tracker = json.load(open(tracker_path, "r"))

    def get_questions_by_ids(self, ids):
        ids_index = [self.ids.index(i) for i in ids]
        return [self.questions[i] for i in ids_index]
            
    def update_s1_query_result(self, query_results: list):
        if len(query_results) != len(self.tracker):
            raise ValueError("Length of query results does not match the length of tracker")
        for i in range(len(self.tracker)):
            self.tracker[i]["s1_query_result"] = query_results[i]
            self.tracker[i]["s1_query_success"] = True if query_results[i] else False
            if self.tracker[i]["s1_query_success"]:
                self.tracker[i]["context"] = f"{self.tracker[i]['question']} {query_results[i]}"
                self.tracker[i]["success_round"] = 1
        return self.tracker

    def print_s1_query_statistics(self):
        s1_query_success = sum([t["s1_query_success"] for t in self.tracker])
        s1_query_fail = len(self.tracker) - s1_query_success
        print(f"[S1 Ontology Query Results] Success: {s1_query_success}, Fail: {s1_query_fail}")
    
    def get_s2_retrieval_questions(self):
        self.s2_retrieval_ids = [t["id"] for t in self.tracker if not t["s1_query_success"]]
        self.s2_retrieval_questions = self.get_questions_by_ids(self.s2_retrieval_ids)
        return self.s2_retrieval_questions
    
    def update_s2_retrieval_result(self, retrieval_results: list):
        if len(retrieval_results) != len(self.s2_retrieval_ids):
            raise ValueError("Length of retrieval results does not match the length of tracker")
        id_alignment = [self.ids.index(i) for i in self.s2_retrieval_ids]
        for i in range(len(self.s2_retrieval_ids)):
            self.tracker[id_alignment[i]]["s2_retrieval_result"] = retrieval_results[i]
        
    def check_s2_agreement(self, retrieval_result: str):
        # check if the input string contains 'Yes'
        return "Yes" in retrieval_result
    
    def update_s2_agreement_result(self, agreement_results: list):
        id_alignment = [self.ids.index(i) for i in self.s2_retrieval_ids]
        for i in range(len(agreement_results)):
            self.tracker[id_alignment[i]]["s2_agreement_result"] = agreement_results[i]
            self.tracker[id_alignment[i]]["context"] = ('\n').join(self.tracker[id_alignment[i]]["s2_retrieval_result"])
            if self.check_s2_agreement(agreement_results[i]):
                self.tracker[id_alignment[i]]["s2_retrieval_success"] = True
                self.tracker[id_alignment[i]]["success_round"] = 2
            else:
                self.tracker[id_alignment[i]]["s2_retrieval_success"] = False

    def print_s2_retrieval_statistics(self):
        s2_retrieval_success = sum([t["s2_retrieval_success"] for t in self.tracker if not t["s1_query_success"]])
        s2_retrieval_fail = len(self.s2_retrieval_ids) - s2_retrieval_success
        print(f"[S2 Retrieval Agreement Results] Success: {s2_retrieval_success}, Fail: {s2_retrieval_fail}")

    def stage_wise_print_s2_retrieval_statistics(self):
        s2_retrieval_success = sum([t["s2_retrieval_success"] for t in self.tracker])
        s2_retrieval_fail = len(self.tracker) - s2_retrieval_success
        print(f"[S2 Retrieval Agreement Results] Success: {s2_retrieval_success}, Fail: {s2_retrieval_fail}")

    def get_s3_RAG_questions(self):
        self.s3_RAG_ids = [t["id"] for t in self.tracker if (not t["s2_retrieval_success"] and not t["s1_query_success"])]
        self.s3_RAG_questions = self.get_questions_by_ids(self.s3_RAG_ids)
        return self.s3_RAG_questions
    
    def update_s3_RAG_result(self, RAG_results: list):
        if len(RAG_results) != len(self.s3_RAG_ids):
            raise ValueError("Length of RAG results does not match the length of tracker")
        id_alignment = [self.ids.index(i) for i in self.s3_RAG_ids]
        for i in range(len(self.s3_RAG_ids)):
            self.tracker[id_alignment[i]]["s3_RAG_result"] = RAG_results[i]
            self.tracker[id_alignment[i]]["success_round"] = 3
            self.tracker[id_alignment[i]]["context"] += ('\n').join(RAG_results[i])

    def get_all_contexts(self):
        return [t["context"] for t in self.tracker]


    """
    Stage-wise: Update all the contexts in each stage, no matter if the stage is successful or not
    """

    def stage_wise_update_s1_query_result(self, query_results: list):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        if len(query_results) != len(self.tracker):
            raise ValueError("Length of query results does not match the length of tracker")
        for i in range(len(self.tracker)):
            self.tracker[i]["s1_query_result"] = query_results[i]
            self.tracker[i]["s1_query_success"] = True if query_results[i] else False
            if self.tracker[i]["s1_query_success"]:
                self.tracker[i]["s1_stage_context"] = f"{self.tracker[i]['question']} {query_results[i]}"
            else:
                self.tracker[i]["s1_stage_context"] = None
        return self.tracker
    
    def stage_wise_update_s2_retrieval_result(self, retrieval_results: list):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        self.s2_retrieval_ids = self.ids
        self.s2_retrieval_questions = self.questions
        if len(retrieval_results) != len(self.tracker):
            raise ValueError("Length of retrieval results does not match the length of tracker")
        for i in range(len(self.tracker)):
            self.tracker[i]["s2_retrieval_result"] = retrieval_results[i]
            self.tracker[i]["s2_stage_context"] = ('\n').join(retrieval_results[i])
        print(f"{len(self.s2_retrieval_ids)} retrieval results updated")
        return self.tracker
    
    def stage_wise_update_s2_agreement_result(self, agreement_results: list):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        if len(agreement_results) != len(self.tracker):
            raise ValueError("Length of agreement results does not match the length of tracker")
        for i in range(len(self.tracker)):
            self.tracker[i]["s2_agreement_result"] = agreement_results[i]
            if self.check_s2_agreement(agreement_results[i]):
                self.tracker[i]["s2_retrieval_success"] = True
            else:
                self.tracker[i]["s2_retrieval_success"] = False

    def stage_wise_update_s3_RAG_result(self, RAG_results: list):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        if len(RAG_results) != len(self.tracker):
            raise ValueError("Length of RAG results does not match the length of tracker")
        for i in range(len(self.tracker)):
            self.tracker[i]["s3_RAG_result"] = RAG_results[i]
            self.tracker[i]["s3_stage_context"] = ('\n').join(RAG_results[i])

    def save_stage_wise_s2_retrieval_contexts(self, output_path):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s2_retrieval_contexts = self.stage_wise_get_s2_contexts()
        s2_output = [{"id": i, "context": c} for i, c in zip(self.s2_retrieval_ids, s2_retrieval_contexts)]
        with open(output_path, "w") as f:
            json.dump(s2_output, f, indent=4)
        print(f"Stage-wise S2 retrieval contexts saved to {output_path.split('/')[-1]}")

    def save_stage_wise_s3_RAG_contexts(self, output_path):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s3_RAG_contexts = self.stage_wise_get_s3_contexts()
        s3_output = [{"id": i, "context": c} for i, c in zip(self.s3_RAG_ids, s3_RAG_contexts)]
        with open(output_path, "w") as f:
            json.dump(s3_output, f, indent=4)
        print(f"Stage-wise S3 RAG contexts saved to {output_path.split('/')[-1]}")

    def load_stage_wise_s2_retrieval_contexts_to_tracker(self, context_path):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s2_retrieval_contexts = json.load(open(context_path, "r"))
        for i in range(len(self.tracker)):
            self.tracker[i]["s2_stage_context"] = s2_retrieval_contexts[i]["context"]
        print(f"Stage-wise S2 retrieval contexts loaded from {context_path.split('/')[-1]}")

    def load_stage_wise_s3_RAG_contexts_to_tracker(self, context_path):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s3_RAG_contexts = json.load(open(context_path, "r"))
        for i in range(len(self.tracker)):
            self.tracker[i]["s3_stage_context"] = s3_RAG_contexts[i]["context"]
        print(f"Stage-wise S3 RAG contexts loaded from {context_path.split('/')[-1]}")
        
    def stage_wise_get_s1_contexts(self):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s1 = []
        for t in self.tracker:
            if t["s1_query_success"]:
                s1.append(t["s1_stage_context"])
            else:
                s1.append(None)
        return s1
    
    def stage_wise_get_s2_contexts(self):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s2 = []
        for t in self.tracker:
            s2.append(t["s2_stage_context"])
        return s2
    
    def stage_wise_get_s3_contexts(self):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s3 = []
        for t in self.tracker:
            s3.append(t["s3_stage_context"])
        return s3
    
    def stage_wise_get_s1s2_contexts(self):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s1s2 = []
        for t in self.tracker:
            if t["s1_query_success"]:
                s1s2.append(t["s1_stage_context"])
            else:
                s1s2.append(t["s2_stage_context"])
        return s1s2
    
    def stage_wise_get_s2s3_contexts(self):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s2s3 = []
        for t in self.tracker:
            temp = t["s2_stage_context"] + "\n"+ t["s3_stage_context"]
            s2s3.append(temp)
        return s2s3
    
    def stage_wise_get_s1s3_contexts(self):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s1s3 = []
        for t in self.tracker:
            if t["s1_query_success"]:
                s1s3.append(t["s1_stage_context"])
            else:
                s1s3.append(t["s3_stage_context"])
        return s1s3
    
    def stage_wise_get_s1s2s3_contexts(self):
        assert self.stage_wise == True, "Stage-wise update is not enabled"
        s1s2s3 = []
        for t in self.tracker:
            if t["s1_query_success"]:
                s1s2s3.append(t["s1_stage_context"])
            elif t["s2_retrieval_success"]:
                s1s2s3.append(t["s2_stage_context"])
            else:
                s1s2s3.append(t["s2_stage_context"] + "\n" + t["s3_stage_context"])
        return s1s2s3