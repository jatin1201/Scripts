import boto3
 ec2 = boto3.resource('ec2', region_name='us-east-1')
  instances = ec2.instances.filter()
  for instance in instances:
     print(instance.id, instance.instance_type)
     # Get a list of ids of all securify groups attached to the instance
     all_sg_ids = [sg['GroupId'] for sg in instance.security_groups]
     # Check the SG to be removed is in the list  
     if sg_id in all_sg_ids:    
     # Remove the SG from the list                                      
       all_sg_ids.remove(sg_id)         
     # Attach the remaining SGs to the instance                              
       instance.modify_attribute(Groups=all_sg_ids)                 
