#!/usr/bin/python
# encoding: UTF-8 
 
# This Python script enables programmatic abilty to create an Remedy Incident with an attachment.
# This script can be called from the command line of a linux system or Windows with Active State Python
# installed. This script will return an BMC Remedy Incident number if successful.

# If an attachment for the ticket is desired then the --attachment arg must be present along 
# with the path to the file to attach on the filesystem of the server that this script is executed on.

# If an BMC REMEDY attachment is desired in the Remedty ticket - this script will call a function to append attachment elements to the 
# SOAP envelope if the --attachment arg is used 



import sys
import os.path
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import base64
from mako.pyparser import arg_id


def add_attachment(filename, path_to_file):
 
    if os.path.isfile(path_to_file):
        Attachment_Filename = filename
        attachmentFile = open(path_to_file, 'r')
        contents = attachmentFile.read()

        base64_Attachment = base64.b64encode(contents)
        base64_Attachment_Len = str(len(base64_Attachment))

        attachmentFile.close()
    else:
        print ("\nError: The file specified after argument --path_to_file ",path_to_file," does not exist or can not be found\n")
        print ("\nEXIT\n")
        sys.exit()

    envelope_middle = u"""<ns0:WorkInfoAttachment1Name>""" + Attachment_Filename + """</ns0:WorkInfoAttachment1Name>
    <ns0:WorkInfoAttachment1Data>""" + base64_Attachment + """</ns0:WorkInfoAttachment1Data>
    <ns0:WorkInfoAttachment1OrigSize>""" + base64_Attachment_Len + """</ns0:WorkInfoAttachment1OrigSize>"""


    return envelope_middle 

def define_first_part_of_envelope(first_name, last_name, assigned_group, assigned_support_company, assigned_support_organization,
                                            impact, reported_source, service_type, status, summary, urgency, login_id, password):

    # Variables meaningful to BMC Remedy to pass into the Envelope Body for the Remedy Incident Request...

        # If the variables are not modified here - then the defaults presented below are used.

        # The list of variables here are required and critical to be letter for letter correct or Remedy will reject the request for a new Incident Ticket


    Assigned_Group = assigned_group
    Assigned_Support_Company = assigned_support_company
    Assigned_Support_Organization = assigned_support_organization

    First_Name = first_name
    Last_Name = last_name
    
    if impact.isdigit():
        impact_actual = str(int(impact)*1000)
        Impact = impact_actual
    else:
        print ("\nERROR: --impact must be followed by a number from 1 to 4. not characters...\n")
        print ("EXIT\n")
        sys.exit()

   
    Reported_Source = reported_source
    Service_Type = service_type
    Status = status
    Summary = summary
    
    if urgency.isdigit():
        urgency_actual = str(int(urgency)*1000)
        Urgency = urgency_actual
    else:
        print ("\nERROR --urgency must be followed by a number from 1 to 4. not characters...\n")
        print ("EXIT\n")
        sys.exit()

    Login_ID = login_id
    Password = password



    envelope_first = u"""<?xml version="1.0" encoding="utf-8"?>
    <SOAP-ENV:Envelope
    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:s0="urn:HPD_IncidentInterface_Create_WS"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xmlns:ns0="urn:HPD_IncidentInterface_Create_WS" 
    xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Header>
      <s0:AuthenticationInfo>
          <s0:userName>""" + Login_ID + """</s0:userName>
            <s0:password>""" + Password + """</s0:password>
         </s0:AuthenticationInfo>
    </SOAP-ENV:Header>
      <ns1:Body>
        <ns0:HelpDesk_Submit_Service>
        <ns0:Assigned_Group>""" + Assigned_Group + """</ns0:Assigned_Group>
        <ns0:Assigned_Support_Company>""" + Assigned_Support_Company + """</ns0:Assigned_Support_Company>
        <ns0:Assigned_Support_Organization>""" + Assigned_Support_Organization + """</ns0:Assigned_Support_Organization>
        <ns0:First_Name>""" + First_Name + """</ns0:First_Name>
        <ns0:Impact>""" + Impact + """</ns0:Impact>
        <ns0:Last_Name>""" + Last_Name + """</ns0:Last_Name>
        <ns0:Reported_Source>""" + Reported_Source + """</ns0:Reported_Source>
        <ns0:Service_Type>""" + Service_Type + """</ns0:Service_Type> 
        <ns0:Status>""" + Status + """</ns0:Status>
        <ns0:Action>CREATE</ns0:Action>
        <ns0:Summary>""" + Summary + """</ns0:Summary>
        <ns0:Urgency>""" + Urgency + """</ns0:Urgency>
        <ns0:Login_ID>""" + Login_ID + """</ns0:Login_ID>"""
    return envelope_first 


def define_last_part_of_envelope():

    envelope_last = u"""</ns0:HelpDesk_Submit_Service>
    </ns1:Body>
    </SOAP-ENV:Envelope>"""
    return envelope_last



def send_soap_call_to_remedy(request):

    encoded_request = request.encode('UTF-8')
    headers = { "POST" : "/item HTTP/1.1",
    "Host": "yourbmcarserver.yourcompany.com:8080",
    "Content-Type": "text/xml; charset=utf-8",
    "Content-Length": str(len(encoded_request)),
    "SoapAction" : "CREATE" }


    print ("headers = \n")
    print (headers)
    print ("\n\n")

    print ("Length of encoded request = ",str(len(encoded_request)))

    response = requests.post(url="http://yourbmcarserver.yourcompany.com:8080/arsys/services/ARService?server=youraradminserver.yourcompany.com&webService=HPD_IncidentInterface_Create_WS",
                                 headers = headers,
                                 data = encoded_request,
                                 verify=False)

    return response

