#!/bin/python3.5
# -*- coding: utf-8 -*-


 #どんなタグ構造でも、文字が何が来ても誤変換がないプログラムにした。<<<本当???
from bs4 import BeautifulSoup
from snownlp import SnowNLP
from pypinyin import pinyin
import os
import datetime
import locale
import glob
import zipfile
import sys
import shutil

def unzippen(filename):

	name, ext = os.path.splitext(filename)
	inputFile = zipfile.ZipFile(filename,'r')

	os.mkdir('[pinyin]'+name)
	os.chdir('[pinyin]'+name)
	inputFile.extractall()
	os.chdir("../")

def get_file(dir):
	file_list = []
	os.chdir(dir)

	for f_name in glob.iglob('./**/*.xhtml', recursive=True):
		#print(f_name)
		file_list.append(f_name)
	for f_name in glob.iglob('./**/*.html', recursive=True):
	#'./'+dir+'/**/*.html', recursive=True
		#print(f_name)
		file_list.append(f_name)
	#os.chdir('../')
	return file_list




def zippen(name):
	os.chdir('../')
	with zipfile.ZipFile('[pinyin]'+name+'.epub','w') as myzip:
		os.chdir('[pinyin]'+name)
		
		print ("current dir",os.getcwd())
		
		for folder, subfolders, files in os.walk(os.getcwd()):
			myzip.write(folder)
			#print (folder)
			for file in files:
				rel_path = os.path.join(folder,file).replace(os.getcwd(),".")
				myzip.write(rel_path)
				#myzip.write(os.path.join(folder,file))
				#print (rel_path)

def hz2py(hans): #hansは文字列　返り値listはリスト形式
	hans_seg = SnowNLP(hans).words
	#print (hans_seg)
	#print (pinyin(hans_seg))

	list = []
	for word in hans_seg :
		tlist = []
		tlist.append(word)
		pin = ""
		for wordt in pinyin(word):
			pin = pin+wordt[0]
			
		tlist.append(pin)
		list.append(tlist)
		#print (word)
		#print (pin)
	return list

def open_file(file_name):
	r = open(file_name,encoding = "utf-8")
	source = r.read()
	r.close()
	
	return source

def converter(source):
	
	soup = BeautifulSoup(source,"html.parser")

	for i in soup.find_all("body"):
		p = str(i)
		#print (p)
		#print ("===============================")
	
		for j in i.strings:
			j_ruby = ""
			py = ""

			for k in hz2py(j):
				#print ("k:::::::::",k)
				new_tag_ruby = soup.new_tag("ruby") #ルビふりの範囲を規定
				new_tag_rt = soup.new_tag("rt") #ルビの文字			
				new_tag_ruby.string = (k[0])
				new_tag_rt.string = (k[1])
				
				new_tag_ruby.append(new_tag_rt)
				#print (new_tag_ruby)
				j_ruby = j_ruby + str(new_tag_ruby) 
				py = py + k[1]
			
			
		#print (j)
		#print ("pinyin:::",py)
			#print ("j_ruby",j_ruby)
			#print ("before replace",p)
			p = p.replace(">"+j+"<",">"+j_ruby+"<")
			
			for k in hz2py(j):
				
				a = str(new_tag_ruby).replace(">"+k[0]+"<",">"+str(new_tag_ruby)+"<")
				b = str(new_tag_ruby).replace(">"+k[1]+"<",">"+str(new_tag_ruby)+"<")
				
				p = p.replace(a, str(new_tag_ruby))
				p = p.replace(b, str(new_tag_ruby))
			
		#print ("p:::::",p)
			
		i.replace_with(BeautifulSoup(p,"html.parser").body)
	return soup
	
		

		
def write_file(file_name,soup):
	f = open(file_name,"w",encoding = "utf-8")
	f.write(str(soup.prettify()))
	f.close()

	

epub_list = glob.glob("*.epub")

if not os.path.exists('./converted_original'):
	os.makedirs('./converted_original')
	
	
if not os.path.exists('./with_pinyin'):
	os.makedirs('./with_pinyin')
	


	

for filename in epub_list:
	name, ext = os.path.splitext(filename)
	print (name,filename)
	unzippen(filename)	

	file_list = get_file('[pinyin]'+name)
	print (file_list)
		
	print ("prosessing started")	
	i = 0
	for li in file_list:
		write_file(li,(converter(open_file(li))))
		d = datetime.datetime.today().strftime("%Y-%m-%d %H:%M-%S")
		file_size = float(os.path.getsize(li))/1000
		print (i+1,"of",len(file_list),d," ||| written:",li,str(file_size)+"KB")
		i = i +1
		
	zippen(name)
	print ("prosessing completed")

	os.chdir("../")

	shutil.rmtree('[pinyin]'+name)
	shutil.move(filename,'./converted_original')
	shutil.move('[pinyin]'+filename,'./with_pinyin')
