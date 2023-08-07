from firebase import get_firestore_client


firestore_client = get_firestore_client()
print(firestore_client.read_from_document(collection_name="graph", document_name="agriculture"))

def hydrate_node(id, id_map, query):
    firestore_client = get_firestore_client()
    result = {}
    
    def helper(cur_id, id_map, result_map):
        result_map[cur_id] = firestore_client.read_from_document(collection_name="graph", document_name=query)[cur_id]
        for id in id_map.keys():
            new_id_map = id_map[id]
            result_map[id]["children"].append(helper(id, new_id_map, result_map[cur_id]))
        return result_map[cur_id]
    
    return helper(id, id_map, result)

hydrate_node()

