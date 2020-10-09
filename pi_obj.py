import time



def create_pi_obj( data ):
    """
    @description: create a pi dict object with the usefull fields.
                    used to standardize data : if a data field is absent, 
                    the dict field will be equal to None.
    @param data : data received from rasberry pi.
    @return : pi dict object.
    """
    pi_obj = {}

    try: pi_obj["location"] = data["location"]
    except: pi_obj["location"] = None

    try: pi_obj["temperature"] = data["temperature"]
    except: pi_obj["temperature"] = None

    try: pi_obj["humidity"] = data["humidity"]
    except: pi_obj["humidity"] = None

    try: pi_obj["luminance"] = data["luminance"]
    except: pi_obj["luminance"] = None

    return pi_obj



def exclude_pi_objs_none_field( pi_objs, field ):
    """
    @description: suppress a pi dict object in a list if a specific field is None.
    @param pi_objs: list of pi dict object.
    @param field: field of interest.
    @return: new pi dict object.
    """
    valid_objs = []
    for pi_obj in pi_objs:
        if pi_obj[field] != None:
            valid_objs.append( pi_obj )
    return valid_objs 


def group_pi_objs_by_field( pi_objs, field ):
    """
    @description: group a list of pi object depending on a field value.
    @param pi_objs : list of pi dict object.
    @param field : field of interest.
    @return : new list of dict {
                <field>: value, (unique)
                "objects": list pi dict object corresponding to field value}
    """            
    valid_objs = exclude_pi_objs_none_field( pi_objs, field )
    groups = []
    for valid_obj in valid_objs:
        field_added = False
        for group in groups:
            if group[field] == valid_obj[field]:
                group["data"].append( valid_obj )
                field_added = True
                break
        if not field_added:
            groups.append( { 
                field: valid_obj[field],
                "data": [valid_obj] } )
    return groups



def mean_pi_objs_by_field( pi_objs, field ):
    """
    @description: compute the mean of pi object according to a field
    @param pi_objs : list of pi dict object.
    @param field : field of interest.
    @return : new list of dict {
                <field>: value, (unique)
                "updateTime": datetime,
                "objects": list pi dict object corresponding to field value}
    """   
    groups = group_pi_objs_by_field( pi_objs, field )
    for group in groups:
        group["updateTime"] = time.time()
        group["data"] = mean_pi_objs( group["data"] )
    return exclude_none_means(groups)



def exclude_none_means( means ):
    """
    @description: exclude inputs of a dict if all data means are None 
    @param pi_objs : list of pi dict object.
    @return : filtered dict of means
    """  
    valid_means = []
    for mean in means:
        if not mean["data"] == None:
            valid_means.append( mean )
    return valid_means



def mean_pi_objs( pi_objs ):
    """
    @description: compute mean of temperature, humidity and 
                  luminance of a dict of pi objects
    @param pi_objs : list of pi dict object.
    @return : dict of means
    """  
    temperature =  mean_values( [pi_obj["temperature"] for pi_obj in pi_objs] )
    humidity = mean_values( [pi_obj["humidity"] for pi_obj in pi_objs] )
    luminance = mean_values( [pi_obj["luminance"] for pi_obj in pi_objs] )
    if temperature == None and humidity == None and luminance == None:
        return None
    return {
        "temperature": temperature,
        "humidity": humidity,
        "luminance": luminance 
    }



def mean_values( values ):
    """
    @description: compute mean of values 
    @param pi_objs : list of values
    @return : mean of values or None 
    """  
    mean = 0
    count = 0
    for value in values:
        if not value == None:
            mean += value
            count += 1
    return None if count == 0 else mean/count  
