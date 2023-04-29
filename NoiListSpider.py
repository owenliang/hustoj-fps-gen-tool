from FpsGenTool import FpsGenTool
import requests
from bs4 import BeautifulSoup
from NoiProblemFetcher import  NoiProblemFetcher
import json 
import time 
# problem下载器
fetcher=NoiProblemFetcher()
tool=FpsGenTool()

# 生成题单JSON
problemset=[]

# 首页，解析所有章节
index_html=requests.get('http://noi.openjudge.cn/').text

soup=BeautifulSoup(index_html,features='lxml')
practice_list=soup.find_all('li',class_='practice-info',recursive=True)
for practice in practice_list:
    a_elem=practice.find('h3').find('a')
    url='http://noi.openjudge.cn'+a_elem['href']
    ch=a_elem['href'].strip('/')
    page=requests.get(url).text
    soup=BeautifulSoup(page,features='lxml')
    for problem in soup.find(id='problemsList').find('tbody').find_all('tr'):
        prob_id=problem.find(class_='problem-id').find('a').string
        print(ch,prob_id)
        problem=fetcher.fetch('/%s/%s'%(ch,prob_id))
        hint_href="<a href='%s'>原题链接</a>"%problem['url']
        tool.add_problem(problem['title'],
                        problem['time_limit'],
                        problem['memory_limit'],
                        problem['description'],
                        input_=problem['input_'],
                        output=problem['output'],
                        sample_input=problem['sample_input'],
                        sample_output=problem['sample_output'],
                        test_input=problem['test_input'],
                        test_output=problem['test_output'],
                        hint=problem['hint']+'<br/>'+hint_href if problem['hint'] else hint_href,
                        source=problem['source'],
                        img=problem['img'])
    time.sleep(2)
tool.dump('noi.xml')