# --------- upload_file.py ----------------
# upload binary file with pycurl by http post
import pycurl, sys, getopt, os, json, argparse, re
from io import BytesIO
from urllib.parse import urlencode


# This class store the JSON data and the text content of user's input
class PCas(object):
   def __init__(self, content, rdata):
      self.content = content
      self.jdata = json.loads(rdata)
   
   def get_content(self):
      return self.content
   
   def get_jdata(self):
      return self.jdata


# This class access the annotation in the CAS
class PCasUtil(object):
   
   @staticmethod
   def select(pcas, atypes):
      jdata = PCas.get_jdata(pcas)
      content = PCas.get_content(pcas)
      ja_types = jdata['_views']['_InitialView']
      jc_types = []
      
      for atype in atypes:
         try:
            jc_types.append(ja_types[atype])
         except KeyError:
            jc_types.append([])
            print ('The data does not contain >>', atype)
      
      return jc_types
         

# This function send the piece of text to server and then get the return data
# The input is the piece of text and the type of annotation that user wish to get
# The output is the return data of server
def query(content):
   c = pycurl.Curl()
   c.setopt(c.URL, 'http://127.0.0.1:9000/index-handle')
   post_data = {'content': content}
   postfields = urlencode(post_data)
   c.setopt(c.POSTFIELDS, postfields)
   buffer = BytesIO()
   c.setopt(c.WRITEDATA, buffer)
   c.perform()
   c.close()
   body = buffer.getvalue().decode('iso-8859-1')
   return body
   
 
# This function is in charge of manipulating all process.
# The input is retrived from user input.
# The user's input is checked as the declared option of the input (-i input text, -a anotation type)
# The user's input is the file names to be stored in the array.
# The array of the file names is checked the extension.
# The file names is uploaded.
def main():
   pcas = None
   while True:
      print ('Here is a list of possible choice:')
      print ("\t1: Enter your text and run Pipeline server.")
      print ("\t2: Enter your annotation type to show the data.")
      print ("\t3: Exit.")
      var = input('Please enter your choice: ')
      
      if (var == "1"):
         content = input('Please enter your text: ')
         print ('Runing pipeline...')
         rdata = query(content)
         pcas = PCas(content, rdata)
         print ('The data is already for querying in step 2!')
      elif (var == "2"):
         if(pcas is None):
            print ('Currently, the program does not have the retreived data. You should complete step 1.')
         else:
            atypes = input('Please enter your annotation type: ')
            atypes = re.sub("[^\w]", " ",  atypes).split()
            data = PCasUtil.select(pcas, atypes)
            while (len(data) == 0):
               print ("Sorry, the annotation does not exist. Please try again!")
               atypes = input('Please enter your annotation type: ')
               atypes = re.sub("[^\w]", " ",  atypes).split()
               data = PCasUtil.select(pcas, atypes)
            print ('{:^30}{:^15}{:^15}{:^15}'.format("VALUE", "BEGIN", "END", "TYPE"))
            for i in range(len(data)):
               values = data[i];
               if (len(values) != 0):
                  for value in values:
                     print ('{:^30}{:^15}{:^15}{:^15}'.format(content[value["begin"]:value["end"]], value["begin"], value["end"], atypes[i].upper()))
      elif (var == "3"):
         print ("you entered", var)
         sys.exit(2)
      else:
         print ('Please enter the right choice!')
 
   
main()
