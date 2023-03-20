from FpsGenTool import FpsGenTool
import requests
from bs4 import BeautifulSoup
from CzosProblemFetcher import  CzosProblemFetcher

# problem下载器
fetcher=CzosProblemFetcher()
tool=FpsGenTool()

# index翻页
for page in range(1,16):
    url='https://oj.czos.cn/problem/index?page=%d&per-page=100'%page
    index_html=requests.get(url).text 
    soup=BeautifulSoup(index_html,features='lxml')
    problem_table=soup.find('table',class_='problem-index-list')
    for problem_tr in problem_table.find('tbody').find_all('tr'):
        problem_id=int(problem_tr.get('data-key'))
        problem=fetcher.fetch(problem_id)
        print(problem_id)

        hint_href="<a href='%s'>原题链接</a>"%problem['url']
        tool.add_problem(problem['title'],
                        '1',
                        '128',
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
tool.dump('result.xml')
