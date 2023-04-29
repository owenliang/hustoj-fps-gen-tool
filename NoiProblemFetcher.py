from FpsGenTool import FpsGenTool
import requests
from bs4 import BeautifulSoup
import base64

# http://noi.openjudge.cn/ch0108/25/

class NoiProblemFetcher:
    def __init__(self):
        pass

    def _gather_img(self, parent, img_list):
        for img in parent.find_all('img', recursive=True):
            if 'src' not in img.attrs:
                continue
            img_list.append(img.get('src'))

    def fetch(self,id):
        problem_url='http://noi.openjudge.cn/%s'%id
        html=requests.get(problem_url).text
        soup=BeautifulSoup(html,features='lxml')
        # 单元名
        contest_title=soup.find(class_='contest-title-tab').find_all('h2')[-1].string
        # 标题
        title=soup.find(id='pageTitle').find('h2').string
        pos=title.find(':')
        title=title[pos+1:].strip()+'(openjudge - '+contest_title+' '+title[:pos].strip()+'题)'

        time_limit=1
        memory_limit=128
        description=None
        input_=None 
        output=None
        sample_input=None
        sample_output=None
        test_input=[]
        test_output=[]
        hint=None # 提示
        source=None # 来源
        img_list=[]#涉及图片
        
        # 扫描problem-content
        key=''
        for elem in soup.find(class_='problem-content',recursive=True).children:
            if elem.name=='dt':
                key=elem.string.strip()
            elif elem.name=='dd':
                if key=='':
                    continue 
                if key=='描述':
                    description=str(elem.encode_contents().decode('utf-8'))
                    self._gather_img(elem,img_list)
                elif key=='输入':
                    input_=str(elem.encode_contents().decode('utf-8'))
                    self._gather_img(elem,img_list)
                elif key=='输出':
                    output=str(elem.encode_contents().decode('utf-8'))
                    self._gather_img(elem,img_list)
                elif key=='样例输入':
                    sample_input=elem.find('pre',recursive=True).string
                    test_input.append(sample_input)
                    self._gather_img(elem,img_list)
                elif key=='样例输出':
                    sample_output=elem.find('pre',recursive=True).string
                    test_output.append(sample_output)
                    self._gather_img(elem,img_list)
                elif key=='提示':
                    hint=str(elem.encode_contents().decode('utf-8'))
                    self._gather_img(elem,img_list)
                elif key=='来源':
                    source=str(elem.encode_contents().decode('utf-8').replace(' ','-'))
                    self._gather_img(elem,img_list)
                key=''
        # 题目参数(时间,内存,难度)
        key=''
        for elem in soup.find(class_='problem-params').children:
            if elem.name=='dt':
                key=elem.string.strip()
            elif elem.name=='dd':
                if key=='总时间限制: ':
                    time_limit=int(elem.string.replace('ms','').strip())//1000
                elif key=='内存限制: ':
                    memory_limit=int(elem.string.replace('kB','').strip())//1024
                key=''

        # 图片内联
        for i in range(len(img_list)):
            url=img_list[i] 
            if not url.startswith('http'):
                url='https://media.openjudge.cn/%s'%img_list[i]
            img_content=requests.get(url).content
            img_b64=base64.b64encode(img_content).decode('utf-8')
            img_list[i]=(img_list[i],img_b64)

        return {
            'id': id,
            'title': title,
            'time_limit':time_limit,
            'memory_limit':memory_limit,
            'description': description,
            'input_': input_,
            'output': output,
            'sample_input': sample_input,
            'sample_output': sample_output,
            'test_input': test_input,
            'test_output': test_output,
            'source': source,
            'hint': hint,
            'url': problem_url,
            'img':img_list,
        }
if __name__=='__main__':
    fetcher=NoiProblemFetcher()
    problem=fetcher.fetch('ch0402/3533')
    print(problem)
    
    hint_href="<a href='%s'>原题链接</a>"%problem['url']

    tool=FpsGenTool()
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
    tool.dump('noi.xml')
    print(tool)