from FpsGenTool import FpsGenTool
import requests
from bs4 import BeautifulSoup
import base64

# https://oj.czos.cn/p/1416
# https://oj.czos.cn/p/1029

class CzosProblemFetcher:
    def __init__(self):
        pass

    def _gather_img(self, parent, img_list):
        for img in parent.find_all('img', recursive=True):
            img_list.append(img.get('src'))

    def fetch(self,id):
        problem_url='https://oj.czos.cn/p/%d'%id
        html=requests.get(problem_url).text
        soup=BeautifulSoup(html,features='lxml')
        # 核心区域
        pdetail=soup.find(class_='problem-detail')
        # 标题
        title=pdetail.find('div').find('b').string
        pos=title.find('-')
        if pos!=-1:
            title=title[pos+1:].strip()+'(东方博宜 - '+title[:pos]+')'
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
                    self._gather_img(content_div,img_list)
                elif key=='输入':
                    input_=str(content_div.find('div',class_='markdown'))
                    self._gather_img(content_div,img_list)
                elif key=='输出':
                    output=str(content_div.find('div',class_='markdown'))
                    self._gather_img(content_div,img_list)
                elif key=='来源':
                    # source=str(content_div.find('div',class_='markdown').find('p'))
                    pass
                elif key=='标签':
                    sources=content_div.find_all('span',recursive=True,class_='label')
                    if sources:
                        source=[]
                        for s in sources:
                            source.append(s.string)
                        source=' '.join(source)
                elif key=='说明':
                    hint=str(content_div.find('div',class_='markdown'))
                    self._gather_img(content_div,img_list)
                elif key=='样例':
                    #print(content_div)
                    sample_input=content_div.find('div',recursive=True,class_='input').find('pre').string
                    sample_output=content_div.find('div',recursive=True,class_='output').find('pre').string
                    test_input.append(sample_input)
                    test_output.append(sample_output)
                    self._gather_img(content_div,img_list)
                key=''
        # 题目参数(时间,内存,难度)
        for info_tr in soup.find(class_='problem-info').find('table').find_all('tr',recursive=True):
            tds=info_tr.find_all('td')
            info_name=tds[0].text
            info_value=tds[1].text.strip()
            if info_name=='时间限制':
                time_limit=info_value.replace('秒','').strip()
            elif info_name=='内存限制':
                memory_limit=info_value.replace('MB','').strip()
            elif info_name=='难度':
                if source:
                    source=source+' '+info_value
                else:
                    source=info_value

        # 图片内联
        for i in range(len(img_list)):
            url=img_list[i] 
            if not url.startswith('http'):
                url='https://oj.czos.cn/%s'%img_list[i]
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
    fetcher=CzosProblemFetcher()
    problem=fetcher.fetch(1029)
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
    tool.dump('czos.xml')
    print(tool)