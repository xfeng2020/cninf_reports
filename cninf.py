import requests
import json
import os
import datetime


def download_pdf(pdf_url, pdf_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.116 Safari/537.36',
    }
    res = requests.get(pdf_url, headers=headers)
    with open(pdf_path, 'wb') as file:
        file.write(res.content)


def get_reports(code, quarter=4, years=3):
    url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'

    # 判断股票上市板块
    if int(code) >= 600000:
        column = 'sse'
        plate = 'sh'
    else:
        column = 'szse'
        plate = 'sz'

    # 查询期间
    if years == -1:
        seDate = None
    else:
        today = datetime.date.today()
        end_date = today + datetime.timedelta(days=3)
        start_date = end_date + datetime.timedelta(days=-365*years)
        seDate = str(start_date) + '~' + str(end_date)

    # 需查询的定期报告类型，其中0为所有定期报告
    category_list = ['category_ndbg_szsh;'
                     'category_bndbg_szsh;'
                     'category_yjdbg_szsh;'
                     'category_sjdbg_szsh;',
                     'category_yjdbg_szsh;',
                     'category_bndbg_szsh;',
                     'category_sjdbg_szsh;',
                     'category_ndbg_szsh;']
    category = category_list[quarter]

    page = 1
    headers = {
        'Host': 'www.cninfo.com.cn',
        'Origin': 'http://www.cninfo.com.cn',
        'Referer': 'http://www.cninfo.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.116 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    hasMore = True
    while hasMore:
        data = {
            'stock': code,
            'tabName': 'fulltext',
            'pageSize': 30,
            'pageNum': page,
            'column': column,
            'category': category,
            'plate': plate,
            'seDate': seDate,
            'searchkey': None,
            'secid': None,
            'sortName': None,
            'sortType': None,
            'isHLtitle': 'true',
        }
        page += 1

        res = requests.post(url, headers=headers, data=data)
        json_text = json.loads(res.text)
        hasMore = json_text['hasMore']
        announcements = json_text['announcements']

        if not announcements:
            print(code + ' 未查找到报告')
            break

        # 建立以股票代码命名的文件夹存放文件
        if not os.path.exists('data/' + code):
            os.makedirs('data/' + code)

        for each in announcements:
            secName = each['secName']
            announcementTitle = each['announcementTitle']
            adjunctUrl = each['adjunctUrl']

            # 部分早期摘要巨潮无pdf版，跳过这部分
            if 'PDF' not in adjunctUrl:
                continue

            # pdf命名，* 在文件名中为非法字符，以 SST 替代 *ST
            secName = secName.replace('*', 'S')
            pdf_path = ('data/' + code + '/'
                        + code + '_' + secName + '_' + announcementTitle
                        + '.pdf')
            pdf_url = 'http://static.cninfo.com.cn/' + adjunctUrl

            if not os.path.exists(pdf_path):
                print('正在下载：' + pdf_path)
                download_pdf(pdf_url, pdf_path)


def main():
    print('-----程序开始运行-----')
    quarter = 1
    years = 2
    stock_code = input('输入股票代码(多个以“,"分隔)：')
    code_list = stock_code.replace(' ', '').split(',')
    for each in code_list:
        get_reports(each, quarter=quarter, years=years)
    print('-----全部下载完成-----')


if __name__ == '__main__':
    main()