def main():

    presented_args = sys.argv
    #print (presented_args)
    
    #first_arg = ['initialized']
    if len(sys.argv) == 2:
        first_arg = str(presented_args[1])
        if (first_arg == "--help") or (first_arg == "-h") or (first_arg == "-help") or (first_arg == "help") or (first_arg == "HELP"):
            print (" ")
            print (first_arg)
            print (" ")
            print (str(presented_args[0]))
            print("\n--first_name Joe\n--last_name Smith\n--assigned_group \"Enterprise Infrastructure\"\n--assigned_support_company YOURCOMPANY\n--assigned_support_organization \"Corporate Information Systems\"\n--impact use a number 1 to 4 for 1 Extensive, 2 Large, 3 Moderate, 4 Minor\n--reported_source OTHER\n--service_type \"Infrastructure Event\"\n--status 2\n--summary \"This is the problem to be solved\"\n--urgency use 1 to 4: 1-Critical, 2-High, 3-Medium, 4-Low\n--login_id RemedyUser\n--password RemedyUserPassword")
            print (" ")
            return

    # List of supported args
    required_args = [ '--first_name','--last_name','--assigned_group','--assigned_support_company','--assigned_support_organization','--impact','--reported_source','--service_type','--status','--summary','--urgency','--login_id','--password']

    if len(sys.argv) >=2 :
        required_presented_args_clean = list(set(presented_args) & (set(required_args)))

        missing_required_args = list(set(required_args) - set(required_presented_args_clean)) 

        if missing_required_args:
            print ("\nError - you need to add these missing arguments to the command line:\n")
            for command_arg in missing_required_args:
                print (command_arg)
                return
                        
        presented_args.pop(0)
        attachment_present = 0
        command_line_len = len(presented_args)
        if command_line_len != 26:
            if command_line_len < 26:
                print ("\nError the command line you entered is missing " + str(26-command_line_len) + " value(s).\n")
                return
            else:
                # Here we check if --attachment is present...\
                set_intersect_attachment = ''.join(list(set(presented_args) & set(['--attachment'])))
                if str(set_intersect_attachment) == "--attachment":
                    print ("--attachment present")
                    attachment_present = 1
                    
                else:
                    print ("\nError the command line you entered has " + str(command_line_len-26)  + " extra value(s) entered.\n")
                    print ("Please remove the extra values or options...\n")
                    return
  

    if attachment_present == 1:
        print ("attachment present")
        required_args_with_attachment = [ '--first_name','--last_name','--assigned_group','--assigned_support_company','--assigned_support_organization','--impact','--reported_source','--service_type','--status','--summary','--urgency','--login_id','--password', '--attachment', '--filename', '--path_to_file']
        if len(sys.argv) >=2 :
            required_presented_args_clean = list(set(presented_args) & (set(required_args_with_attachment)))

            missing_required_args = list(set(required_args) - set(required_presented_args_clean)) 

            if missing_required_args:
                print ("\nError - you need to add these missing arguments to the command line:\n")
                for command_arg in missing_required_args:
                    print (command_arg)
                    return
            if command_line_len != 31:
                if command_line_len < 31:
                    print ("\nError the command line you entered is missing " + str(31-command_line_len) + " value(s).\n")
                    return
                else:
                    print ("\nError the command line you entered has " + str(command_line_len-31)  + " extra value(s) entered.\n")
                    print ("Please remove the extra values or options...\n")
                    return
                
    
    #Now parse thru the args presented:
    
    if '--attachment' in presented_args:
        presented_args.remove('--attachment')
    
    # Make two lists
    attribute = []
    value = []
    evenodd = 0;
    for arg in presented_args:
        if evenodd == 1:
            value.append(arg)
            evenodd = 0
        else:
            attribute.append(arg)
            evenodd = 1
      
    for cmd, arg in zip(attribute, value):
       
        cmd = str(cmd)
        # Assign the args
    
        if cmd == "--first_name":
            first_name = arg
        elif cmd == "--last_name":
            last_name = arg
        elif cmd == "--assigned_group":
            assigned_group = arg
        elif cmd == "--assigned_support_company":
            assigned_support_company = arg
        elif cmd == "--assigned_support_organization":
            assigned_support_organization = arg
        elif cmd == "--impact":
            impact = arg
        elif cmd == "--reported_source":
            reported_source  = arg
        elif cmd == "--service_type":
            service_type  = arg
        elif cmd == "--status":
            status  = arg
        elif cmd == "--summary":
            summary = arg   
        elif cmd == "--urgency":
            urgency = arg
        elif cmd == "--login_id":
            login_id  = arg
        elif cmd == "--password":
            password = arg
        if attachment_present == 1:
            if cmd == "--filename":
                filename = arg
            elif cmd == "--path_to_file":
                path_to_file = arg
 
    #Build soap request envelope
    
    # No attachment:

    if not attachment_present:
    
        request = define_first_part_of_envelope(first_name, last_name, assigned_group, assigned_support_company, assigned_support_organization, impact, reported_source, service_type, status, summary, urgency, login_id, password) + define_last_part_of_envelope()
                
    else:
        #attachment is present
        request = define_first_part_of_envelope(first_name, last_name, assigned_group, assigned_support_company, assigned_support_organization, impact, reported_source, service_type, status, summary, urgency, login_id, password)
        request = request + add_attachment(filename, path_to_file)
        request = request + define_last_part_of_envelope()
        
      
    response = send_soap_call_to_remedy(request)
    print ("\n",response,"\n")
    print (BeautifulSoup(response.text, "xml").prettify())

# end main()


if __name__== "__main__":
    main()


