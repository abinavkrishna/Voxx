import pickle

with open("responses.txt") as f:
    responses_list = [line.rstrip() for line in f]
f.close()

queries = responses_list[0::2]
responses = responses_list[1::2]

print(str(queries))
print(str(responses))
question_response_pairs = {}

for q_index in range(0,len(queries)):
    question_response_pairs[queries[q_index]] = responses[q_index]

with open("responses.pkl","wb") as f:
    pickle.dump(question_response_pairs,f)
f.close()
