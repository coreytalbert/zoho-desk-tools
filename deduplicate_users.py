import json
import pprint

# one email : many (created date, id)
# if there is more than one id, merge all records using the oldest record as the source

contact_map = dict()

with open("all_contacts.json") as all_contacts:
    all_contacts_arr = json.load(all_contacts)
    
    for contact in all_contacts_arr:

        contact_email = contact.get("email")
        
        if contact_email not in contact_map:
            contact_map[contact_email] = list()

        contact_map[contact_email].append(
            (contact.get("createdTime"), contact.get("id"))
        )

duplicate_count = 0
for contact in contact_map:
    if len(contact_map[contact]) > 1:
        duplicate_count+=1

# pprint.pprint(contact_map)

# v is a list of tuples of the form (createdTime, id)
duplicated_contacts = {k:v for (k, v) in contact_map.items() if len(v) > 1}

# pprint.pprint(duplicated_contacts)

del duplicated_contacts[None]

with open("merge_contacts_api_payload.txt", 'w') as deduped_file:

    for (k, v) in duplicated_contacts.items():
    
        # Sorting by ascending createdTime here, and considering the oldest contact to be 
        # the primary record into which all other records should be merged 
        v.sort(key=lambda tup: tup[0]) 

        # https://desk.zoho.com/DeskAPIDocument#Contacts#Contacts_MergeContacts
        merge_dict = dict(
            {
                "ids":[], # The list of contact ids to merge into the source id
                "source":{
                    "firstName":"", 
                    "lastName":"", 
                    "email":"", 
                    "secondaryEmail":"", 
                    "accountId":"", 
                    "phone":"", 
                    "title":""
                }
            }
        )
    
        for tup in v:
            merge_dict["ids"].append(tup[1])
        del merge_dict["ids"][0] # This first value is the source id, it should not be in the list

        source_id = v[0][1]

        for attr in merge_dict.get("source").keys():
            merge_dict["source"][attr] = source_id

        deduped_file.write("merge_contacts_api_payloads.insert(")
        deduped_file.write(merge_dict.__str__())
        deduped_file.write(");")
        deduped_file.write('\n')
        pprint.pprint(merge_dict)


print("total records: ", len(all_contacts_arr))
print("unique emails: ", len(contact_map))
print("duplicated contacts: ", duplicate_count)
