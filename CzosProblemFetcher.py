from FpsGenTool import FpsGenTool
import requests
from bs4 import BeautifulSoup

# https://oj.czos.cn/p/1416

class CzosProblemFetcher:
    def __init__(self):
        pass

    def fetch(self,id):
        html=requests.get('https://oj.czos.cn/p/%d'%id).text
        soup=BeautifulSoup(html,features='lxml')
        # 核心区域
        pdetail=soup.find(class_='problem-detail')
        # 标题
        title=pdetail.find('div').find('b').string
        pos=title.find('-')
        if pos!=-1:
            title=title[pos+1:].strip()
        description=None
        input_=None 
        output=None
        sample_input=None
        sample_output=None
        test_input=[]
        test_output=[]
        hint=None # 提示
        source=None # 来源

        # 扫描content-header+content-wrapper
        key=''
        for content_div in pdetail.find(class_='problem-view').find_all('div'):
            if not content_div.has_attr('class'):
                key=''
                continue
            #print(content_div)
            if 'content-header' in content_div.get('class'): 
                key=content_div.find('span').contents[0]
            elif 'content-wrapper' in content_div.get('class'):
                if key=='题目描述':
                    description=str(content_div.find('div',class_='markdown'))
                elif key=='输入':
                    input_=str(content_div.find('div',class_='markdown'))
                elif key=='输出':
                    output=str(content_div.find('div',class_='markdown'))
                elif key=='来源':
                    # source=str(content_div.find('div',class_='markdown').find('p'))
                    pass
                elif key=='标签':
                    source=content_div.find('span',recursive=True,class_='label')
                    if source:
                        source=source.string
                elif key=='说明':
                    hint=str(content_div.find('div',class_='markdown'))
                elif key=='样例':
                    #print(content_div)
                    sample_input=content_div.find('div',recursive=True,class_='input').find('pre').string
                    sample_output=content_div.find('div',recursive=True,class_='output').find('pre').string
                    test_input.append(sample_input)
                    test_output.append(sample_output)
                key=''
        return {
            'id': id,
            'title': title,
            'description': description,
            'input_': input_,
            'output': output,
            'sample_input': sample_input,
            'sample_output': sample_output,
            'test_input': test_input,
            'test_output': test_output,
            'source': source,
            'hint': hint,
        }

if __name__=='__main__':
    fetcher=CzosProblemFetcher()
    problem=fetcher.fetch(1802)
    print(problem)

    tool=FpsGenTool()
    tool.add_problem(problem['title'],
                    '1',
                    '32',
                    problem['description'],
                    input_=problem['input_'],
                    output=problem['output'],
                    sample_input=problem['sample_input'],
                    sample_output=problem['sample_output'],
                    test_input=problem['test_input'],
                    test_output=problem['test_output'],
                    hint=problem['hint'],
                    source=problem['source'])
    tool.dump('result.xml')
    print(tool)